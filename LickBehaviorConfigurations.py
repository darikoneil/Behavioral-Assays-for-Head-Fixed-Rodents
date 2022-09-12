from os import mkdir, getcwd
from TypeCheck import test_burrow_preference_config


class BurrowPreferenceConfig:
    """
    Configuration File for Burrow Preference Task
    """
    def __init__(self):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "Darik"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\", self.animal_id])

        # Behavior Parameters
        self._habituation_duration = 5 # Habituation duration in seconds, integer
        self._behavior_duration = 5 # Burrow preference duration in seconds, integer

        # Make the data folder - SHOULD NOT EXIST
        try:
            mkdir(self.data_path)
        except FileExistsError:
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
    def behavior_duration(self):
        """
        Duration of behavior in seconds

        :rtype: int
        """
        return self._behavior_duration

    def validation(self):
        try:
            test_burrow_preference_config(self)
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

