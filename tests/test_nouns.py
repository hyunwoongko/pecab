from pecab import PeCab
from tests import pecab   # noqa


label = [
    "자장면",
    "짬뽕",
    "그것",
    "고민",
]


def test_nouns(pecab: PeCab):
    assert pecab.nouns("자장면을 먹을까? 짬뽕을 먹을까? 그것이 고민이로다.") == label

