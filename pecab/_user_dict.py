from functools import lru_cache

from pecab._utils._consts import Pos


class UserDictionary:
    WORD_COST = -10000
    LEFT_ID = 1781
    RIGHT_ID = 3533
    RIGHT_ID_T = 3535
    RIGHT_ID_F = 3534
    USER_POS = "NNG"

    @lru_cache(maxsize=50)
    def __getitem__(self, item):
        if item in self.user_token_info:
            return self.user_token_info[item]
        else:
            return None

    def __init__(self, char_definition, entries):
        entries = sorted(entries, reverse=True)
        self.user_token_info = {}

        for token in entries:
            token = token.strip()

            if len(token) == 0:
                continue

            elif " " in token:
                raise ValueError("User defined words can not contain space.")

            last_char = token[-1]
            if char_definition.is_hangul(last_char):
                if char_definition.has_coda(last_char):
                    right_id = self.RIGHT_ID_T
                else:
                    right_id = self.RIGHT_ID_F
            else:
                right_id = self.RIGHT_ID

            morph_inf = dict()
            morph_inf["surface"] = token
            morph_inf["left_id"] = self.LEFT_ID
            morph_inf["right_id"] = right_id
            morph_inf["word_cost"] = int(self.WORD_COST)
            morph_inf["POS"] = self.USER_POS
            morph_inf["POS_type"] = Pos.MORPHEME
            morph_inf["morphemes"] = None
            self.user_token_info[token] = morph_inf
