from pecab import PeCab

label = [
    "자장면",
    "짬뽕",
    "그것",
    "고민",
]

pecab = PeCab()
output = pecab.nouns("자장면을 먹을까? 짬뽕을 먹을까? 그것이 고민이로다.")

if output != label:
    raise Exception(f"test failed :(\noutput: {output}")
else:
    print(f"test passed ;)\noutput: {output}")
