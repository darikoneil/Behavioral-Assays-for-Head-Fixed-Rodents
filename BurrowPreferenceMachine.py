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
            _config = BurrowPreferenceConfig("pass") # Folder will already exist since created in DAQ Step

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

        # Habituation
        self.hab_start = float()
        self.hab_end = float()

        # Preference Test
        self.pref_start = float()
        self.pref_end = float()

        # Behavioral Flags
        self.habituation_complete = False
        self.preference_complete = False
        self.saving_complete = False

        self.states = ['Setup', 'Habituation', 'PreferenceTest', 'Saving', 'End']

        self.transitions = [
            {'trigger': 'startBehavior', 'source': 'Setup', 'dest': 'Habituation', 'before': 'initializeHabituation'},
            {'trigger': 'graduateHabituation', 'source': 'Habituation', 'dest': 'PreferenceTest', 'before': 'initializePreference', 'conditions': 'allowedToProceed'},
            {'trigger': 'graduatePreference', 'source': 'PreferenceTest', 'dest': 'Saving', 'conditions': 'allowedToProceed'},
            {'trigger': 'finishedSaving', 'source': 'Saving', 'dest': 'End'},
        ]

        Machine(model=self, states=self.states, transitions=self.transitions, initial='Setup')

        Thread.__init__(self)

    def start(self):
        while True:
            if self.state is 'Setup':
                if self.start_run:
                    print("Transitioning from Setup to Habituation\n")
                    self.startBehavior()
            elif self.state is 'Habituation':
                self.stage_time = time()
                if self.checkStageTime(self.stage_time, self.hab_end):
                    self.habituation_complete = True
                    print("Transitioning from Habituation to Preference\n")
                    self.graduateHabituation()
            elif self.state is 'PreferenceTest':
                self.stage_time = time()
                if self.checkStageTime(self.stage_time, self.pref_end):
                    self.preference_complete = True
                    print("Transitioning from Preference to Saving\n")
                    self.graduatePreference()
            elif self.state is 'Saving':
                if self.saving_complete:
                    print("Transitioning from Saving to End\n")
                    self.finishedSaving()
            elif self.state is 'End':
                self.start_run = False
                print("Ending...")
                return

    def allowedToProceed(self):
        return self.proceed_sync

    def initializeHabituation(self):
        self.hab_start = time()
        self.hab_end = self.hab_start + self.habituation_duration
        return

    def initializePreference(self):
        self.pref_start = time()
        self.pref_end = self.pref_start + self.behavior_duration
        return

    @staticmethod
    def checkStageTime(stagetime, stageend):
        if stagetime < stageend:
            return False
        else:
            return True


if __name__ == "__main__":
    BPT = BurrowPreferenceTask()
    BPT.start_run = True
    BPT.proceed_sync = True
    print("Burrow Preference Task Instantiated\n")
    BPT.start()
