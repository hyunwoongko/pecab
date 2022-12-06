from pecab import PeCab
from tests import pecab   # noqa

label = [
    ("토끼", "NNG"),
    ("정", "NNG"),
    ("에서", "JKB"),
    (" ", "SP"),
    ("크림", "NNG"),
    (" ", "SP"),
    ("우동", "NNG"),
    ("을", "JKO"),
    (" ", "SP"),
    ("시켰", "VV+EP"),
    ("어요", "EF"),
    (".", "SF"),
]


def test(pecab: PeCab):
    assert pecab.pos("토끼정에서 크림 우동을 시켰어요.", drop_space=False) == label
