from os import mkdir, getcwd
from TypeCheck import test_burrow_preference_config, test_sucrose_preference_config


class BurrowPreferenceConfig:
    """
    Configuration File for Burrow Preference Task
    """
    def __init__(self, *args):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "BTest"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\", self.animal_id])

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

class SucrosePreferenceConfig:
    """
    Configuration File for Sucrose Preference Task
    """
    def __init__(self, *args):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "CTest"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\", self.animal_id])

        # Behavior Parameters
        self._habituation_duration = 5 # Habituation duration in seconds, integer
        self._preference_trial_duration = 5 # Sucrose preference duration in seconds, integer
        self._num_preference_trials = 5 # Number of sucrose preference trials
        self._single_lick_volume = 3 # liquid dispensed in response to single lick (uL)
        self._max_liquid_intake =  1 # upper limit of total liquid consumption (mL)

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
    def preference_trial_duration(self):
        """
        Duration of sucrose preferece in seconds
        
        :rtype: int
        """
        return self._preference_trial_duration

    @property
    def preference_trial_duration_minutes(self):
        """
        Duration of sucrose preference in minutes
        
        :rtype: int
        """
        return self._preference_trial_duration/60

    @property
    def num_preference_trial(self):
        """
        Number of sucrose preference trials
        
        :rtype: int
        """
        return self._num_preference_trials

    @property
    def preference_duration_total(self):
        """
        Total duration of sucrose preference in seconds

        :rtype: int
        """
        return self._num_preference_trials*self._preference_trial_duration

    @property
    def preference_duration_total(self):
        """
        Total duration of sucrose preference in minutes

        :rtype: int
        """
        return self._num_preference_trials*self._preference_trial_duration/60

    @property
    def single_lick_volume(self):
        """
        Volume of liquid release upon single lick in microliters

        :rtype: int
        """
        return self._single_lick_volume

    @property
    def max_liquid_intake(self):
        """
        Maximal intake of liquid permitted in milliliters

        :rtype: int
        """    
        return self._max_liquid_intake

    @property
    def number_of_licks_allowed(self):
        """
        Number of licks permitted before eaching maximum liquid intake

        :rtype: int
        """
        return self._max_liquid_intake*1000/self._single_lick_volume

    def validation(self):
        try:
            test_sucrose_preference_config(self)
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

    SPC = SucrosePreferenceConfig()
    print("".join(["MouseID: ", SPC.animal_id]))
    print("".join(["Base Directory: ", SPC.base_path]))
    print("".join(["Data Folder: ", SPC.data_path]))
    print("".join(["Habituation Duration: ", str(SPC.habituation_duration)]))
    print("".join(["Preference Duration: ", str(SPC.preference_duration)]))
    print("".join(["Number of Preference Trials: ", str(SPC.num_preference_trial)]))
    print("".join(["Lick Volume: ", str(SPC.single_lick_volume)]))
    print("".join(["Maximal Intake: ", str(SPC.max_liquid_intake)]))
    print("".join(["Configuration Validated: ", str(SPC.validated)]))
