from pecab._tokenizer import Type
from pecab._tokens import TokenAttributes
from pecab._utils._consts import Pos


class Postprocessor:
    @staticmethod
    def _init_unk_token_attribute(terms, offsets):
        unknown = TokenAttributes()
        unknown.terms = [terms]
        unknown.offsets = [offsets]
        unknown.pos_length = [1]
        unknown.pos_types = [Pos.MORPHEME]
        unknown.pos_tags = ["UNKNOWN"]
        unknown.dict_types = [Type.UNKNOWN]
        return unknown

    @staticmethod
    def _merge_token_attribute(source, target):
        for name, _ in target.__dict__.items():
            target.__dict__[name] += source.__dict__[name]
        return target

    def relax_long_unk(self, tkn_attr_obj, tokenizer):
        long_unknown_token = tkn_attr_obj.terms[0]
        idx = -1
        for i, ch in enumerate(long_unknown_token):
            if i == 0:
                pch = ch
            if ch != pch:
                idx = i
                break

        if idx == -1:
            return tkn_attr_obj

        front_string = long_unknown_token[:idx]
        rest_string = long_unknown_token[idx:]
        front_tkn_attr = self._init_unk_token_attribute(
            terms=front_string, offsets=(0, len(front_string) - 1)
        )

        tokenizer.set_input(rest_string)
        while tokenizer.increment_token():
            pass
        rest_tkn_attr = tokenizer.tkn_attr_obj
        return self._merge_token_attribute(source=rest_tkn_attr, target=front_tkn_attr)
