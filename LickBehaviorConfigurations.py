from os import mkdir, getcwd
from TestingModules.TypeCheck import test_burrow_preference_config


class BurrowPreferenceConfig:
    """
    Configuration File for Burrow Preference Task
    """
    def __init__(self, *args):
        # initialize validation flag
        self.validated = False

        # General Parameters (Protected with no single setters)
        self._animal_id = "ATest"
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
        self._animal_id = "Mouse Name"
        self._base_path = getcwd() # or manually enter a filepath
        self._data_path = "".join([self.base_path, "\\", self.animal_id])

        # Behavior Parameters
        self._habituation_duration = 5 # Habituation duration in seconds, integer
        self._single_lick_volume = 3.8 # liquid dispensed in response to single lick (uL)
        self._max_liquid_intake = 1 # upper limit of total liquid consumption (mL)
        self._licks_per_trial = 25 # Number of licks per trial
        self._reward_duration_water = 20.125 # ms
        self._reward_duration_sucrose = 18.5 # ms
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
        # self.validated = self.validation()

        # try:
        #     assert(self.validated is True)
        # except AssertionError:
            # print("Configuration could not be validated")
            # return
        # except AttributeError:
         #    return

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
    def single_lick_volume(self):
        """
        Volume of liquid release upon single lick in microliters

        :rtype: int
        """
        return self._single_lick_volume

    @property
    def single_lick_volume_mL(self):
        return self._single_lick_volume/1000

    @property
    def max_liquid_intake(self):
        """
        Maximal intake of liquid permitted in milliliters

        :rtype: int
        """    
        return self._max_liquid_intake

    @property
    def total_rewards_allowed(self):
        """
        Number of licks permitted before maximum liquid intake

        :rtype: int
        """
        return self._max_liquid_intake*1000/self._single_lick_volume

    # @property
    # def num_preference_trial(self):
    #     """
    #    Number of sucrose preference trials

    #   :rtype: int
    #   """
    #   return self.total_rewards_allowed/self._licks_per_trial

    @property
    def volume_per_trial(self):
        """
        Liquid dispensed per trial in uL

        :rtype: int
        """
        return self._licks_per_trial*self.single_lick_volume

    @property
    def licks_per_trial(self):
        """
        Number of licks per trial

        :rtype: int
        """
        return self._licks_per_trial

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


#  @property
   #  def swap_index(self):
      #   """
      #   Order for lick spout swapping
      #   """
      #   return self._swap_index

    # def validation(self):
      #   try:
         #    test_sucrose_preference_config(self)
        #    return True
      #   except RuntimeError:
      #       return False

   #  @staticmethod
   #  def generate_swap_order_shuffled(num_trials):
      #  """
     #   Generate order for lick spout swapping - shuffled

    #    :rtype: tuple
     #   """
     #  # swap_index = np.append(np.full(int(np.ceil(num_trials/2)), 1, dtype=int), np.full(int(np.floor(num_trials/2))))
     # #  np.random.shuffle(swap_index)
     # #  return tuple(swap_index.reshape(1, -1)[0])

    # @staticmethod
    # def generate_swap_order_psuedo_shuffle(num_trials):
    #    """
    #    Generate order for lick spout swapping - psuedo-shuffled
    #
    #    :rtype: tuple
     #   """
     #   _num_stages = int(np.floor(num_trials/2))
     #   _states = [0, 1]
     #   for i in range(_num_stages):
          #  random.shuffle(_states)
        #    swap_index.extend(_states)
    #    if len(swap_index) != num_trials:
     #       swap_index.extend(1)
    #    return tuple(swap_index)



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
    print("".join(["Licks Per Trial: ", str(SPC.licks_per_trial)]))
    print("".join(["Lick Volume: ", str(SPC.single_lick_volume)]))
    print("".join(["Maximal Intake: ", str(SPC.max_liquid_intake)]))
    print("".join(["Configuration Validated: ", str(SPC.validated)]))
    print("".join(["Total Rewards Allowed: ", str(SPC.total_rewards_allowed)]))
