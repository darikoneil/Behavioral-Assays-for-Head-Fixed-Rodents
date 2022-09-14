from BurrowPreferenceMachine import BurrowPreferenceTask
from testing_utility_functions import load_pickle_from_file
from os import getcwd


def test_run_machine():
    """
    This function assess the integrity of the Burrow Preference Machine during execution

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    BPT = BurrowPreferenceTask(Config)
    BPT.start_run = True
    BPT.proceed_sync = True
    BPT.saving_complete = True
    assert(BPT.state == "Setup")
    assert(BPT.start_run is True)
    BPT.start()
    assert(BPT.proceed_sync is True)
    assert(BPT.habituation_complete is True)
    assert(BPT.preference_complete is True)
    assert(BPT.saving_complete is True)
    assert(BPT.state == "End")
    assert(BPT.start_run is False)
    assert(int(BPT.hab_end-BPT.hab_start) == Config.habituation_duration)
    assert(int(BPT.pref_end-BPT.pref_start) == Config.behavior_duration)


def test_machine_vars():
    """
    This function assess the integrity of the Config-Passed Burrow Preference Machine Variables

    :rtype: None
    """
    Config = load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"]))
    BPT = BurrowPreferenceTask(Config)
    BPT.start_run = True
    BPT.proceed_sync = True
    BPT.saving_complete = True
    BPT.start()
    assert(BPT.habituation_duration == Config.habituation_duration)
    assert(BPT.behavior_duration == Config.behavior_duration)
    assert(BPT.animal_id == Config.animal_id)
