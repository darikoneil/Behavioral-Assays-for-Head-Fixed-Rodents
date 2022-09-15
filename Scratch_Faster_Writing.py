import imageio as iio
from timeit import timeit
import numpy as np

Filename1  = "C:\\Users\\YUSTE\\Desktop\\test.npy)
Filename2 = "C:\\Users\\YUSTE\\Desktop\\test.mp4")

timeit('iiio.mimwrite(Filename1, np.random.randint(1, 255, (10000, 512, 512), dtype=np.int8), fps=30, quality=10, macro_block_size=4)', number=5)

timeit('np.save(Filename2, np.random.randint(1, 255, (10000, 512, 512), dtype=np.int8))', number=5)

