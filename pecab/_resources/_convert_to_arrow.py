# https://towardsdatascience.com/apache-arrow-read-dataframe-with-zero-memory-69634092b1a
import gzip
import pickle
import pandas as pd
from tqdm import tqdm

from pecab._datrie import DoubleArrayTrie
import pyarrow as pa


with gzip.open("mecab_csv.pkl", "rb") as rf:
    entries = pickle.load(rf)


data = {}
for i, (key, val) in tqdm(enumerate(entries)):
    surface = val["surface"]
    if surface not in data:
        data[surface] = {k: str(v) for k, v in val.items()}
    else:
        for k, v in val.items():
            if k != "surface":
                data[surface][k] += f"|{v}"

trie = DoubleArrayTrie(data)
words = pd.DataFrame.from_records(list(trie._value))
words = pa.Table.from_pandas(words)

arrays = {"base": trie._base, "check": trie._check}
arrays = pd.DataFrame.from_dict(arrays)
arrays = pa.Table.from_pandas(arrays)

with pa.OSFile("words.arrow", "wb") as sink:
    with pa.RecordBatchFileWriter(sink, words.schema) as writer:
        writer.write_table(words)

with pa.OSFile("arrays.arrow", "wb") as sink:
    with pa.RecordBatchFileWriter(sink, arrays.schema) as writer:
        writer.write_table(arrays)

# read file:
# arrays = pa.ipc.RecordBatchFileReader(pa.memory_map("arrays.arrow", "r")).read_all()
# words = pa.ipc.RecordBatchFileReader(pa.memory_map("words.arrow", "r")).read_all()
# trie = DoubleArrayTrie.from_files(arrays, words)
# out = trie.get("가나안")
