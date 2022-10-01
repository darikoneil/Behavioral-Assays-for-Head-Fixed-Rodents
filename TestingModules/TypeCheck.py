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
    _dir = "".join([BasePath, "\\Data\\", "Test_Mouse"])
    if path.exists(_dir):
        rmtree(_dir)


def test_lick_training_config(*args):
    """
    This function tests validity & integrity of the lick training configuration

    :param args: To pass a specific burrow_config use the key lick_training_config
    :rtype: None
    """

    if args:
        lick_training_config = args[0]
    else:
        from LickBehaviorConfigurations import LickTrainingConfig
        lick_training_config = LickTrainingConfig()
    
        # animal id
    assert(isinstance(lick_training_config.animal_id, str))

    # base path
    assert(isinstance(lick_training_config.base_path, str))

    # data path
    assert(isinstance(lick_training_config.data_path, str))

    # habituation duration
    assert(isinstance(lick_training_config.habituation_duration, int))

    # single lick vol
    assert(isinstance(lick_training_config.single_lick_volume, float))

    # max lick vol
    assert(isinstance(lick_training_config.max_liquid_intake, float))

    # licks per trial
    assert(isinstance(lick_training_config.licks_per_trial, int))


def cleanup_lick_training_config(BasePath):
    from shutil import rmtree
    _dir = "".join([BasePath, "\\Data\\", "Test_Mouse"])
    if path.exists(_dir):
        rmtree(_dir)
