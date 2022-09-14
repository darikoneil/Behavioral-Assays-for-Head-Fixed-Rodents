from RunBurrowPreference import DAQtoBurrow
from HardwareConfiguration import HardConfig
from testing_utility_functions import load_pickle_from_file
from os import getcwd


def test_daq():
    """
    This tests DAQ instantiation

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    DAQ = DAQtoBurrow(Config)
