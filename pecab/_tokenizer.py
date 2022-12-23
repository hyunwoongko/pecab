import ast
import os
import sys
from functools import lru_cache
from typing import List, Optional

import numpy as np
import pyarrow as pa
import unicodedata

from pecab._datrie import DoubleArrayTrie
from pecab._utils._unknown import UNK
from pecab._tokens import DictionaryToken, TokenAttributes, DecompoundToken
from pecab._user_dict import UserDictionary
from pecab._utils._char_definition import CharacterDefinition, character_category_map
from pecab._utils._char_unicode import SPACE_SEPARATOR, NON_SPACING_MARK, is_punctuation
from pecab._utils._consts import Pos, Tokenization, Type

PATH = os.path.dirname(__file__)


class Tokenizer:
    def __init__(self, user_dict: Optional[List[str]], split_compound: bool):
        self.buffer = Tokenizer.Buffer()
        self.split_compound = split_compound
        self.character_definition = CharacterDefinition()
        self.known_dict = DoubleArrayTrie.from_files(
            arrays=self.load_arrow("arrays.arrow"),
            words=self.load_arrow("words.arrow"),
        )
        self.conn_costs = np.memmap(
            os.path.join(PATH, "_resources", "matrix.npy"),
            mode="r",
            dtype="int16",
            shape=Tokenization.CONN_SHAPE,
        )
        self.unknown_dict = UNK
        self.user_dict = (
            UserDictionary(self.character_definition, user_dict)
            if user_dict is not None
            else None
        )
        self.reset_state()

    @staticmethod
    @lru_cache(maxsize=2)
    def load_arrow(filename):
        return pa.ipc.RecordBatchFileReader(
            pa.memory_map(
                os.path.join(PATH, "_resources", filename),
                mode="r",
            )
        ).read_all()

    @lru_cache(maxsize=5000)
    def create_entries(self, surface):
        data_entries = {}
        word_ref_id = self.known_dict[surface]
        if word_ref_id is None:
            return None
        else:
            for k, v in word_ref_id.items():
                for k2, v2 in enumerate(v.split("|")):
                    if k2 in data_entries:
                        data_entries[k2][k] = v2
                    else:
                        data_entries[k2] = {k: v2}
            return data_entries

    def reset_state(self):
        self.pos = 0
        self.end = False
        self.last_backtrace_pos = 0
        self.positions = Tokenizer.WrappedPositionArray()
        self.token_attributes = TokenAttributes()
        self.pending = []
        self.positions.get(0).add(0, 0, -1, -1, -1, -1, Type.KNOWN, None, None, None)

    def set_input(self, text: str):
        new_text = ""
        for ch in text:
            if character_category_map(ch) is None:
                new_text += " "
            else:
                new_text += ch

        self.buffer.set(new_text)
        self.reset_state()

    class Buffer:
        def set(self, text):
            self.text = text

        def get(self, pos):
            if 0 <= pos <= len(self.text) - 1:
                return self.text[pos]
            else:
                return -1

        def slice_get(self, start_pos, end_pos):
            return self.text[start_pos:end_pos]

    class Position:
        def __init__(self):
            self.pos = 0
            self.count = 0
            self.costs = []
            self.last_right_id = []
            self.back_pos = []
            self.back_word_pos = []
            self.back_index = []
            self.back_id = []
            self.back_dict_type = []
            self.back_pos_type = []
            self.morphemes = []
            self.back_pos_tag = []

        def add(
            self,
            cost,
            last_right_id,
            back_pos,
            back_rpos,
            back_index,
            back_id,
            back_dict_type,
            back_pos_type,
            morphemes,
            back_pos_tag,
        ):
            self.costs.append(cost)
            self.last_right_id.append(last_right_id)
            self.back_pos.append(back_pos)
            self.back_word_pos.append(back_rpos)
            self.back_index.append(back_index)
            self.back_id.append(back_id)
            self.back_dict_type.append(back_dict_type)
            self.count += 1

            self.back_pos_type.append(back_pos_type)
            self.morphemes.append(morphemes)
            self.back_pos_tag.append(back_pos_tag)

        def reset(self):
            self.count = 0

    class WrappedPositionArray:
        def __init__(self):
            self.positions = [
                Tokenizer.Position(),
                Tokenizer.Position(),
                Tokenizer.Position(),
                Tokenizer.Position(),
            ]

            self.next_write = 0
            self.next_pos = 0
            self.count = 0

        def reset(self):
            self.next_write -= 1
            while self.count > 0:
                if self.next_write == -1:
                    self.next_write = len(self.positions) - 1

                self.positions[self.next_write].reset()
                self.next_write -= 1
                self.count -= 1

            self.next_write = 0
            self.next_pos = 0
            self.count = 0

        def get(self, pos):
            while pos >= self.next_pos:
                if self.count == len(self.positions):
                    self.new_positions = []
                    for _ in range(0, 1 + self.count):
                        self.new_positions.append(Tokenizer.Position())

                    self.new_positions[
                        : len(self.positions) - self.next_write
                    ] = self.positions[
                        self.next_write : len(self.positions) - self.next_write
                    ]
                    self.new_positions[
                        len(self.positions) - self.next_write : self.next_write
                    ] = self.positions[: self.next_write]
                    self.positions = self.new_positions[:]

                if self.next_write == len(self.positions):
                    self.next_write = 0

                assert self.positions[self.next_write].count == 0

                self.positions[self.next_write].pos = self.next_pos
                self.next_write += 1
                self.next_pos += 1
                self.count += 1

            assert self.in_bounds(pos)
            index = self.get_index(pos)
            assert self.positions[index].pos == pos

            return self.positions[index]

        def get_nextpos(self):
            return self.next_pos

        def in_bounds(self, pos):
            return self.next_pos > pos >= self.next_pos - self.count

        def get_index(self, pos):
            index = self.next_write - (self.next_pos - pos)
            if index < 0:
                index += len(self.positions)
            return index

    @staticmethod
    def compute_space_penalty(left_pos, num_spaces):
        space_penalty = 0
        if num_spaces > 0:
            if left_pos in [
                "JKS",
                "JKC",
                "JKG",
                "JKO",
                "JKB",
                "JKV",
                "JKQ",
                "JX",
                "JC",
            ]:
                space_penalty = 6000
            elif left_pos == [
                "EC",
                "EF",
                "EP",
                "ETM",
                "ETN",
                "XSA",
                "XSN",
                "XSV",
                "VCP",
            ]:
                space_penalty = 3000
        return space_penalty

    def add(self, surface, data_dict, from_pos_data, word_pos, end_pos, type_):
        word_id = surface
        left_pos = data_dict["POS"]
        word_cost = int(data_dict["word_cost"])
        left_id = int(data_dict["left_id"])
        right_id = int(data_dict["right_id"])
        back_pos_type = data_dict["POS_type"]
        morphemes = ast.literal_eval(str(data_dict["morphemes"]))

        least_cost = sys.maxsize
        least_idx = -1
        assert from_pos_data.count > 0

        for idx in range(0, from_pos_data.count):
            num_spaces = word_pos - from_pos_data.pos
            cost = (
                from_pos_data.costs[idx]
                + self.conn_costs[from_pos_data.last_right_id[idx], left_id]
                + self.compute_space_penalty(left_pos, num_spaces)
            )

            if cost < least_cost:
                least_cost = cost
                least_idx = idx

        least_cost += word_cost
        self.positions.get(end_pos).add(
            cost=least_cost,
            last_right_id=right_id,
            back_pos=from_pos_data.pos,
            back_rpos=word_pos,
            back_index=least_idx,
            back_id=word_id,
            back_dict_type=type_,
            back_pos_type=back_pos_type,
            morphemes=morphemes,
            back_pos_tag=left_pos,
        )

    def increment_token(self):
        while len(self.pending) == 0:
            if self.end:
                return False
            self.parse()

        token = self.pending.pop()
        length = token.length
        assert length > 0
        self.token_attributes.terms.append(token.surface_form)
        self.token_attributes.offsets.append((token.start_offset, token.end_offset))
        self.token_attributes.pos_length.append(token.pos_len)
        self.token_attributes.pos_types.append(token.pos_type)
        self.token_attributes.pos_tags.append(token.pos_tag)
        self.token_attributes.dict_types.append(token.dict_type)
        return True

    def parse(self):
        unknown_word_end_index = -1
        user_word_max_pos_ahead = -1

        while True:
            if self.buffer.get(self.pos) == -1:
                break
            pos_data = self.positions.get(self.pos)
            is_frontier = self.positions.get_nextpos() == self.pos + 1

            if pos_data.count == 0:
                self.pos += 1
                continue

            if (
                self.pos > self.last_backtrace_pos
                and pos_data.count == 1
                and is_frontier
            ):
                self.backtrace(pos_data, 0)

                pos_data.costs[0] = 0
                if len(self.pending) > 0:
                    return

            if ord(self.buffer.get(self.pos)) in SPACE_SEPARATOR:
                self.pos += 1
                next_char = self.buffer.get(self.pos)

                while next_char != -1 and ord(next_char) in SPACE_SEPARATOR:
                    self.pos += 1
                    next_char = self.buffer.get(self.pos)

            if self.buffer.get(self.pos) == -1:
                self.pos = pos_data.pos

            any_matches = False
            if self.user_dict is not None:
                max_pos_ahead = 0
                pos_ahead = self.pos

                while True:
                    ch = self.buffer.get(pos_ahead)
                    if ch == -1:
                        break
                    surface = self.buffer.slice_get(self.pos, pos_ahead + 1)
                    user_id_ref = self.user_dict[surface]

                    if user_id_ref is not None:
                        last_result = user_id_ref
                        max_pos_ahead = pos_ahead
                        any_matches = True

                    pos_ahead += 1

                if any_matches and max_pos_ahead > user_word_max_pos_ahead:
                    self.add(
                        last_result["surface"],
                        last_result,
                        pos_data,
                        self.pos,
                        max_pos_ahead + 1,
                        Type.USER,
                    )
                    user_word_max_pos_ahead = max(
                        user_word_max_pos_ahead, max_pos_ahead
                    )

            if not any_matches:
                pos_ahead = self.pos
                while True:
                    ch = self.buffer.get(pos_ahead)
                    if ch == -1:
                        break
                    surface = self.buffer.slice_get(self.pos, pos_ahead + 1)
                    data_entries = self.create_entries(surface)

                    if data_entries is not None:
                        for data_entry in data_entries.values():
                            self.add(
                                surface,
                                data_entry,
                                pos_data,
                                self.pos,
                                pos_ahead + 1,
                                Type.KNOWN,
                            )
                            any_matches = True

                    pos_ahead += 1

            if unknown_word_end_index > pos_data.pos:
                self.pos += 1
                continue

            first_character = self.buffer.get(self.pos)
            if any_matches is False or self.character_definition.is_invoke(
                first_character
            ):
                character_id = self.character_definition.get_character_class(
                    first_character
                )
                if self.character_definition.is_group(first_character) is False:
                    unknown_word_length = 1
                else:
                    unknown_word_length = 1
                    script_code = unicodedata.category(first_character)
                    is_punct = is_punctuation(first_character)
                    pos_ahead = self.pos + 1

                    while True:
                        next_ch = self.buffer.get(pos_ahead)
                        if next_ch == -1:
                            break
                        next_hex_ch = ord(next_ch)
                        next_script_code = unicodedata.category(next_ch)

                        if unknown_word_length == Tokenization.MAX_UNKNOWN_WORD_LENGTH:
                            break

                        same_script = (script_code == next_script_code) or (
                            next_hex_ch in NON_SPACING_MARK
                        )
                        if (
                            same_script
                            and is_punct == is_punctuation(next_ch)
                            and self.character_definition.is_group(next_ch)
                        ):
                            unknown_word_length += 1
                        else:
                            break

                        pos_ahead += 1

                word_id_ref = self.unknown_dict[character_id]
                self.add(
                    character_id,
                    word_id_ref,
                    pos_data,
                    self.pos,
                    self.pos + unknown_word_length,
                    Type.UNKNOWN,
                )

            self.pos += 1
        self.end = True

        if self.pos > 0:
            end_pos_data = self.positions.get(self.pos)
            least_cost = sys.maxsize
            least_idx = -1

            for idx in range(0, end_pos_data.count):
                cost = (
                    end_pos_data.costs[idx]
                    + self.conn_costs[end_pos_data.last_right_id[idx], 0]
                )

                if cost < least_cost:
                    least_cost = cost
                    least_idx = idx

            self.backtrace(end_pos_data, least_idx)

    def backtrace(self, end_pos_data, from_idx):
        end_pos = end_pos_data.pos
        pos = end_pos
        best_idx = from_idx

        while pos > self.last_backtrace_pos:
            pos_data = self.positions.get(pos)
            assert best_idx < pos_data.count

            back_pos = pos_data.back_pos[best_idx]
            back_word_pos = pos_data.back_word_pos[best_idx]
            assert back_pos >= self.last_backtrace_pos

            length = pos - back_word_pos
            back_dict_type = pos_data.back_dict_type[best_idx]
            next_best_idx = pos_data.back_index[best_idx]

            fragment = self.buffer.slice_get(back_word_pos, back_word_pos + length)
            back_pos_type = pos_data.back_pos_type[best_idx]
            morphemes = pos_data.morphemes[best_idx]
            back_pos_tag = pos_data.back_pos_tag[best_idx]

            fragment_offset = back_word_pos - self.last_backtrace_pos
            assert fragment_offset >= 0

            if back_dict_type == Type.UNKNOWN:
                for i in range(length - 1, -1, -1):
                    char_len = 1
                    token = DictionaryToken(
                        dict_type=Type.UNKNOWN,
                        dictionary=None,
                        word_id=None,
                        surface_form=fragment[i],
                        offset=fragment_offset + i,
                        length=char_len,
                        start_offset=back_word_pos + i,
                        end_offset=back_word_pos + i + char_len,
                        pos_type=back_pos_type,
                        morphemes=morphemes,
                        pos_tag=back_pos_tag,
                    )
                    self.pending.append(token)
            else:
                token = DictionaryToken(
                    dict_type=back_dict_type,
                    dictionary=None,
                    word_id=None,
                    surface_form=fragment,
                    offset=fragment_offset,
                    length=length,
                    start_offset=back_word_pos,
                    end_offset=back_word_pos + length,
                    pos_type=back_pos_type,
                    morphemes=morphemes,
                    pos_tag=back_pos_tag,
                )
                if self.split_compound:
                    morphemes = token.morphemes
                    if morphemes is None:
                        self.pending.append(token)
                    else:
                        _end_offset = back_word_pos + length
                        _pos_length = 0
                        for i in range(len(morphemes) - 1, -1, -1):
                            _pos_tag, _surface_form = morphemes[i]
                            _len_surface_form = len(_surface_form)

                            if token.pos_type == Pos.COMPOUND:
                                assert _end_offset - _len_surface_form >= 0
                                decompound_token = DecompoundToken(
                                    pos_tag=_pos_tag,
                                    surface_form=_surface_form,
                                    start_offset=_end_offset - _len_surface_form,
                                    end_offset=_end_offset,
                                    pos_type=Pos.MORPHEME,
                                    dict_type=back_dict_type,
                                )
                            else:
                                decompound_token = DecompoundToken(
                                    pos_tag=_pos_tag,
                                    surface_form=_surface_form,
                                    start_offset=token.start_offset,
                                    end_offset=token.end_offset,
                                    pos_type=Pos.MORPHEME,
                                    dict_type=back_dict_type,
                                )
                            _pos_length += 1
                            _end_offset -= _len_surface_form
                            self.pending.append(decompound_token)
                else:
                    self.pending.append(token)

            if back_word_pos != back_pos:
                offset = back_pos - self.last_backtrace_pos
                len_ = back_word_pos - back_pos
                space_token = DictionaryToken(
                    dict_type=Type.UNKNOWN,
                    dictionary=None,
                    word_id=None,
                    surface_form=" ",
                    offset=offset,
                    length=len_,
                    start_offset=back_pos,
                    end_offset=back_pos + len_,
                    pos_type=Pos.MORPHEME,
                    morphemes=None,
                    pos_tag=self.unknown_dict["SPACE"]["POS"],
                )
                self.pending.append(space_token)

            pos = back_pos
            best_idx = next_best_idx

        self.last_backtrace_pos = end_pos
