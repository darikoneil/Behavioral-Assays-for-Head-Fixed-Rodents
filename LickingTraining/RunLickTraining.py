import numpy as np
from ctypes import byref
from PyDAQmx import *
from GenericModules.DAQModules import DigitalGroupReader
from LickBehaviorConfigurations import SucrosePreferenceConfig
from HardwareConfiguration import HardConfig
from GenericModules.SaveModule import Saver, Pickler
from GenericModules.BehavioralCamera_Slave import BehavCam

global DAQmx_Val_RSE, DAQmx_Val_Volts, DAQmx_Val_Rising, DAQmx_Val_ContSamps, DAQmx_Val_Acquired_Into_Buffer
global DAQmx_Val_GroupByScanNumber, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines, DAQmx_Val_OnDemand
global DAQmx_Val_ChanPerLine  # These are globals for the DAQ Interface & all globals are scary!


class DAQtoLickTraining(Task):
    def __init__(self, *args):
        Task.__init__(self)

        _hardware_config = HardConfig()

        if args:
            self.sucrose_preference_config = args[0]
        else:
            self.sucrose_preference_config = SucrosePreferenceConfig()

        # User Parameters
        self.cameras_on = False
        self.print_period = 10

        # Training Parameters
        self.animal_id = self.sucrose_preference_config.animal_id
        self.single_lick_volume = self.sucrose_preference_config.single_lick_volume
        self.total_rewards_allowed = self.sucrose_preference_config.total_rewards_allowed
        self.trial_rewards_limit = self.sucrose_preference_config.licks_per_trial

        # Training Flags
        self.current_state = "Setup"
        self.current_trial = 0
        self.current_trial_rewards = 0
        self.current_spout = "Water" # or Sucrose
        self.training_started = False
        self.unsaved = True
        self.hold = False

        # Data holders
        self.running_licks = 0
        self.running_licks_water = 0
        self.running_licks_sucrose = 0
        self.running_water_rewards = 0
        self.running_sucrose_rewards = 0
        self.running_rewards = 0

        # Setup DAQ - General DAQ Parameters - Put into class because might be iterated on
        self.timeout = _hardware_config.timeout  # timeout parameter must be type floating 64 (units: seconds, double)
        self.sampling_rate = _hardware_config.sampling_rate  # DAQ sampling rate (units: Hz, integer)
        self.buffer_time = _hardware_config.buffer_time  # DAQ buffering time (units: ms, integer)
        self.buffers_per_second = _hardware_config.buffers_per_second # DAQ buffers each second (units: Hz, round integer)
        # Samples per Buffer (units: samples, round integer) (Comment for below)
        self.buffer_size = _hardware_config.buffer_size
        self.totNumBuffers = int()  # integer record of number of buffers collected (running)

        # Setup DAQ - Analog Input
        self.DAQAnalogInBuffer = np.tile(np.zeros((self.buffer_size,), dtype=np.float64),
                                         (_hardware_config.num_analog_in, 1))
        self.numSamplesPerBlock = np.uint32(_hardware_config.num_analog_in * self.buffer_size)
        self.voltage_range_in = _hardware_config.analog_voltage_range
        self.units = int32()  # read units (type 32b integer, this implies default units)
        self.CreateAIVoltageChan(_hardware_config.analog_chans_in, "Analog In", DAQmx_Val_RSE, self.voltage_range_in[0],
                                 self.voltage_range_in[1], DAQmx_Val_Volts, None)
        # RSE is reference single-ended, Val_Volts flags voltage units
        self.CfgSampClkTiming("", self.sampling_rate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.buffer_size)
        # Val rising means on the rising edge, cont samps is continuous sampling
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.buffer_size, 0, name='EveryNCallback')
        # Callback every buffer_size over time = buffer_size*sampling_rate
        self.AutoRegisterDoneEvent(0, name='DoneCallback')  # Flag Callback Executed

        # Setup DAQ - Digital Output
        self.permissions = Task()
        self.permissions.number_of_channels = _hardware_config.num_digital_out_port_1
        self.permissions.fill_mode = np.bool_(1)
        self.permissions.units = np.int32(1)
        self.permissions.timeout = self.timeout
        self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
        self.permissions.CreateDOChan(_hardware_config.digital_chans_out_port_1, "Permissions", DAQmx_Val_ChanForAllLines)
        self.permissions_sucrose_channel_id = _hardware_config.permission_sucrose_channel_id
        self.permissions_water_channel_id = _hardware_config.permission_water_channel_id

        # Setup DAQ - Digital Input
        self.rewards_monitor = Task()
        self.rewards_monitor = DigitalGroupReader(_hardware_config.num_digital_in, _hardware_config.digital_chans_in,
                                                  _hardware_config.timeout, _hardware_config.buffer_size,
                                                  "Reward Monitor")
        self.water_reward_channel_id = _hardware_config.water_reward_channel_id
        self.sucrose_reward_channel_id = _hardware_config.sucrose_reward_channel_id
        self.licking_water_channel_id = _hardware_config.licking_water_channel_id
        self.licking_sucrose_channel_id = _hardware_config.licking_sucrose_channel_id

        # Prep Data Buffers
        self.bufferedAnalogDataToSave = np.array(self.DAQAnalogInBuffer.copy(), dtype=np.float64)
        self.bufferedDigitalDataToSave = np.full((_hardware_config.num_digital_in, self.buffer_size), 0, dtype=np.uint8)
        self.bufferedStateToSave = np.array(['0'], dtype=str)

        # Grabbed Digital Buffer
        self.grabbedDigitalBuffer = self.bufferedDigitalDataToSave.copy()
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()

        self.save_module_analog = Saver()
        self.save_module_analog.filename = self.sucrose_preference_config.data_path + "\\analog.npy"

        self.save_module_digital = Saver()
        self.save_module_digital.filename = self.sucrose_preference_config.data_path + "\\digital.npy"

        self.save_module_state = Saver()
        self.save_module_state.filename = self.sucrose_preference_config.data_path + "\\state.npy"

        self.save_module_config = Pickler()
        self.save_module_config.filename = self.sucrose_preference_config.data_path + "\\config"

        if self.cameras_on:
            self.master_camera = BehavCam(0, 640, 480, "CAM")
            self.master_camera.file_prefix = "".join([self.sucrose_preference_config.data_path, "\\", "_cam2_"])
            self.master_camera.isRunning2 = True
            self.master_camera.start()

    def EveryNCallback(self):

        # Read Device 1 Analog Inputs
        self.ReadAnalogF64(self.buffer_size, self.timeout, DAQmx_Val_GroupByChannel, self.DAQAnalogInBuffer,
                               self.numSamplesPerBlock, byref(self.units), None)

        # Grab the data
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()

        # Grab Digital Stuff
        self.rewards_monitor.ReadSignals()
        self.grabbedDigitalBuffer = self.rewards_monitor.readData.copy()

        # Update buffer count
        self.totNumBuffers += 1

        # Export
        self.bufferedAnalogDataToSave = np.append(self.bufferedAnalogDataToSave, self.grabbedAnalogBuffer, axis=1)
        self.bufferedStateToSave = np.append(self.bufferedStateToSave, self.current_state)
        self.bufferedDigitalDataToSave = np.append(self.bufferedDigitalDataToSave, self.grabbedDigitalBuffer, axis=1)
        if self.cameras_on:
            self.master_camera.currentTrial = self.current_trial
            self.master_camera.currentBuffer = self.totNumBuffers - 1

        # Process rewards if training started
        if self.training_started:
            # Process rewards...
            if self.current_spout == "Water":
                if self.process_rewards(self.grabbedDigitalBuffer[self.water_reward_channel_id, :]):
                    self.current_trial_rewards += 1
                    self.running_water_rewards += 1
            elif self.current_spout == "Sucrose":
                if self.process_rewards(self.grabbedDigitalBuffer[self.sucrose_reward_channel_id, :]):
                    self.current_trial_rewards += 1
                    self.running_sucrose_rewards += 1
        self.running_rewards = self.running_sucrose_rewards + self.running_water_rewards
        # Process licks...
        if self.process_licks(self.grabbedDigitalBuffer[self.licking_water_channel_id, :]):
            self.running_licks_water += 1
        if self.process_licks(self.grabbedDigitalBuffer[self.licking_sucrose_channel_id, :]):
            self.running_licks_sucrose += 1
        self.running_licks = self.running_licks_water + self.running_licks_sucrose

        # Check if this trial is finished or if this task is finished
        self.check_if_finished()

        # Report information to the console
        if self.totNumBuffers % self.print_period == 0:
            print("\n ----------------------------------")
            print("".join(["\nRunning Intake: ", str(self.running_rewards), " rewards delivered", " and ", str(self.running_rewards * self.single_lick_volume), " uL consumed"]))
            print("".join(["\nRunning Licks: ", str(self.running_licks)]))
            print("".join(["\nCurrent Trial: ", str(self.current_trial)]))
            print("".join(["\nRunning Trial Intake: ", str(self.current_trial_rewards)]))
            print("\n ----------------------------------")

        return 0

    @staticmethod
    def DoneCallback(status):
        print("Status ", status.value)  # Not sure why we print but that's fine
        return 0

    def startAcquisition(self):
        # Analog Inputs
        self.StartTask() # (Master Clock!!!)
        # Digital Output
        self.permissions.StartTask()
        # Digital Input
        self.rewards_monitor.StartTask()

    def clearDAQ(self):
        self.rewards_monitor.StopTask()
        self.rewards_monitor.ClearTask()
        self.permissions.StopTask()
        self.permissions.ClearTask()
        self.StopTask()
        self.ClearTask()

    def stopDAQ(self):
        self.rewards_monitor.StopTask()
        self.permissions.StopTask()
        self.StopTask()

    def end_training(self):
        self.current_state = "End"
        print("\n Training Complete!\n")
        self.stopDAQ()
        self.save_data()
        while self.unsaved:
            continue
        print("\nData Saved\n")

    def start_training(self):
        self.current_state = str(self.current_trial)
        self.training_started = True
        self.initialize_permission()

    def advance_trial(self):
        self.hold = True
        self.current_trial += 1
        self.current_state = str(self.current_trial)
        self.current_trial_rewards = 0
        self.swap_permission()
        self.hold = False

    def swap_permission(self):
        if self.current_spout == "Water":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[[self.permissions_water_channel_id, self.permissions_sucrose_channel_id]] = 0, 1
            self.permissions.WriteDigitalLines(self.permissions.fill_mode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
            self.current_spout = "Sucrose"
        elif self.current_spout == "Sucrose":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[[self.permissions_water_channel_id, self.permissions_sucrose_channel_id]] = 1, 0
            self.permissions.WriteDigitalLines(self.permissions.fill_mode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
            self.current_spout = "Water"
            
    def initialize_permission(self):
        if self.current_spout == "Water":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[[self.permissions_water_channel_id, self.permissions_sucrose_channel_id]] = 1, 0
            self.permissions.WriteDigitalLines(self.permissions.fill_mode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
        elif self.current_spout == "Sucrose":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[[self.permissions_water_channel_id, self.permissions_sucrose_channel_id]] = 0, 1
            self.permissions.WriteDigitalLines(self.permissions.fill_mode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)

    def check_if_finished(self):
        if self.running_rewards >= self.total_rewards_allowed:
            self.end_training()
        elif self.current_trial_rewards >= self.trial_rewards_limit:
            self.current_trial += 1
            self.current_state = str(self.current_trial)
            self.current_trial_rewards = 0
            self.swap_permission()

    def save_data(self):
        return

    @staticmethod
    def process_rewards(Data):
        if np.max(np.diff(Data)) > 0:
            return True
        else:
            return False

    @staticmethod
    def process_licks(Data):
        if np.max(np.diff(Data)) > 0:
            return True
        else:
            return False
