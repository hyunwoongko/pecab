from pecab import PeCab
from tests import pecab_with_split_compound  # noqa

label = [
    "가볍",
    "ᆫ",
    "냉장",
    "고",
    "를",
    "사",
    "ㅏㅆ",
    "어요",
    ".",
]


def test_split_compound(pecab_with_split_compound: PeCab):
    assert pecab_with_split_compound.morphs("가벼운 냉장고를 샀어요.") == label
