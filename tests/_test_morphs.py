from pecab import PeCab

label = [
    "아버지",
    "가",
    "방",
    "에",
    "들어가",
    "시",
    "다",
]

pecab = PeCab()
output = pecab.morphs("아버지가방에들어가시다")

if output != label:
    raise Exception(f"test failed :(\noutput: {output}")
else:
    print(f"test passed ;)\noutput: {output}")
