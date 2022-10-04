from TestingModules.testing_utility_functions import load_pickle_from_file
from os import getcwd
from time import time
# Burrow Preference DAQ Tests
from BurrowPreferenceTask.RunBurrowPreference import DAQtoBurrow

# Licking Training DAQ Tests
from LickingTraining.RunLickTraining import DAQtoLickTraining

# Burrow


def test_daq_burrow_preference():
    """
    This tests DAQ instantiation

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_BPT.pkl"]))
    DAQ = DAQtoBurrow(Config)


def test_daq_burrow_preference_acquisition():
    """
    This tests DAQ acquisition

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_BPT.pkl"]))
    DAQ = DAQtoBurrow(Config)
    DAQ.startAcquisition()


def test_daq_burrow_preference_runtime():
    """
    This tests daq runtime

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_BPT.pkl"]))
    DAQ = DAQtoBurrow(Config)
    DAQ.startAcquisition()
    _not_started = True
    while DAQ.behavior_complete is False:
        if _not_started:
            _not_started = False
            DAQ.burrow_preference_machine.start_run = True
            DAQ.startBehavior()

# Lick


def test_daq_lick():
    """
    This tests DAQ instantiation

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_LTC.pkl"]))
    DAQ = DAQtoLickTraining(Config)


def test_daq_lick_acquisition():
    """
    This tests DAQ acquisition

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_LTC.pkl"]))
    DAQ = DAQtoLickTraining(Config)
    DAQ.startAcquisition()



def test_daq_lick_runtime():
    Config = load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_LTC.pkl"]))
    DAQ = DAQtoLickTraining(Config)
    DAQ.cameras_on = True
    DAQ.startAcquisition()
    _not_started = True
    _start_time = time()
    _dur = 10
    while DAQ.training_complete is False:
        if _not_started:
            _not_started = False
            DAQ.start_training()
        if (time()-_dur) > _start_time:
            DAQ.end_training()
