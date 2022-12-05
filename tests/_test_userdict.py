from pecab import PeCab

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

user_dict = ["삼성디지털프라자", "지펠냉장고"]
pecab = PeCab(user_dict=user_dict)
output = pecab.pos("저는 삼성디지털프라자에서 지펠냉장고를 샀어요.")

if output != label:
    raise Exception(f"test failed :(\noutput: {output}")
else:
    print(f"test passed ;)\noutput: {output}")
