class Token(object):
    def __init__(
        self,
        surface_form,
        offset,
        length,
        start_offset,
        end_offset,
        pos_type,
        morphemes,
        pos_tag,
        dict_type,
    ):
        self.surface_form = surface_form
        self.offset = offset
        self.length = length
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.pos_type = pos_type
        self.morphemes = morphemes
        self.pos_tag = pos_tag
        self.dict_type = dict_type
        self.pos_incr = 1
        self.pos_len = 1


class DictionaryToken(Token):
    def __init__(
        self,
        dict_type,
        dictionary,
        word_id,
        surface_form,
        offset,
        length,
        start_offset,
        end_offset,
        pos_type,
        morphemes,
        pos_tag,
    ):
        super().__init__(
            surface_form,
            offset,
            length,
            start_offset,
            end_offset,
            pos_type,
            morphemes,
            pos_tag,
            dict_type,
        )
        self.dict_type = dict_type
        self.dictionary = dictionary
        self.word_id = word_id


class DecompoundToken(Token):
    def __init__(
        self,
        pos_tag,
        surface_form,
        start_offset,
        end_offset,
        pos_type,
        dict_type,
    ):
        super().__init__(
            surface_form,
            0,
            len(surface_form),
            start_offset,
            end_offset,
            pos_type,
            None,
            pos_tag,
            dict_type,
        )


class TokenAttributes(object):
    def __init__(self):
        self.terms = []
        self.offsets = []
        self.pos_length = []
        self.pos_types = []
        self.pos_tags = []
        self.dict_types = []

    def get(self):
        return self.__dict__
