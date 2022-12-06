"""
__init__ as a factory of fixtures
"""
import pytest
from pecab import PeCab


@pytest.fixture(scope="session")
def pecab() -> PeCab:
    return PeCab()


@pytest.fixture(scope="session")
def pecab_with_userdict() -> PeCab:
    user_dict = ["삼성디지털프라자", "지펠냉장고"]
    return PeCab(user_dict=user_dict)


@pytest.fixture(scope="session")
def pecab_with_split_compound() -> PeCab:
    return PeCab(split_compound=True)
