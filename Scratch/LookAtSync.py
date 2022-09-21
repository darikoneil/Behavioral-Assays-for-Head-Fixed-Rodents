import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt


def look_at_sync(_base_path, _animal_id):

    _analog = np.load("".join([_base_path, "\\", _animal_id, "\\", "analog.npy"]))

    _digital = np.load("".join([_base_path, "\\", _animal_id, "\\", "digital.npy"]))
    _digital = abs(_digital)-1
    _state = np.load("".join([_base_path, "\\", _animal_id, "\\", "state.npy"]))

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(311)
    ax1.plot(_digital)
    ax2 = fig1.add_subplot(312)
    ax2.plot(_analog[0, :])
    ax3 = fig1.add_subplot(313)
    ax3.plot(_analog[1, :])
