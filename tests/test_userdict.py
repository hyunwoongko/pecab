from pecab import PeCab
from tests import pecab_with_userdict  # noqa

label = [
    ("저", "NP"),
    ("는", "JX"),
    ("삼성디지털프라자", "NNG"),
    ("에서", "JKB"),
    ("지펠냉장고", "NNG"),
    ("를", "JKO"),
    ("샀", "VV+EP"),
    ("어요", "EF"),
    (".", "SF"),
]


def test_userdict(pecab_with_userdict: PeCab):
    assert pecab_with_userdict.pos("저는 삼성디지털프라자에서 지펠냉장고를 샀어요.") == label
