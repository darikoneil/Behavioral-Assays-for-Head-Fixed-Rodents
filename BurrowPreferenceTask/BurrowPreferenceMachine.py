from LickBehaviorConfigurations import BurrowPreferenceConfig
from threading import Thread
from transitions import Machine
from time import time


class BurrowPreferenceTask(Thread):
    def __init__(self, *args):
        # Passed from config
        if args:
            _config = args[0]
        else:
            _config = BurrowPreferenceConfig("pass")  # Folder will already exist since created in DAQ Step

        self.animal_id = _config.animal_id
        self.habituation_duration = _config.habituation_duration
        self.behavior_duration = _config.behavior_duration

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
        self.pref_end = float()

        # Behavioral Flags
        self.habituation_complete = False
        self.preference_complete = False
        self.saving_complete = False

        self.states = ['Setup', 'Retract', 'Habituation', 'Release', 'PreferenceTest', 'Saving', 'End']

        self.transitions = [
            {'trigger': 'startBehavior', 'source': 'Setup', 'dest': 'Retract', 'before': 'initializeRetract',
             'conditions': 'allowedToProceed'},
            {'trigger': 'graduateRetraction', 'source': 'Retract', 'dest': 'Habituation',
             'before': 'initializeHabituation', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduateHabituation', 'source': 'Habituation', 'dest': 'Release',
             'before': 'initializeRelease', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduateRelease', 'source': 'Release', 'dest': 'PreferenceTest',
             'before': 'initializePreference', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduatePreference', 'source': 'PreferenceTest', 'dest': 'Saving',
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
                if self.checkStageTime(self.stage_time, self.pref_end):
                    self.preference_complete = True
                    # print("Transitioning from Preference to Saving\n")
                    self.graduatePreference()
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
        self.pref_end = self.pref_start + self.behavior_duration

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
    from TestingModules.testing_utility_functions import load_pickle_from_file
    from os import getcwd
    BPT = BurrowPreferenceTask(load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_BPT.pkl"])))
    BPT.start_run = True
    BPT.proceed_sync = True
    BPT.saving_complete = True
    print("Burrow Preference Task Instantiated\n")
    BPT.start()
