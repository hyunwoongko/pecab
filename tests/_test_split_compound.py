from pecab import PeCab

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

pecab = PeCab(split_compound=True)
output = pecab.morphs("가벼운 냉장고를 샀어요.")

if output != label:
    raise Exception(f"test failed :(\noutput: {output}")
else:
    print(f"test passed ;)\noutput: {output}")
