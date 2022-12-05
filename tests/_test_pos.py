from pecab import PeCab

label = [
    ("이것", "NP"),
    ("은", "JX"),
    ("문장", "NNG"),
    ("입니다", "VCP+EF"),
    (".", "SF"),
]

pecab = PeCab()
output = pecab.pos("이것은 문장입니다.")

if output != label:
    raise Exception(f"test failed :(\noutput: {output}")
else:
    print(f"test passed ;)\noutput: {output}")
