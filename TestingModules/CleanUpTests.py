from TestingModules.TypeCheck import cleanup_burrow_preference_config, cleanup_lick_training_config


def pre_clean_test(BasePath):
    print("Pre-Cleaning")
    cleanup_burrow_preference_config(BasePath)
    cleanup_lick_training_config(BasePath)
    print("Finished")


def clean_up_test(BasePath):
    print("Cleaning up...")
    cleanup_burrow_preference_config(BasePath)
    cleanup_lick_training_config(BasePath)
    print("Finished")
