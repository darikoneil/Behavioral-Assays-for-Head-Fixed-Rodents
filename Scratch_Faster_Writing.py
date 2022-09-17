import numpy as np
from time import time
from os import getcwd

_base_path = getcwd()
_animal_id = "M33780_ALONE_REAL_2"

Frames = np.fromfile("".join([_base_path, "\\", _animal_id, "\\_cam1__Frame.npy"]), dtype=np.uint8)

Shapes = np.genfromtxt("".join([_base_path, "\\", _animal_id, "\\_cam1__meta.txt"]), delimiter=",")

Frames = Frames.reshape(int(Shapes[0]), int(Shapes[1]), int(Shapes[2]))

_start = time()

Frames.tofile("C:\\Users\\YUSTE\\Desktop\\test_large.bin")

_end = time()-_start

print("".join(["Took ", str(_end), "Seconds To Write"]))

_start = time()

Frames.tofile("C:\\Users\\YUSTE\\Desktop\\test_large.bin")

_end = time()-_start

print("".join(["Took ", str(_end), "Seconds To Write"]))

from time import time
_start = time()
BF = np.array(RF, dtype=np.uint8)
_end = time()-_start
print(str(_end))