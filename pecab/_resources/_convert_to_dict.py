import pandas as pd

from pecab._utils._consts import Pos

names = [
    "surface",
    "left_id",
    "right_id",
    "word_cost",
    "POS",
    "POS_type",
    "morphemes",
    "useless.1",
    "useless.2",
    "useless.3",
    "useless.4",
    "useless.5",
]

data_pandas = pd.read_csv("unk.def", names=names)
data_entries = {}

for entry in data_pandas.to_dict("records"):
    data_entry = {}
    surface = None
    for key, val in entry.items():
        if "useless" not in key:
            if key == "POS_type":
                val = "Pos.MORPHEME"
            elif key == "morphemes":
                val = None
            elif key == "surface":
                surface = val
            data_entry[key] = val
    data_entries[surface] = data_entry

data_entries["EMOJI"] = (
    {
        "surface": "EMOJI",
        "left_id": 1801,
        "right_id": 3566,
        "word_cost": 3640,
        "POS": "SY",
        "POS_type": Pos.MORPHEME,
        "morphemes": None,
    },
)

with open("unknown.py", mode="w") as fp:
    code = f"""from pecab.utils.pos import Pos

UNK = {data_entries}
"""
    code = code.replace("'Pos.MORPHEME'", "Pos.MORPHEME")
    fp.write(code + "\n")

# read file
# from pecab.resources.unk import UNK
