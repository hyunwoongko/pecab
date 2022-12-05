class Pos:
    MORPHEME = "MORP"
    COMPOUND = "COMP"
    INFLECT = "INFL"
    PREANALYSIS = "PREANY"


class Type:
    KNOWN = "KN"
    UNKNOWN = "UKN"
    USER = "US"


class Tokenization:
    MIN_CHAR_LENGTH = 7
    MAX_UNKNOWN_WORD_LENGTH = 1024
    CONN_SHAPE = (3822, 2693)
