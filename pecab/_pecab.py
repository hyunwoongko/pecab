from functools import lru_cache
from typing import Optional, List

from pecab._postprocessor import Postprocessor
from pecab._tokenizer import Tokenizer
from pecab._utils._consts import Type, Tokenization


class PeCab:
    def __init__(
        self, user_dict: Optional[List[str]] = None, split_compound: bool = False
    ):
        self.tokenizer = Tokenizer(user_dict, split_compound)
        self.postprocessor = Postprocessor()

    @lru_cache(maxsize=5000)
    def _tokenize(self, text: str):
        self.tokenizer.set_input(text)
        while self.tokenizer.increment_token():
            pass

        token_attributes = self.tokenizer.token_attributes

        if (
            len(token_attributes.terms) == 1
            and token_attributes.dict_types[0] == Type.UNKNOWN
            and len(token_attributes.terms[0]) >= Tokenization.MIN_CHAR_LENGTH
        ):
            token_attributes = self.postprocessor.relax_long_unk(
                token_attributes, self.tokenizer
            )

        return token_attributes.get()

    def morphs(self, text: str, drop_space: bool = True):
        tokenization_output = self._tokenize(text)
        return [
            token
            for token in tokenization_output["terms"]
            if drop_space is False
            or (drop_space and token not in " \t\n\r\f\v")
        ]

    def pos(self, text: str, drop_space: bool = True):
        tokenization_output = self._tokenize(text)
        return [
            (token, pos)
            for token, pos in zip(
                tokenization_output["terms"], tokenization_output["pos_tags"]
            )
            if drop_space is False
            or (drop_space and token not in " \t\n\r\f\v")
        ]

    def nouns(self, text: str, drop_space: bool = True):
        tokenization_output = self._tokenize(text)
        return [
            token
            for token, pos in zip(
                tokenization_output["terms"], tokenization_output["pos_tags"]
            )
            if (
                drop_space is False
                or (drop_space and token not in " \t\n\r\f\v")
            )
            and pos.startswith("N")
        ]
