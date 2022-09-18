from LickBehaviorConfigurations import SucrosePreferenceConfig
from threading import Thread
from transitions import Machine
from time import time


class SucrosePreferenceTask(Thread):
    def __init__(self, Config):
        # Passed from config; Don't reinitialize because it will re-shuffle the trial index
        _config = Config

        self.animal_id = _config.animal_id
        self.habituation_duration = _config.habituation_duration
        self.num_preference_trials = _config.num_preference_trials
        self.swap_index = _config.swap_index

        if _config.validated is False:
            print("Unable to initialize with invalid configuration!")
            return

        # Internal
        self.proceed_sync = False
        self.start_run = False
        self.stage_time = float()

        # Retract
        self.retract_start = float()
        self.retract_duration = 5
        self.retract_end = float()

        # Habituation
        self.hab_start = float()
        self.hab_end = float()

        # Release
        self.release_start = float()
        self.release_end = float()
        self.release_duration = 5

        # Preference Test
        self.pref_start = float()

        # Swapping
        self.swap_start = float()
        self.swap_end = float()
        self.swap_duration = 5

        # Rotating
        self.rotate_start = float()
        self.rotate_end = float()
        self.rotate_duration = 5

        # Deceiving
        self.deceive_start = float()
        self.deceive_end = float()
        self.deceive_duration = float()

        # Behavioral Flags
        self.habituation_complete = False
        self.preference_complete = False
        self.saving_complete = False

        self.states = ['Setup', 'Retract', 'Habituation', 'Release', 'PreferenceTest', 'Swapping', 'Rotating', 'Deceiving', 'Saving', 'End']

        self.transitions = [
            {'trigger': 'startBehavior', 'source': 'Setup', 'dest': 'Retract', 
            'before': 'initializeRetract', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduateRetraction', 'source': 'Retract', 'dest': 'Habituation',
             'before': 'initializeHabituation', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduateHabituation', 'source': 'Habituation', 'dest': 'Release',
             'before': 'initializeRelease', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduateRelease', 'source': 'Release', 'dest': 'PreferenceTest',
             'before': 'initializePreference', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduatePreference', 'source': 'PreferenceTest', 'dest': 'Swapping',
             'before': 'initializeSwapping', 'conditions': 'allowedToProceed'},
             {'trigger': 'swapping2Rotating', 'source': 'Swapping', 'dest': 'Rotating', 
             'before': 'initializeRotating', 'conditions': 'allowedToProceed'},
             {'trigger': 'swapping2Deceiving', 'source': 'Swapping', 'dest': 'Deceiving', 
             'before': 'initializeDeceiving', 'conditions': 'allowedToProceed'},
             {'trigger': 'rotating2Preference', 'source': 'Rotating', 'dest': 'PreferenceTest', 
             'before': 'initializePreference', 'conditions': 'allowedToProceed'},
             {'trigger': 'deceiving2Preference', 'source': 'Deceiving', 'dest': 'PreferenceTest', 
             'before': 'initializePreference', 'conditions': 'allowedToProceed'},
             {'trigger': 'swapping2Saving', 'source': 'Swapping', 'dest': 'Saving', 
             'conditions': 'allowedToProceed'},
            {'trigger': 'finishedSaving', 'source': 'Saving', 'dest': 'End'},
        ]

        Machine(model=self, states=self.states, transitions=self.transitions, initial='Setup')

        Thread.__init__(self)

    def run(self):
        while True:
            if self.state is 'Setup':
                if self.start_run:
                    # print("Transitioning from Setup to Retract\n")
                    self.startBehavior()
            elif self.state is 'Retract':
                self.stage_time = time()
                if self.checkStageTime(self.stage_time, self.retract_end):
                    # print("Transitioning from Retraction to Habituation\n")
                    self.graduateRetraction()
            elif self.state is 'Habituation':
                self.stage_time = time()
                if self.checkStageTime(self.stage_time, self.hab_end):
                    self.habituation_complete = True
                    # print("Transitioning from Habituation to Release\n")
                    self.graduateHabituation()
            elif self.state is 'Release':
                self.stage_time = time()
                if self.checkStageTime(self.stage_time, self.release_end):
                    # print("Transitioning from Release to Preference\n")
                    self.graduateRelease()
            elif self.state is 'PreferenceTest':
                self.stage_time = time()
                # print("Transitioning from Preference to Saving\n")
            elif self.state is 'Swapping':
                if self.checkStageTime(self.stage_time, self.swap_end):
                    if self.running_trial_index == self.num_preference_trials:
                        self.swapping2Saving()
                    elif self.swap_index[self.running_trial_index] == 1:
                        self.swapping2Rotating()
                    elif self.swap_index[self.running_trial_index] == 0:
                        self.swapping2Deceiving()
            elif self.state is 'Rotating':
                if self.checkStageTime(self.stage_time, self.rotate_end):
                    self.rotating2Preference()
            elif self.state is 'Deceiving':
                if self.checkStageTime(self.stage_time, self.deceive_end):
                    self.deceiving2Preference()
            elif self.state is 'Saving':
                if self.saving_complete:
                    # print("Transitioning from Saving to End\n")
                    self.finishedSaving()
            elif self.state is 'End':
                self.start_run = False
                # print("Ending...")
                return

    def allowedToProceed(self):
        return self.proceed_sync

    def initializeHabituation(self):
        self.hab_start = time()
        self.hab_end = self.hab_start + self.habituation_duration

    def initializePreference(self):
        self.pref_start = time()

    def initializeSwapping(self):
        self.running_trial_index += 1
        self.swap_start = time()
        self.swap_end = self.swap_start + self.swap_duration

    def initializeRotating(self):
        self.rotate_start = time()
        self.rotate_end = self.rotate_start + self.rotate_duration

    def initializeDeceiving(self):
        self.deceive_start = time()
        self.deceive_end = self.deceive_start + self.deceive_duration

    def initializeRetract(self):
        self.retract_start = time()
        self.retract_end = self.retract_start + self.retract_duration

    def initializeRelease(self):
        self.release_start = time()
        self.release_end = self.release_start + self.release_duration

    @staticmethod
    def checkStageTime(stagetime, stageend):
        if stagetime < stageend:
            return False
        else:
            return True


if __name__ == "__main__":
    from testing_utility_functions import load_pickle_from_file
    from os import getcwd
    BPT = SucrosePreferenceTask(load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"])))
    BPT.start_run = True
    BPT.proceed_sync = True
    BPT.saving_complete = True
    print("Sucrose Preference Task Instantiated\n")
    BPT.start()