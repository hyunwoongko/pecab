import gzip
import pickle

import numpy as np

with gzip.open("matrix_def.pkl", "rb") as rf:
    matrix_dict = pickle.load(rf)

matrix_list = [list(line.values()) for line in matrix_dict.values()]
matrix_numpy = np.array(matrix_list, dtype=np.int16)
# int16 can cover [-8,239, 10,000]

mmap_numpy = np.memmap(
    "matrix.npy",
    dtype="int16",
    mode="w+",
    shape=matrix_numpy.shape,
)
mmap_numpy[:] = matrix_numpy[:]
mmap_numpy.flush()

# read file:
# matrix = np.memmap("matrix.npy", mode="r+", shape=(3822, 2693), dtype="int16")
