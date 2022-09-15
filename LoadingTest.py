from os import getcwd
import numpy as np
import pickle as pkl
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

_animal_id = "Mouse X"

_base_path = getcwd()

_analog = np.load("".join([_base_path, "\\", _animal_id, "\\", "analog.npy"]))

_digital = np.load("".join([_base_path, "\\", _animal_id, "\\", "digital.npy"]))

_state = np.load("".join([_base_path, "\\", _animal_id, "\\", "state.npy"]))

_cam_1_Frames = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam1__Frame.npy"]))

_cam_1_FrameIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam1__FramesIDs.npy"]))

_cam_1_BufferIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam1__BufferIDs.npy"]))

_cam_2_Frames = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam2__Frame.npy"]))

_cam_2_FrameIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam2__FramesIDs.npy"]))

_cam_2_BufferIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam2__BufferIDs.npy"]))

with open("".join([_base_path, "\\", _animal_id, "\\", "hardware_config"]), "rb") as f:
    _hardware = pkl.load(f)

with open("".join([_base_path, "\\", _animal_id, "\\", "behavior_config"]), "rb") as f:
    _config = pkl.load(f)

_daq_catch_times = np.load("".join([_base_path, "\\", _animal_id, "\\", "daq_catch_times.npy"]))
