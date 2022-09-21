import os
from time import time

from PyDAQmx import *
from DAQModules import DigitalGroupReader

from LickBehaviorConfigurations import SucrosePreferenceConfig
from HardwareConfiguration import HardConfig
from SaveModule import Saver, Pickler
from BehavioralCamera_Slave import BehavCam

import sys
from ctypes import byref
import numpy as np
from time import time

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
        self.wet_blocks = int(4)
        self.trial_intake = 5
        self.hold_advance = False
        self.unsaved = False

        self.running_sucrose_licks = 0
        self.running_water_licks = 0
        self.running_sucrose_rewards = 0
        self.running_water_rewards = 0
        self.running_intake = 0
        self.running_licks = 0
        self.running_trial_intake = 0
        self.training_started = False

        self.current_state = "Setup"
        self.current_spout = 0
        self.current_trial = 1
        self.current_trial_intake = 0
        self.current_trial_buffer = np.full((1, 100), 0, dtype=np.uint8)
        self.wet_string = "Wet Trial: "
        self.dry_string = "Dry Trial: "
        self.print_period = 10

        # Setup DAQ - General DAQ Parameters - Put into class because might be iterated on
        self.timeout = _hardware_config.timeout  # timeout parameter must be type floating 64 (units: seconds, double)
        self.samplingRate = _hardware_config.samplingRate  # DAQ sampling rate (units: Hz, integer)
        self.bufferTime = _hardware_config.bufferTime  # DAQ buffering time (units: ms, integer)
        self.buffersPerSecond = _hardware_config.buffersPerSecond  # DAQ buffers each second (units: Hz, round integer)
        # Samples per Buffer (units: samples, round integer) (Comment for below)
        self.bufferSize = _hardware_config.bufferSize
        self.totNumBuffers = int()  # integer record of number of buffers collected (running)

        # Setup DAQ - Device 1 - Instance Analog Inputs ( Multi-Channel Matrix with Single Grab )
        self.DAQAnalogInBuffer = np.tile(np.zeros((self.bufferSize,), dtype=np.float64),
                                         (_hardware_config.numAnalogIn, 1))
        self.numSamplesPerBlock = np.uint32(_hardware_config.numAnalogIn * self.bufferSize)
        self.voltageRangeIn = _hardware_config.analogVoltageRange
        self.units = int32()  # read units (type 32b integer, this implies default units)
        self.CreateAIVoltageChan(_hardware_config.analogChansIn, "Analog In", DAQmx_Val_RSE, self.voltageRangeIn[0],
                                 self.voltageRangeIn[1], DAQmx_Val_Volts, None)
        # RSE is reference single-ended, Val_Volts flags voltage units
        self.CfgSampClkTiming("", self.samplingRate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.bufferSize)
        # Val rising means on the rising edge, cont samps is continuous sampling
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.bufferSize, 0, name='EveryNCallback')
        # Callback every bufferSize over time = bufferSize*samplingRate
        self.AutoRegisterDoneEvent(0, name='DoneCallback')  # Flag Callback Executed

        # Setup DAQ - Device 1 - Instance Analog Output
        # | Motor Command
        self.motorVoltageRange = _hardware_config.motorVoltageRange  # Range of motor voltage (units: V, floating 64)
        self.motorOut = Task()  # Instance Analog Out Task Object
        self.motorOut.numSamples = int(1)  # Analog Out Length (units: samples, integer)
        self.motorOut.units = int32()  # units of analog out (units: Volts, signed 32b integer)
        self.motorOut.CreateAOVoltageChan(_hardware_config.motorChannel, "Motor Out", self.motorVoltageRange[0],
                                          self.motorVoltageRange[1], DAQmx_Val_Volts, None)

        # Setup Permissions
        self.permissions = Task()
        self.permissions.CreateDOChan("LickDAQ/port1/line0:1", "Permissions", DAQmx_Val_ChanForAllLines)

        # self.trialFlagger = Task()
        # self.trialFlagger.CreateDOChan(_hardware_config.trialFlaggerChannel, "Trial Flagger", DAQmx_Val_ChanForAllLines)


        # ID Important Input Channels for Reference during Analysis - Device 1
        self.imagingChannel = _hardware_config.imagingChannelInt
        self.gateChannel = _hardware_config.gateChannelInt
        self.propChannel = _hardware_config.propChannelInt

        # Setup DAQ - Device 3 - Instance Digital Outputs
        # | Lick Swapper Command
        # self.lickSwapper = Task()
        # self.lickSwapper.CreateDOChan(_hardware_config.lickSwapChannel, "Lick Swap Out", DAQmx_Val_ChanForAllLines)
        # | Sucrose Channel Command

        # Setup DAQ - Device 3 - Instance Digital Inputs
        # | Group Digital Reader

        # Setup DAQ - Device 3 - Data Buffers
        # self.lickingBuffer = self.LickingReader.readData.copy()

        # ID Important Input Channels for Reference during Analysis - Device 1
        self.rewardSucroseChannel = _hardware_config.deliveredSucroseChannel
        self.rewardWaterChannel = _hardware_config.deliveredWaterChannel
        self.lickedSucroseChannel = _hardware_config.lickedSucroseChannel
        self.lickedWaterChannel = _hardware_config.lickedWaterChannel

        # Setup DAQ - Device 3 - Instance Digital Inputs
        # | Attempted Sucrose Delivery
        self.rewardSucrose = Task()
        self.rewardSucrose.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.rewardSucrose.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.rewardSucrose.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.rewardSucrose.numSampsPerChan = np.int32(self.rewardSucrose.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.rewardSucrose.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.rewardSucrose.arraySizeInBytes = self.rewardSucrose.readData.__len__()
        self.rewardSucrose.CreateDIChan(_hardware_config.deliveredSucroseChannel, "Attempted Sucrose",
                                         DAQmx_Val_ChanForAllLines)
        # | Attempted Water Delivery
        self.rewardWater = Task()
        self.rewardWater.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.rewardWater.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.rewardWater.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.rewardWater.numSampsPerChan = np.int32(self.rewardWater.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.rewardWater.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.rewardWater.arraySizeInBytes = self.rewardWater.readData.__len__()
        self.rewardWater.CreateDIChan(_hardware_config.deliveredWaterChannel, "Attempted Water",
                                       DAQmx_Val_ChanForAllLines)
        # | Licked Sucrose
        self.lickedSucrose = Task()
        self.lickedSucrose.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.lickedSucrose.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.lickedSucrose.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.lickedSucrose.numSampsPerChan = np.int32(self.lickedSucrose.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.lickedSucrose.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.lickedSucrose.arraySizeInBytes = self.lickedSucrose.readData.__len__()
        self.lickedSucrose.CreateDIChan(_hardware_config.lickedSucroseChannel, "Licked Sucrose",
                                        DAQmx_Val_ChanForAllLines)
        # | Licked Water
        self.lickedWater = Task()
        self.lickedWater.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.lickedWater.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.lickedWater.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.lickedWater.numSampsPerChan = np.int32(self.lickedWater.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.lickedWater.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.lickedWater.arraySizeInBytes = self.lickedWater.readData.__len__()
        self.lickedWater.CreateDIChan(_hardware_config.lickedWaterChannel, "Licked Water", DAQmx_Val_ChanForAllLines)

        self.rewardSucroseChannel = _hardware_config.deliveredSucroseChannelInt
        self.rewardWaterChannel = _hardware_config.deliveredWaterChannelInt
        self.lickedSucroseChannel = _hardware_config.lickedSucroseChannelInt
        self.lickedWaterChannel = _hardware_config.lickedWaterChannelInt

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

        # self.master_camera = BehavCam(0, 640, 480, "CAM")
        # self.master_camera.file_prefix = "".join([self.sucrose_preference_config.data_path, "\\", "_cam1_"])
        # self.master_camera.isRunning2 = True
        # self.master_camera.start()

    def EveryNCallback(self):

        # Read Device 1 Analog Inputs
        self.ReadAnalogF64(self.bufferSize, self.timeout, DAQmx_Val_GroupByChannel, self.DAQAnalogInBuffer,
                           self.numSamplesPerBlock, byref(self.units), None)

        # Read Device 3 Digital Inputs
        # self.LickingReader.ReadSignals()

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

        # self.grabbedDigitalBuffer = self.LickingReader.readData.copy()
        # print(self.grabbedDigitalBuffer)
        # Count Total Buffers
        self.totNumBuffers += 1

        # Export
        self.bufferedAnalogDataToSave = np.append(self.bufferedAnalogDataToSave, self.grabbedAnalogBuffer, axis=1)
        self.bufferedStateToSave = np.append(self.bufferedStateToSave, self.current_state)
        self.bufferedDigitalDataToSave = np.append(self.bufferedDigitalDataToSave, self.grabbedDigitalBuffer, axis=1)

        if self.training_started:
            # Process Rewards
            if self.current_spout == 0:
                if self.process_rewards(self.grabbedDigitalBuffer[self.rewardWaterChannel, :], self.reward_duration_water):
                    self.current_trial_intake += 1
                    self.running_water_rewards += self.current_trial_intake
            elif self.current_spout == 1:
                if self.process_rewards(self.grabbedDigitalBuffer[self.rewardSucroseChannel, :], self.reward_duration_sucrose):
                    self.current_trial_intake += 1
                    self.running_sucrose_rewards += self.current_trial_intake


            self.running_intake = self.running_sucrose_rewards + self.running_water_rewards
            # Process Licks
            self.running_licks += np.sum(self.process_licks(self.grabbedDigitalBuffer[[self.lickedSucroseChannel,
                                                                                            self.lickedWaterChannel],
                                                            :]))

            # self.master_camera.currentTrial = self.current_trial
            # self.master_camera.currentBuffer = self.totNumBuffers -1

            # Check if finished
            if self.running_intake >= self.number_rewards_allowed:
                self.end_training()
            elif self.current_trial_intake >= self.trial_intake:
                self.current_trial += 1
                self.current_state = str(self.current_trial)
                self.current_trial_intake = 0
                self.current_trial_buffer = np.full((1, 100), 0, dtype=np.uint8)
                if self.current_spout == 0:
                    self.current_spout = 1
                    print("Swap Water")
                    self.sucroseDriver.WriteAnalogF64(self.sucroseDriver.numSamples, np.bool_(1),
                                         self.timeout, DAQmx_Val_GroupByChannel, np.array([4.999], dtype=np.float64),
                                         self.sucroseDriver.units, None)
                    self.waterDriver.WriteAnalogF64(self.waterDriver.numSamples, np.bool_(1),
                                         self.timeout, DAQmx_Val_GroupByChannel, np.array([0.001], dtype=np.float64),
                                         self.waterDriver.units, None)
                elif self.current_spout == 1:
                    self.current_spout = 0
                    print("Swap Sucrose")
                    self.sucroseDriver.WriteAnalogF64(self.sucroseDriver.numSamples, np.bool_(1),
                                         self.timeout, DAQmx_Val_GroupByChannel, np.array([0.001], dtype=np.float64),
                                         self.sucroseDriver.units, None)
                    self.waterDriver.WriteAnalogF64(self.waterDriver.numSamples, np.bool_(1),
                                         self.timeout, DAQmx_Val_GroupByChannel, np.array([4.999], dtype=np.float64),
                                         self.waterDriver.units, None)


        if self.totNumBuffers % self.print_period == 0:
            print("\n ----------------------------------")
            print("".join(["\nRunning Intake: ", str(self.running_intake), " rewards delivered", " and ", str(self.running_intake * self.single_lick_volume), " uL consumed"]))
            print("".join(["\nRunning Licks: ", str(self.running_licks)]))
            print("".join(["\nCurrent Trial: ", str(self.current_trial)]))
            print("".join(["\nRunning Trial Intake: ", str(self.current_trial_intake)]))
            print("\n ----------------------------------")
            #print(self.grabbedDigitalBuffer)

        return 0

    @staticmethod
    def DoneCallback(status):
        print("Status ", status.value)  # Not sure why we print but that's fine
        return 0

    def stopDAQ(self):
        # self.LickingReader.StopTask()
        self.waterDriver.StopTask()
        self.sucroseDriver.StopTask()
        self.lickSwapper.StopTask()
        self.gateTrigger.StopTask()
        self.gateOutDriver.StopTask()
        self.motorOut.StopTask()
        self.trialFlagger.StopTask()
        self.lickedWater.StopTask()
        self.lickedSucrose.StopTask()
        self.rewardWater.StopTask()
        self.rewardSucrose.StopTask()
        self.StopTask()

    def clearDAQ(self):
        # self.LickingReader.EndTask()
        self.lickedWater.StopTask()
        self.lickedWater.ClearTask()
        self.lickedSucrose.StopTask()
        self.lickedSucrose.ClearTask()
        self.rewardWater.StopTask()
        self.rewardWater.ClearTask()
        self.rewardSucrose.StopTask()
        self.rewardSucrose.ClearTask()
        self.waterDriver.StopTask()
        self.waterDriver.ClearTask()
        self.sucroseDriver.StopTask()
        self.sucroseDriver.ClearTask()
        self.lickSwapper.StopTask()
        self.lickSwapper.ClearTask()
        self.gateTrigger.StopTask()
        self.gateTrigger.ClearTask()
        self.gateOutDriver.StopTask()
        self.gateOutDriver.ClearTask()
        self.motorOut.StopTask()
        self.motorOut.ClearTask()
        self.trialFlagger.StopTask()
        self.trialFlagger.ClearTask()
        self.StopTask()
        self.ClearTask()

    def startAcquisition(self):
        self.StartTask() # Device 1 - Analog Inputs (Master Clock!!!)
        # Device 1 Analog Output
        self.motorOut.StartTask()
        # Device 3 Digital Input
        # self.LickingReader.BeginTask()
        self.rewardSucrose.StartTask()
        self.rewardWater.StartTask()
        self.lickedSucrose.StartTask()
        self.lickedWater.StartTask()
        # self.trialFlagger.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW

    def start_training(self):
        self.current_state = str(self.current_trial)
        self.training_started = True
        # self.master_camera.is_recording_time = True
        # self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None) # Write High
        # self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write Low

    def end_training(self):
        self.current_state = "End"
        # self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        # self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        print("\n Training Complete!\n")
        self.stopDAQ()
        self.save_data()
        while self.unsaved:
            continue
        print("\nData Saved\n")

    def save_data(self):
        self.unsaved = True
        print("Saving Analog Data...")
        self.save_module_analog.bufferedData = self.bufferedAnalogDataToSave.copy()
        _ = self.save_module_analog.timeToSave()

        print("Saving Digital Data...")
        self.save_module_digital.bufferedData = self.bufferedDigitalDataToSave.copy()
        _ = self.save_module_digital.timeToSave()

        print("Saving State Data...")
        self.save_module_state.bufferedData = self.bufferedStateToSave.copy()
        _ = self.save_module_state.timeToSave()

        print("Saving Config Data...")
        self.save_module_config.pickledPickles = self.sucrose_preference_config
        _ = self.save_module_config.timeToSave()

        print("Saving Camera...")
        self.master_camera.shutdown_mode = True
        self.master_camera.save_data()
        self.unsaved = False


    def swap_spouts(self):
        # if self.current_spout == 0:
            # self.current_spout = 1
            # print("Swap Water")
            # self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write Low
            # self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None) # Write High
        # elif self.current_spout == 1:
            # self.current_spout = 0
            #print("Swap Sucrose")
            # self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None)  # Write High
            # self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None) # Write High
        pass

    def advance_trial(self):
        self.hold_advance = True
        self.current_trial += 1
        self.current_state = str(self.current_trial)
        self.current_trial_intake = 0
        self.current_trial_buffer = np.full((1, 100), 0, dtype=np.uint8)
        self.swap_spouts()
        self.hold_advance = False

    @staticmethod
    def process_rewards(Data, RewardDuration):
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


if __name__ == "__main__":
    LT = DAQtoLickTraining()
    LT.startAcquisition()
    LT.start_training()
