from BurrowPreferenceTask.RunBurrowPreference import DAQtoBurrow
from testing_utility_functions import load_pickle_from_file
from os import getcwd


def test_daq():
    """
    This tests DAQ instantiation

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    DAQ = DAQtoBurrow(Config)


def test_daq_acquisition():
    """
    This tests DAQ acquisition

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    DAQ = DAQtoBurrow(Config)
    DAQ.startAcquisition()


def test_daq_runtime():
    """
    This tests daq runtime

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    DAQ = DAQtoBurrow(Config)
    DAQ.startAcquisition()
    _not_started = True
    while DAQ.behavior_complete is False:
        if _not_started:
            _not_started = False
            DAQ.burrow_preference_machine.start_run = True
            DAQ.startBehavior()
