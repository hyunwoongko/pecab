from pecab import PeCab
from tests import pecab   # noqa

label = [
    ("이것", "NP"),
    ("은", "JX"),
    ("문장", "NNG"),
    ("입니다", "VCP+EF"),
    (".", "SF"),
]


def test_pos(pecab: PeCab):
    assert pecab.pos("이것은 문장입니다.") == label
