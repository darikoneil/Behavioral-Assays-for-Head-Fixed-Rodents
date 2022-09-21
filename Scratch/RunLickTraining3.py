from PyDAQmx import *
from GenericModules.DAQModules import DigitalGroupReader

from LickBehaviorConfigurations import SucrosePreferenceConfig
from HardwareConfiguration import HardConfig
from GenericModules.SaveModule import Saver, Pickler
from GenericModules.BehavioralCamera_Slave import BehavCam

from ctypes import byref
import numpy as np

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

        # Training Parameters
        self.animal_id = self.sucrose_preference_config.animal_id
        self.single_lick_volume = self.sucrose_preference_config.single_lick_volume
        self.max_intake = self.sucrose_preference_config.max_liquid_intake
        self.total_rewards_allowed = self.sucrose_preference_config.total_rewards_allowed
        self.number_rewards_allowed = self.total_rewards_allowed
        self.reward_duration_sucrose = 18.5 # ms
        self.reward_duration_water = 20.125 # ms

        # Training Flags
        self.current_state = "Setup"
        self.current_trial = 0
        self.current_trial_intake = 0
        self.current_trial_buffer = None # Filled Later After Digital Input Instancing
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
        self.CfgSampClkTiming("", self.samplingRate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.buffer_size)
        # Val rising means on the rising edge, cont samps is continuous sampling
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.buffer_size, 0, name='EveryNCallback')
        # Callback every buffer_size over time = buffer_size*samplingRate
        self.AutoRegisterDoneEvent(0, name='DoneCallback')  # Flag Callback Executed

        # Setup DAQ - Digital Output
        self.permissions = Task()
        self.permissions.number_of_channels = _hardware_config.num_digital_out_port_1
        self.permissions.fill_mode = np.bool_(1)
        self.permissions.units = np.float64(1)
        self.permissions.timeout = self.timeout
        self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
        self.permissions.CreateDOChan(_hardware_config.digital_chans_out_port_1, "Permissions", DAQmx_Val_ChanForAllLines)
        self.permissions_sucrose_channel_id = int(1)
        self.permissions_water_channel_id = int(2)

        # Setup DAQ - Digital Input
        self.rewards_monitor = Task()
        self.rewards_monitor = DigitalGroupReader(_hardware_config.num_digital_in, _hardware_config.digital_chans_in,
                                                  _hardware_config.timeout, _hardware_config.buffer_size,
                                                  "Reward Monitor")

        # Prep Data Buffers
        self.bufferedAnalogDataToSave = np.array(self.DAQAnalogInBuffer.copy(), dtype=np.float64)
        self.bufferedDigitalDataToSave = np.full((4, self.bufferSize), 0, dtype=np.uint8)
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

        self.master_camera = BehavCam(0, 640, 480, "CAM")
        self.master_camera.file_prefix = "".join([self.sucrose_preference_config.data_path, "\\", "_cam2_"])
        self.master_camera.isRunning2 = True
        self.master_camera.start()

    def EveryNCallback(self):

        # Read Device 1 Analog Inputs
        self.ReadAnalogF64(self.bufferSize, self.timeout, DAQmx_Val_GroupByChannel, self.DAQAnalogInBuffer,
                               self.numSamplesPerBlock, byref(self.units), None)

        # Grab the data
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()


        # Grab Digital Stuff
        self.lickedWater.ReadDigitalLines(self.lickedWater.numSampsPerChan, self.timeout, self.lickedWater.fillMode,
                                          self.lickedWater.readData, self.lickedWater.arraySizeInBytes,
                                          self.lickedWater.sampsPerChanRead, byref(self.lickedWater.numBytesPerSamp),
                                          None)

        self.lickedSucrose.ReadDigitalLines(self.lickedSucrose.numSampsPerChan, self.timeout,
                                            self.lickedSucrose.fillMode,
                                            self.lickedSucrose.readData, self.lickedSucrose.arraySizeInBytes,
                                            self.lickedSucrose.sampsPerChanRead,
                                            byref(self.lickedSucrose.numBytesPerSamp), None)

        self.rewardWater.ReadDigitalLines(self.rewardWater.numSampsPerChan, self.timeout, self.rewardWater.fillMode,
                                          self.rewardWater.readData, self.rewardWater.arraySizeInBytes,
                                          self.rewardWater.sampsPerChanRead, byref(self.rewardWater.numBytesPerSamp),
                                          None)

        self.rewardSucrose.ReadDigitalLines(self.rewardSucrose.numSampsPerChan, self.timeout,
                                            self.rewardSucrose.fillMode,
                                            self.rewardSucrose.readData, self.rewardSucrose.arraySizeInBytes,
                                            self.rewardSucrose.sampsPerChanRead,
                                            byref(self.rewardSucrose.numBytesPerSamp), None)

        self.grabbedDigitalBuffer[self.lickedWaterChannel, :] = self.lickedWater.readData.copy()
        self.grabbedDigitalBuffer[self.lickedSucroseChannel, :] = self.lickedSucrose.readData.copy()
        self.grabbedDigitalBuffer[self.rewardWaterChannel, :] = self.rewardWater.readData.copy()
        self.grabbedDigitalBuffer[self.rewardSucroseChannel, :] = self.rewardSucrose.readData.copy()

        self.totNumBuffers += 1

        # Export
        self.bufferedAnalogDataToSave = np.append(self.bufferedAnalogDataToSave, self.grabbedAnalogBuffer, axis=1)
        self.bufferedStateToSave = np.append(self.bufferedStateToSave, self.current_state)
        self.bufferedDigitalDataToSave = np.append(self.bufferedDigitalDataToSave, self.grabbedDigitalBuffer, axis=1)
        self.master_camera.currentTrial = self.current_trial
        self.master_camera.currentBuffer = self.totNumBuffers - 1

        if self.training_started:
            # Process Rewards
            if self.current_spout == "Water":
                if self.process_rewards(self.grabbedDigitalBuffer[self.rewardWaterChannel, :]):
                    self.current_trial_intake += 1
                    self.running_water_rewards += self.current_trial_intake
            elif self.current_spout == "Sucrose":
                if self.process_rewards(self.grabbedDigitalBuffer[self.rewardSucroseChannel, :]):
                    self.current_trial_intake += 1
                    self.running_sucrose_rewards += self.current_trial_intake

        self.running_rewards = self.running_sucrose_rewards + self.running_water_rewards

        # Process Licks
        if self.process_licks(self.grabbedDigitalBuffer[self.rewardWaterChannel, :]):
            self.running_licks_water += 1

        if self.process_licks(self.grabbedDigitalBuffer[self.rewardSucroseChannel, :]):
            self.running_licks_sucrose += 1

        self.running_licks = self.running_licks_water + self.running_licks_sucrose

        # Check if finished
        self.check_if_finished()

        if self.totNumBuffers % self.print_period == 0:
            print("\n ----------------------------------")
            print("".join(["\nRunning Intake: ", str(self.running_intake), " rewards delivered", " and ", str(self.running_intake * self.single_lick_volume), " uL consumed"]))
            print("".join(["\nRunning Licks: ", str(self.running_licks)]))
            print("".join(["\nCurrent Trial: ", str(self.current_trial)]))
            print("".join(["\nRunning Trial Intake: ", str(self.current_trial_intake)]))
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
        self.rewardSucrose.StartTask()
        self.rewardWater.StartTask()
        self.lickedSucrose.StartTask()
        self.lickedWater.StartTask()

    def clearDAQ(self):
        self.lickedWater.StopTask()
        self.lickedWater.ClearTask()
        self.lickedSucrose.StopTask()
        self.lickedSucrose.ClearTask()
        self.rewardWater.StopTask()
        self.rewardWater.ClearTask()
        self.rewardSucrose.StopTask()
        self.rewardSucrose.ClearTask()
        self.StopTask()
        self.ClearTask()

    def stopDAQ(self):
        self.lickedWater.StopTask()
        self.lickedSucrose.StopTask()
        self.rewardWater.StopTask()
        self.rewardSucrose.StopTask()
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
        self.current_trial_intake = 0
        self.current_trial_buffer = np.full((1, 100), 0, dtype=np.uint8)
        self.swap_permission()
        self.hold = False

    def swap_permission(self):
        if self.current_spout == "Water":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[self.permissions_water_channel_id, self.permissions_sucrose_channel_id] = 0, 1
            self.permissions.WriteDigitalLines(self.permissions.fillMode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
            self.current_spout = "Sucrose"
        elif self.current_spout == "Sucrose":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[self.permissions_water_channel_id, self.permissions_sucrose_channel_id] = 1, 0
            self.permissions.WriteDigitalLines(self.permissions.fillMode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
            self.current_spout = "Water"
            
    def initialize_permission(self):
        if self.current_spout == "Water":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[self.permissions_water_channel_id, self.permissions_sucrose_channel_id] = 1, 0
            self.permissions.WriteDigitalLines(self.permissions.fillMode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)
        elif self.current_spout == "Sucrose":
            self.permissions.data = np.full(self.permissions.number_of_channels, 0, dtype=np.uint8)
            self.permissions.data[self.permissions_water_channel_id, self.permissions_sucrose_channel_id] = 0, 1
            self.permissions.WriteDigitalLines(self.permissions.fillMode, self.permissions.units,
                                               self.permissions.timeout, DAQmx_Val_GroupByChannel,
                                               self.permissions.data, None, None)

    def check_if_finished(self):
        if self.running_intake >= self.number_rewards_allowed:
            self.end_training()
        elif self.current_trial_intake >= self.trial_intake:
            self.current_trial += 1
            self.current_state = str(self.current_trial)
            self.current_trial_intake = 0
            self.current_trial_buffer = np.full((1, 100), 0, dtype=np.uint8)
            self.swap_permission()

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