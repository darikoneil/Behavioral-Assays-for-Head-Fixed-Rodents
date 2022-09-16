# Conduct type check of behavioral configurations
from os import path


def test_burrow_preference_config(*args):
    """
    This function tests validity & integrity of the burrow preference configuration

    :param args: To pass a specific burrow_config use the key burrow_preference_config
    :rtype: None
    """

    if args:
        burrow_preference_config = args[0]
    else:
        from LickBehaviorConfigurations import BurrowPreferenceConfig
        burrow_preference_config = BurrowPreferenceConfig()

    # animal id
    assert(isinstance(burrow_preference_config.animal_id,  str))

    # base path
    assert(isinstance(burrow_preference_config.base_path, str))

    # data path
    assert(isinstance(burrow_preference_config.data_path, str))

    # habituation duration
    assert(isinstance(burrow_preference_config.habituation_duration, int))

    # behavior duration
    assert(isinstance(burrow_preference_config.behavior_duration, int))


def cleanup_burrow_preference_config(BasePath):
    from shutil import rmtree
    _dir = "".join([BasePath, "\\", "Test_Mouse"])
    if path.exists(_dir):
        rmtree(_dir)

def test_burrow_preference_config(*args):
    """
    This function tests validity & integrity of the sucrose preference configuration

    :param args: To pass a specific burrow_config use the key sucrose_preference_config
    :rtype: None
    """

    if args:
        sucrose_preference_config = args[0]
    else:
        from LickBehaviorConfigurations import SucrosePreferenceConfig
        sucrose_preference_config = SucrosePreferenceConfig()
    
        # animal id
    assert(isinstance(sucrose_preference_config.animal_id,  str))

    # base path
    assert(isinstance(sucrose_preference_config.base_path, str))

    # data path
    assert(isinstance(sucrose_preference_config.data_path, str))

    # habituation duration
    assert(isinstance(sucrose_preference_config.habituation_duration, int))

    # single lick vol
    assert(isinstance(sucrose_preference_config.single_lick_volume, int))

    # max lick vol
    assert(isinstance(sucrose_preference_config.max_liquid_intake, int))

    # licks per trial
    assert(isinstance(sucrose_preference_config.licks_per_trial, int))

def cleanup_sucrose_preference_config(BasePath):
    from shutil import rmtree
    _dir = "".join([BasePath, "\\", "Test_Mouse"])
    if path.exists(_dir):
        rmtree(_dir)
