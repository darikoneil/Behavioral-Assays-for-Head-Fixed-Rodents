from os import getcwd
import numpy as np
import pickle as pkl



def test_data_loading():
    _base_path = getcwd()
    _animal_id = "BTest"

    with open("".join([_base_path, "\\", _animal_id, "\\", "behavior_config"]), "rb") as f:
        _config = pkl.load(f)

    _analog = np.load("".join([_base_path, "\\", _animal_id, "\\", "analog.npy"]))

    _digital = np.load("".join([_base_path, "\\", _animal_id, "\\", "digital.npy"]))

    _state = np.load("".join([_base_path, "\\", _animal_id, "\\", "state.npy"]))

    _cam_1_meta = np.genfromtxt("".join([_base_path, "\\", _animal_id, "\\", "_cam1__meta.txt"]), delimiter=",", dtype=int)

    _cam_1_Frames = np.fromfile("".join([_base_path, "\\", _animal_id, "\\", "_cam1__Frame.npy"]), dtype=np.uint8)

    _cam_1_Frames = _cam_1_Frames.reshape(_cam_1_meta[0], _cam_1_meta[1], _cam_1_meta[2])

    _cam_1_FrameIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam1__FramesIDs.npy"]))

    _cam_1_BufferIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam1__BufferIDs.npy"]))

    _cam_2_meta = np.genfromtxt("".join([_base_path, "\\", _animal_id, "\\", "_cam2__meta.txt"]), delimiter=",", dtype=int)

    _cam_2_Frames = np.fromfile("".join([_base_path, "\\", _animal_id, "\\", "_cam2__Frame.npy"]), dtype=np.uint8)

    _cam_2_Frames = _cam_2_Frames.reshape(_cam_2_meta[0], _cam_2_meta[1], _cam_2_meta[2])

    _cam_2_FrameIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam2__FramesIDs.npy"]))

    _cam_2_BufferIDs = np.load("".join([_base_path, "\\", _animal_id, "\\", "_cam2__BufferIDs.npy"]))

    with open("".join([_base_path, "\\", _animal_id, "\\", "hardware_config"]), "rb") as f:
        _hardware = pkl.load(f)

    _daq_catch_times = np.load("".join([_base_path, "\\", _animal_id, "\\", "daq_catch_times.npy"]))
