from pecab import PeCab
from tests import pecab   # noqa


label = [
    "아버지",
    "가",
    "방",
    "에",
    "들어가",
    "시",
    "다",
]


def test_morphs(pecab: PeCab):
    assert pecab.morphs("아버지가방에들어가시다") == label

