import numpy as np
import pickle
from os import path


class Saver:

    def __init__(self):
        self.bufferedData = np.array([0], dtype=np.float64)
        currentPath = path.dirname(path.realpath(__file__))
        self.filename = currentPath + "\\startle.npy"  # default file path
        # Constructor for threading

    def timeToSave(self):
        np.save(self.filename, self.bufferedData)
        return True


class Pickler:

    def __init__(self):
        currentPath = path.dirname(path.realpath(__file__))
        self.filename = currentPath + "\\pickles.npy"  # default file path
        self.pickledPickles = None

    def timeToSave(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.pickledPickles, f)
        return True

