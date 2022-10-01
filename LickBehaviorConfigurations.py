from os import mkdir, getcwd
from TestingModules.TypeCheck import test_burrow_preference_config, test_lick_training_config, \
    cleanup_burrow_preference_config, cleanup_lick_training_config
import numpy as np
import random


class BurrowPreferenceConfig:
    """
    Configuration File for Burrow Preference Task
    """
    def __init__(self, *args):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "Test_Mouse"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\Data\\", self.animal_id])

        # Behavior Parameters
        self._habituation_duration = 5 # Habituation duration in seconds, integer
        self._behavior_duration = 5 # Burrow preference duration in seconds, integer

        # Make the data folder - SHOULD NOT EXIST
        try:
            mkdir(self.data_path)
        except FileExistsError:
            if args:
                pass
            else:
                print("\nThis folder already exists!!! Please use unique animal identifiers!\n")
                return

        # Check Integrity
        self.validated = self.validation()

        try:
            assert(self.validated is True)
        except AssertionError:
            print("Configuration could not be validated")
            return
        except AttributeError:
            return

    @property
    def animal_id(self):
        """
        ID of animal

        :rtype: str
        """
        return self._animal_id

    @property
    def base_path(self):
        """
       Path to create a data folder in

        :rtype: str
        """
        return self._base_path

    @property
    def data_path(self):
        """
        Location of created data folder

        :rtype: str
        """
        return self._data_path

    @property
    def habituation_duration(self):
        """
        Duration of habituation in seconds

        :rtype: int
        """
        return self._habituation_duration

    @property
    def habituation_duration_minutes(self):
        """
        Duration of habituation in minutes

        :rtype: int
        """
        return self._habituation_duration/60

    @property
    def behavior_duration(self):
        """
        Duration of behavior in seconds

        :rtype: int
        """
        return self._behavior_duration

    @property
    def behavior_duration_minutes(self):
        """
        Duration of behavior in minutes

        :rtype: int
        """
        return self._behavior_duration/60

    def validation(self):
        try:
            test_burrow_preference_config(self)
            return True
        except RuntimeError:
            return False


