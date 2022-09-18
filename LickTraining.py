import os
from time import time

from PyDAQmx import *

from LickBehaviorConfigurations import SucrosePreferenceConfig
from HardwareConfiguration import HardConfig
from SaveModule import Saver, Pickler

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

        self.sucrose_preference_config = SucrosePreferenceConfig()

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

        # Setup DAQ - Device 1 - Instance Digital Outputs
        # | Gate Out Driver (For Open Collector)
        self.gateOutDriver = Task()
        self.gateOutDriver.CreateDOChan(_hardware_config.gateOutDriveChannel, "Gate Drive Out",
                                        DAQmx_Val_ChanForAllLines)

        self.trialFlagger = Task()
        self.trialFlagger.CreateDOChan(_hardware_config.trialFlaggerChannel, "Trial Flagger", DAQmx_Val_ChanForAllLines)

        # Setup DAQ - Device 1 - Instance Digital Inputs
        # | Gate Trigger Input
        self.gateTrigger = Task()  # Instance Gate Trigger Digital In Task Object
        self.gateTrigger.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.gateTrigger.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.gateTrigger.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.gateTrigger.numSampsPerChan = np.int32(self.gateTrigger.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.gateTrigger.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.gateTrigger.arraySizeInBytes = self.gateTrigger.readData.__len__()
        self.gateTrigger.CreateDIChan(_hardware_config.gateChannel, "Gate In", DAQmx_Val_ChanForAllLines)

        # Setup Data Buffer Variables - Device 1
        # Passed Data Variables: It's better to LEAVE a buffer unread and skip it than to error out of a trial
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()  # Single Grab of Analog Data

        # ID Important Input Channels for Reference during Analysis - Device 1
        self.imagingChannel = _hardware_config.imagingChannelInt
        self.gateChannel = _hardware_config.gateChannelInt
        self.propChannel = _hardware_config.propChannelInt

        # Setup DAQ - Device 3 - Instance Digital Outputs
        # | Lick Swapper Command
        self.lickSwapper = Task()
        self.lickSwapper.CreateDOChan(_hardware_config.lickSwapChannel, "Lick Swap Out", DAQmx_Val_ChanForAllLines)
        # | Sucrose Channel Command
        self.sucroseDriver = Task()
        self.sucroseDriver.CreateDOChan(_hardware_config.sucroseChannel, "Sucrose Drive Out", DAQmx_Val_ChanForAllLines)
        # | Water Channel Command
        self.waterDriver = Task()
        self.waterDriver.CreateDOChan(_hardware_config.waterChannel, "Water Drive Out", DAQmx_Val_ChanForAllLines)

        # Setup DAQ - Device 3 - Instance Digital Inputs
        # | Attempted Sucrose Delivery
        self.attemptSucrose = Task()
        self.attemptSucrose.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.attemptSucrose.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.attemptSucrose.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.attemptSucrose.numSampsPerChan = np.int32(self.attemptSucrose.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.attemptSucrose.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.attemptSucrose.arraySizeInBytes = self.attemptSucrose.readData.__len__()
        self.attemptSucrose.CreateDIChan(_hardware_config.deliveredSucroseChannel, "Attempted Sucrose",
                                         DAQmx_Val_ChanForAllLines)
        # | Attempted Water Delivery
        self.attemptWater = Task()
        self.attemptWater.fillMode = np.bool_(1)  # Flag interleaved samples (32b boolean)
        self.attemptWater.sampsPerChanRead = int32()  # number of samples per channel (number of read datas per chan)
        self.attemptWater.readData = np.full(100, 0, dtype=np.uint8)  # unsigned 8b integer
        self.attemptWater.numSampsPerChan = np.int32(self.attemptWater.readData.__len__())  # samples per chan
        # (units: samples, signed 32b integer)
        self.attemptWater.numBytesPerSamp = int32()  # bytes per sample (signed 32b integer)
        # number of elements inn readArray that constitutes a sample per channel (signed 32b integer)
        self.attemptWater.arraySizeInBytes = self.attemptWater.readData.__len__()
        self.attemptWater.CreateDIChan(_hardware_config.deliveredWaterChannel, "Attempted Water",
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

        # Setup Data Buffer Variables - Device 3
        # Passed Data Variables: It's better to LEAVE a buffer unread and skip it than to error out of a trial
        self.attemptSucroseBuffer = self.attemptSucrose.readData.copy()  # Single Grab of Digital Data
        self.attemptWaterBuffer = self.attemptWater.readData.copy()  # Single Grab of Digital Data
        self.lickedSucroseBuffer = self.lickedSucrose.readData.copy()  # Single Grab of Digital Data
        self.lickedWaterBuffer = self.lickedWater.readData.copy()  # Single Grab of Digital Data

        # ID Important Input Channels for Reference during Analysis - Device 1
        self.attemptSucroseChannel = _hardware_config.deliveredSucroseChannel
        self.attemptWaterChannel = _hardware_config.deliveredWaterChannel
        self.lickedSucroseChannel = _hardware_config.lickedSucroseChannel
        self.lickedWaterChannel = _hardware_config.lickedWaterChannel

        # Prep Data Buffers
        self.bufferedAnalogDataToSave = np.array(self.DAQAnalogInBuffer.copy(), dtype=np.float64)
        self.bufferedDigitalDataToSave = np.full((4, 100), 0, dtype=np.uint8)
        self.bufferedStateToSave = np.array(['0'], dtype=str)

        # DAQ Callback Tracking (usually commented out)
        self.daq_catch_times = []
        self.daq_catch_times_saver = Saver()
        self.daq_catch_times_saver.filename = self.sucrose_preference_config.data_path + "\\daq_catch_times.npy"

        # Daq licking
        #self.grabbedWaterLickBuffer = self.lickedWater.readData.copy()
        #self.grabbedSucroseLickBuffer = self.lickedSucrose.readData.copy()
        #self.grabbedAttemptWaterBuffer = self.attemptWater.readData.copy()
        #self.grabbedAttemptSucroseBuffer = self.attemptSucrose.readData.copy()
        self.grabbedDigitalBuffer = self.bufferedDigitalDataToSave.copy()

        # STUFF FOR TRAINING
        self.sucrose_licks = 0
        self.water_licks = 0
        self.sucrose_attempt_delivery = 0
        self.water_attempt_delivery = 0
        self.running_intake = 0
        self.intake_goal = self.sucrose_preference_config.max_liquid_intake
        self.animal_id = self.sucrose_preference_config.animal_id
        self.single_intake = self.sucrose_preference_config.single_lick_volume_mL
        self.number_licks_allowed = self.sucrose_preference_config.total_licks_allowed
        self.reward_duration = 30 # ms
        self.current_state = "Setup"
        self.print_period = 50

        self.save_module_analog = Saver()
        self.save_module_analog.filename = self.sucrose_preference_config.data_path + "\\analog.npy"

        self.save_module_digital = Saver()
        self.save_module_digital.filename = self.sucrose_preference_config.data_path + "\\digital.npy"

        self.save_module_state = Saver()
        self.save_module_state.filename = self.sucrose_preference_config.data_path + "\\state.npy"

        self.save_module_config = Pickler()
        self.save_module_config.filename = self.sucrose_preference_config.data_path + "\\config"

        self.reward_duration_water = 14
        self.reward_duration_sucrose = 13

    def EveryNCallback(self):
        # Read Device 1 Analog Inputs

        self.ReadAnalogF64(self.bufferSize, self.timeout, DAQmx_Val_GroupByChannel, self.DAQAnalogInBuffer,
                           self.numSamplesPerBlock, byref(self.units), None)
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()  # Grab the buffer now and make NI drivers happy if we have any lags

        # Grab Digital Stuff
        self.grabbedDigitalBuffer[0, :] = self.lickedWater.ReadDigitalLines(self.lickedWater.numSampsPerChan, self.timeout, self.lickedWater.fillMode,
                                                                            self.lickedWater.readData, self.lickedWater.arraySizeInBytes,
                                                                            self.lickedWater.sampsPerChanRead, byref(self.lickedWater.numBytesPerSamp), None)

        self.grabbedDigitalBuffer[1, :] = self.lickedSucrose.ReadDigitalLines(self.lickedSucrose.numSampsPerChan, self.timeout, self.lickedSucrose.fillMode,
                                                                            self.lickedSucrose.readData, self.lickedSucrose.arraySizeInBytes,
                                                                            self.lickedSucrose.sampsPerChanRead, byref(self.lickedSucrose.numBytesPerSamp), None)

        self.grabbedDigitalBuffer[2, :] = self.attemptWater.ReadDigitalLines(self.attemptWater.numSampsPerChan, self.timeout, self.attemptWater.fillMode,
                                                                            self.attemptWater.readData, self.attemptWater.arraySizeInBytes,
                                                                            self.attemptWater.sampsPerChanRead, byref(self.attemptWater.numBytesPerSamp), None)

        self.grabbedDigitalBuffer[3, :] = self.attemptSucrose.ReadDigitalLines(self.attemptSucrose.numSampsPerChan, self.timeout, self.attemptSucrose.fillMode,
                                                                            self.attemptSucrose.readData, self.attemptSucrose.arraySizeInBytes,
                                                                            self.attemptSucrose.sampsPerChanRead, byref(self.attemptSucrose.numBytesPerSamp), None)

        # Count Total Buffers
        self.totNumBuffers += 1

        # Process Rewards
        self.running_intake += (self.process_deliveries_water(self.grabbedDigitalBuffer[2, :], self.reward_duration_water) +
                                self.process_deliveries_sucrose(self.grabbedDigitalBuffer[3, :], self.reward_duration_sucrose))

        # Check if finished
        if self.running_intake >= self.number_licks_allowed:
            self.end_training()

        if self.totNumBuffers % self.print_period == 0:
            print("".join(["\nRunning Intake: ", str(self.running_intake), " rewards delivered", " and ", str(self.running_intake * self.single_intake/1000), " mL consumed", "\n"]))

        # Export
        self.bufferedAnalogDataToSave = np.append(self.bufferedAnalogDataToSave, self.grabbedAnalogBuffer, axis=1)
        self.bufferedStateToSave = np.append(self.bufferedStateToSave, self.current_state)
        self.bufferedDigitalDataToSave = np.append(self.bufferedDigitalDataToSave, self.grabbedDigitalBuffer,
                                                   axis=0)
        #
        return 0

    @staticmethod
    def DoneCallback(status):
        print("Status ", status.value)  # Not sure why we print but that's fine
        return 0

    def stopDAQ(self):
        self.lickedWater.StopTask()
        self.lickedSucrose.StopTask()
        self.attemptWater.StopTask()
        self.attemptSucrose.StopTask()
        self.waterDriver.StopTask()
        self.sucroseDriver.StopTask()
        self.lickSwapper.StopTask()
        self.gateTrigger.StopTask()
        self.gateOutDriver.StopTask()
        self.motorOut.StopTask()
        self.trialFlagger.StopTask()
        self.StopTask()

    def clearDAQ(self):
        self.lickedWater.StopTask()
        self.lickedWater.ClearTask()
        self.lickedSucrose.StopTask()
        self.lickedSucrose.ClearTask()
        self.attemptWater.StopTask()
        self.attemptWater.ClearTask()
        self.attemptSucrose.StopTask()
        self.attemptSucrose.ClearTask()
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
        # Device 1 Digital Output
        self.gateOutDriver.StartTask()
        self.gateOutDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(1), None) # Write High
        # Device 1 Digital Input
        self.gateTrigger.StartTask()
        # Device 3 Digital Output
        self.lickSwapper.StartTask()
        self.lickSwapper.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        self.sucroseDriver.StartTask()
        self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        self.waterDriver.StartTask()
        self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        # Device 3 Digital Input
        self.attemptSucrose.StartTask()
        self.attemptWater.StartTask()
        self.lickedSucrose.StartTask()
        self.lickedWater.StartTask()
        self.trialFlagger.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW

    def start_training(self):
        self.current_state = "Training"
        self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None) # Write High
        self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None) # Write High

    def end_training(self):
        self.current_state = "End"
        self.waterDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        self.sucroseDriver.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None) # Write LOW
        print("\n Training Complete!\n")
        self.stopDAQ()
        self.save_data()
        print("\nData Saved\n")

    def save_data(self):
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

    @staticmethod
    def process_intake(DigitalBuffer, RewardDuration, VolumePerReward):
        _rewards_water = DAQtoLickTraining.process_deliveries(DigitalBuffer[2, :], RewardDuration)
        _rewards_sucrose = DAQtoLickTraining.process_deliveries(DigitalBuffer[3, :], RewardDuration)
        return DAQtoLickTraining.convert_deliveries_to_intake((_rewards_water+_rewards_sucrose), VolumePerReward)

    @staticmethod
    def convert_deliveries_to_intake(Rewards, VolumePerReward):
        return Rewards * VolumePerReward

    @staticmethod
    def process_deliveries(Data, RewardDuration):
        return np.floor((len(np.where(Data == 1)[0]))/RewardDuration)

    @staticmethod
    def process_deliveries_water(Data, RewardDuration):
        return np.floor(np.sum(Data)/RewardDuration)

    @staticmethod
    def process_deliveries_sucrose(Data, RewardDuration):
        return np.floor(np.sum(Data)/RewardDuration)


if __name__ == "__main__":
    LT = DAQtoLickTraining()
    LT.startAcquisition()
    LT.start_training()