class LickTrainingConfig:
    """
    Configuration File for Lick Training Task
    """
    def __init__(self, *args):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "Test_Mouse"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\Data\\", self.animal_id])

        # Behavior Parameters
        self._habituation_duration = 5 # Habituation duration in seconds, integer
        self._single_lick_volume = 3.8 # liquid dispensed in response to single lick (uL)
        self._max_liquid_intake = 1.0 # upper limit of total liquid consumption (mL)
        self._rewards_per_trial = 25 # Number of rewards per trial
        self._reward_duration_water = 20.125 # ms
        self._reward_duration_sucrose = 18.5 # ms
        self._dual_starts = 0 # Number of dual starts
        self._wet_starts = 4 # Number of wet starts
        self._spout_index = self.generate_spout_index()

        # Make the data folder - SHOULD NOT EXIST
        try:
            mkdir(self.data_path)
        except FileExistsError:
            if args:
                pass
            else:
                print("\nThis folder already exists!!! Please use unique animal identifiers!\n")
                return

        # Check Integrity
        self.validated = self.validation()

        try:
            assert(self.validated is True)
        except AssertionError:
            print("Configuration could not be validated")
            return
        except AttributeError:
            return

    @property
    def animal_id(self):
        """
        ID of animal

        :rtype: str
        """
        return self._animal_id

    @property
    def base_path(self):
        """
       Path to create a data folder in

        :rtype: str
        """
        return self._base_path

    @property
    def data_path(self):
        """
        Location of created data folder

        :rtype: str
        """
        return self._data_path

    @property
    def habituation_duration(self):
        """
        Duration of habituation in seconds

        :rtype: int
        """
        return self._habituation_duration

    @property
    def habituation_duration_minutes(self):
        """
        Duration of habituation in minutes

        :rtype: float
        """
        return self._habituation_duration/60

    @property
    def single_lick_volume(self):
        """
        Volume of liquid release upon single lick in microliters

        :rtype: float
        """
        return self._single_lick_volume

    @property
    def single_lick_volume_mL(self):
        return self._single_lick_volume/1000

    @property
    def max_liquid_intake(self):
        """
        Maximal intake of liquid permitted in milliliters

        :rtype: float
        """    
        return self._max_liquid_intake

    @property
    def total_rewards_allowed(self):
        """
        Number of licks permitted before maximum liquid intake

        :rtype: int
        """
        return np.floor(self._max_liquid_intake*1000/self._single_lick_volume, dtype=int)

    @property
    def total_rewards_allowed_given_trials(self):
        """

        :rtype: int
        """
        return self.num_trials*self.rewards_per_trial

    @property
    def intake_limit_given_trials_uL(self):
        """

        :rtype: float
        """
        return self.num_trials*self.rewards_per_trial*self.single_lick_volume

    @property
    def intake_limit_given_trials_mL(self):
        """

        :rtype: float
        """
        return self.num_trials*self.rewards_per_trial*self.single_lick_volume_mL

    @property
    def num_trials(self):
        """
        Number of sucrose preference trials

       :rtype: int
       """
        return np.floor(self.total_rewards_allowed/self._rewards_per_trial, dtype=int)

    @property
    def volume_per_trial(self):
        """
        Liquid dispensed per trial in uL

        :rtype: float
        """
        return self._rewards_per_trial*self.single_lick_volume

    @property
    def rewards_per_trial(self):
        """
        Number of licks per trial

        :rtype: int
        """
        return self._rewards_per_trial

    @property
    def reward_duration_water(self):
        """
        Duration of solenoid being opened for reward (water, ms)

        :rtype: float
        """
        return self._reward_duration_water

    @property
    def reward_duration_sucrose(self):
        """
        Duration of solenoid being opened for reward (sucrose, ms)

        :rtype: float
        """
        return self._reward_duration_sucrose

    @property
    def wet_starts(self):
        """

        :rtype: int
        """
        return self._wet_starts

    @property
    def dual_starts(self):
        """

        :rtype: int
        """
        return self._dual_starts

    @property
    def spout_index(self):
        """
        Index of Spout Configuration By Trial

        :rtype: tuple
        """
        return self._spout_index

    def generate_spout_index(self):
        """

        :rtype: tuple
        """
        SpoutIndex = []
        _num_stages = int(np.floor(self.num_trials/2))
        _states = ["Water", "Sucrose"]


        for i in range(_num_stages):
            random.shuffle(_states)
            SpoutIndex.extend(_states)
            if len(SpoutIndex) != self.num_trials:
                random.shuffle(_states)
                SpoutIndex.extend(1)

        return tuple(SpoutIndex)

    def validation(self):
        try:
            test_lick_training_config(self)
            return True
        except RuntimeError:
            return False


if __name__ == '__main__':
    BPC = BurrowPreferenceConfig()
    print("".join(["MouseID: ", BPC.animal_id]))
    print("".join(["Base Directory: ", BPC.base_path]))
    print("".join(["Data Folder: ", BPC.data_path]))
    print("".join(["Habituation Duration: ", str(BPC.habituation_duration)]))
    print("".join(["Behavior Duration: ", str(BPC.behavior_duration)]))
    print("".join(["Configuration Validated: ", str(BPC.validated)]))
    cleanup_burrow_preference_config(getcwd())

    LTC = LickTrainingConfig()
    print("".join(["MouseID: ", LTC.animal_id]))
    print("".join(["Base Directory: ", LTC.base_path]))
    print("".join(["Data Folder: ", LTC.data_path]))
    print("".join(["Habituation Duration: ", str(LTC.habituation_duration)]))
    print("".join(["Licks Per Trial: ", str(LTC.rewards_per_trial)]))
    print("".join(["Lick Volume: ", str(LTC.single_lick_volume)]))
    print("".join(["Maximal Intake: ", str(LTC.max_liquid_intake)]))
    print("".join(["Configuration Validated: ", str(LTC.validated)]))
    print("".join(["Total Rewards Allowed: ", str(LTC.total_rewards_allowed)]))
    cleanup_lick_training_config(getcwd())
