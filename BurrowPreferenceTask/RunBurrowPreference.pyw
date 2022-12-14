from PyDAQmx import *

from PyQt6 import QtGui, QtCore, QtWidgets
from BurrowPreference_Real_GUI import Ui_MainWindow
from BurrowPreferenceMachine import BurrowPreferenceTask
from LickBehaviorConfigurations import BurrowPreferenceConfig
from GenericModules.BehavioralCamera_Master import BehavCamMaster
from Hardware.HardwareConfiguration import HardConfig
from GenericModules.SaveModule import Saver, Pickler

import sys
from ctypes import byref
import numpy as np
from time import time

import pyqtgraph as pg

global DAQmx_Val_RSE, DAQmx_Val_Volts, DAQmx_Val_Rising, DAQmx_Val_ContSamps, DAQmx_Val_Acquired_Into_Buffer
global DAQmx_Val_GroupByScanNumber, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines, DAQmx_Val_OnDemand
global DAQmx_Val_ChanPerLine  # These are globals for the DAQ Interface & all globals are scary!


class DAQtoBurrow(Task):
    """
    Instance Factory for DAQ to Burrow interface
    """
    def __init__(self, *args):
        Task.__init__(self)

        # internal variables
        self.current_state = "Dummy"
        self.cameras_on = False
        self.task_percentage = 0
        self.progress_period = 1

        # Indicators for States
        self.habituation_complete = False
        self.preference_complete = False
        self.saving_complete = False
        self.behavior_complete = False

        # Import Burrow Preference Configuration
        if args:
            self.burrow_preference_config = BurrowPreferenceConfig(args[0])
        else:
            self.burrow_preference_config = BurrowPreferenceConfig()

        # Import Hardware Configuration
        _hardware_config = HardConfig()
        
        # Instance Behavior
        self.burrow_preference_machine = BurrowPreferenceTask()
        
        # Setup DAQ - General DAQ Parameters - Put into class because might be iterated on
        self.timeout = _hardware_config.timeout  # timeout parameter must be type floating 64 (units: seconds, double)
        self.sampling_rate = _hardware_config.sampling_rate  # DAQ sampling rate (units: Hz, integer)
        self.buffer_time = _hardware_config.buffer_time  # DAQ buffering time (units: ms, integer)
        self.buffers_per_second = _hardware_config.buffers_per_second  # DAQ buffers each second (units: Hz, round integer)
        # Samples per Buffer (units: samples, round integer) (Comment for below)
        self.buffer_size = _hardware_config.buffer_size
        self.totNumBuffers = int() # integer record of number of buffers collected (running)

        # Setup DAQ - Device 1 - Instance Analog Inputs ( Multi-Channel Matrix with Single Grab )
        self.DAQAnalogInBuffer = np.tile(np.zeros((self.buffer_size,), dtype=np.float64), (_hardware_config.num_analog_in, 1))
        self.numSamplesPerBlock = np.uint32(_hardware_config.num_analog_in * self.buffer_size)
        self.voltageRangeIn = _hardware_config.analog_voltage_range
        self.units = int32()  # read units (type 32b integer, this implies default units)
        self.CreateAIVoltageChan(_hardware_config.analog_chans_in, "Analog In", DAQmx_Val_RSE, self.voltageRangeIn[0],
                                 self.voltageRangeIn[1], DAQmx_Val_Volts, None)
        # RSE is reference single-ended, Val_Volts flags voltage units
        self.CfgSampClkTiming("", self.sampling_rate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.buffer_size)
        # Val rising means on the rising edge, cont samps is continuous sampling
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.buffer_size, 0, name='EveryNCallback')
        # Callback every buffer_size over time = buffer_size*sampling_rate
        self.AutoRegisterDoneEvent(0, name='DoneCallback')  # Flag Callback Executed

        # Setup DAQ - Device 1 - Instance Analog Output
        # | Motor Command
        self.motor_voltage_range = _hardware_config.motor_voltage_range  # Range of motor voltage (units: V, floating 64)
        self.motorOut = Task()  # Instance Analog Out Task Object
        self.motorOut.numSamples = int(1)  # Analog Out Length (units: samples, integer)
        self.motorOut.units = int32()  # units of analog out (units: Volts, signed 32b integer)
        self.motorOut.CreateAOVoltageChan(_hardware_config.motor_channel, "Motor Out", self.motor_voltage_range[0],
                                          self.motor_voltage_range[1], DAQmx_Val_Volts, None)

        # Setup DAQ - Device 1 - Instance Digital Outputs
        # | Gate Out Driver (For Open Collector)
        self.gateOutDriver = Task()
        self.gateOutDriver.CreateDOChan(_hardware_config.gate_driver_channel_name, "Gate Drive Out", DAQmx_Val_ChanForAllLines)

        self.trialFlagger = Task()
        self.trialFlagger.CreateDOChan(_hardware_config.trial_channel_name, "Trial Flagger", DAQmx_Val_ChanForAllLines)

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
        self.gateTrigger.CreateDIChan(_hardware_config.gate_triggered_channel_name, "Gate In", DAQmx_Val_ChanForAllLines)

        # Setup Data Buffer Variables - Device 1
        # Passed Data Variables: It's better to LEAVE a buffer unread and skip it than to error out of a trial
        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()  # Single Grab of Analog Data
        self.grabbedGateTriggerBuffer = self.gateTrigger.readData.copy()  # Single Grab of Digital Data

        # ID Important Input Channels for Reference during Analysis - Device 1
        self.imagingChannel = _hardware_config.imaging_sync_channel_id
        self.gateChannel = _hardware_config.gate_triggered_channel_id
        self.propChannel = _hardware_config.motor_pos_channel_id

        # Prep Data Buffers
        self.bufferedAnalogDataToSave = np.array(self.DAQAnalogInBuffer.copy(), dtype=np.float64)
        self.bufferedDigitalDataToSave = np.array(self.gateTrigger.readData.copy(), dtype=np.uint8)
        self.bufferedStateToSave = np.array(['0'], dtype=str)

        # DAQ Callback Tracking (usually commented out)
        self.daq_catch_times = []
        self.daq_catch_times_saver = Saver()
        self.daq_catch_times_saver.filename = self.burrow_preference_config.data_path + "\\daq_catch_times.npy"

        self.save_module_analog = Saver()
        self.save_module_analog.filename = self.burrow_preference_config.data_path + "\\analog.npy"
        self.save_module_state = Saver()
        self.save_module_state.filename = self.burrow_preference_config.data_path + "\\state.npy"
        self.save_module_digital = Saver()
        self.save_module_digital.filename = self.burrow_preference_config.data_path + "\\digital.npy"
        self.save_module_config = Pickler()
        self.save_module_config.filename = self.burrow_preference_config.data_path + "\\behavior_config"

        # We don't care enough let's just keep the attribute space clean for coding purposes
        _save_module_hardware = Pickler()
        _save_module_hardware.filename = self.burrow_preference_config.data_path + "\\hardware_config"
        _save_module_hardware.pickledPickles = _hardware_config
        _ = _save_module_hardware.timeToSave()

        # Cameras
        self.master_camera = BehavCamMaster()

    def EveryNCallback(self):
        self.burrow_preference_machine.proceed_sync = True

        # _start_time = time()

        # Read Device 1 Analog Inputs
        self.ReadAnalogF64(self.buffer_size, self.timeout, DAQmx_Val_GroupByChannel, self.DAQAnalogInBuffer,
                           self.numSamplesPerBlock, byref(self.units), None)

        self.grabbedAnalogBuffer = self.DAQAnalogInBuffer.copy()  # Grab the buffer now and make NI drivers happy if we have any lags

        # Read Device 1 Digital Inputs
        self.gateTrigger.ReadDigitalLines(self.gateTrigger.numSampsPerChan, self.timeout, self.gateTrigger.fillMode,
                                          self.gateTrigger.readData, self.gateTrigger.arraySizeInBytes,
                                          self.gateTrigger.sampsPerChanRead, byref(self.gateTrigger.numBytesPerSamp),
                                          None)

        self.grabbedGateTriggerBuffer = self.gateTrigger.readData.copy()
        self.process_gate_sensor()

        # Count Total Buffers
        self.totNumBuffers += 1

        # Parse States

        if self.current_state != self.burrow_preference_machine.state:
            self.current_state = self.burrow_preference_machine.state
            self.update_behavior()

            if self.current_state == "Saving":
                myapp.updateStateSignals.emit()
                self.save_data()
                self.burrow_preference_machine.saving_complete = True
                while self.burrow_preference_machine.state != "End":
                    continue
                self.behavior_complete = True
                self.current_state = self.burrow_preference_machine.state
                self.update_behavior()
                myapp.updateStateSignals.emit()
                myapp.update_progress_bar.emit()
                self.stopDAQ()

            if self.current_state == "End":
                self.behavior_complete = True

            myapp.updateStateSignals.emit()

        self.bufferedAnalogDataToSave = np.append(self.bufferedAnalogDataToSave, self.grabbedAnalogBuffer, axis=1)
        self.bufferedStateToSave = np.append(self.bufferedStateToSave, self.current_state)
        self.bufferedDigitalDataToSave = np.append(self.bufferedDigitalDataToSave, self.grabbedGateTriggerBuffer, axis=0)

        # Determine if updating progress bar
        if (self.totNumBuffers % self.progress_period) == 0:
            if self.current_state == "Habituation":
                self.task_percentage = self.calculate_percentage_complete(self.burrow_preference_machine.hab_start,
                                                                          self.burrow_preference_machine.stage_time,
                                                                          self.burrow_preference_machine.hab_end)
            elif self.current_state == "PreferenceTest":
                self.task_percentage = self.calculate_percentage_complete(self.burrow_preference_machine.pref_start,
                                                                          self.burrow_preference_machine.stage_time,
                                                                          self.burrow_preference_machine.pref_end)
            else:
                pass
            myapp.update_progress_bar.emit()

        # _catch_time = (time()-_start_time)*1000
        # self.daq_catch_times.append(_catch_time)

        # print("".join(["This iteration was ", str(_catch_time), " milliseconds"]))

        # Record Camera Data
        if self.cameras_on:
            if self.master_camera.cam_1.is_recording_time != self.habituation_complete:
                self.master_camera.cam_1.is_recording_time = True
                self.master_camera.cam_2.is_recording_time = True

            self.master_camera.cam_1.currentTrial = self.current_state
            self.master_camera.cam_2.currentTrial = self.current_state
            self.master_camera.cam_1.currentBuffer = self.totNumBuffers-1
            self.master_camera.cam_2.currentBuffer = self.totNumBuffers-1

        # Throw Signals to GUI
        myapp.catchSignals.emit()

        self.burrow_preference_machine.proceed_sync = False

        return 0

    @staticmethod
    def DoneCallback(status):
        print("Status ", status.value) # Not sure why we print but that's fine
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

    def save_data(self):
        self.stopDAQ()
        self.burrow_preference_machine.state = "End"
        self.burrow_preference_machine.start_run = False
        self.task_percentage = 0
        myapp.update_progress_bar.emit()

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
        self.save_module_config.pickledPickles = self.burrow_preference_config
        _ = self.save_module_config.timeToSave()

        # Save DAQ Catch Times (usually commented out)
        print("Saving DAQ Catch Times...")
        self.daq_catch_times_saver.bufferedData = self.daq_catch_times
        _ = self.daq_catch_times_saver.timeToSave()

        if self.cameras_on:
            self.master_camera.cam_1.isRunning1 = False
            self.master_camera.cam_1.shutdown_mode = True
            self.master_camera.cam_2.isRunning2 = False
            self.master_camera.cam_2.shutdown_mode = True
            print("Saving Camera 1...")
            self.master_camera.cam_1.save_data()
            while self.master_camera.cam_1.unsaved:
                continue
            print("Saving Camera 2...")
            self.master_camera.cam_2.save_data()
            while self.master_camera.cam_2.unsaved:
                continue
            self.task_percentage = 100
        myapp.update_progress_bar.emit()

    def update_behavior(self):
        self.habituation_complete = self.burrow_preference_machine.habituation_complete
        self.preference_complete = self.burrow_preference_machine.preference_complete
        self.saving_complete = self.burrow_preference_machine.saving_complete

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

    def startBehavior(self):
        self.burrow_preference_machine.start()

    def process_gate_sensor(self):
        # dummy var to find the max & flip 0 to 1 // 1 to 0 (Hardware Open Collector Configuration)
        _gateData = np.array(self.grabbedGateTriggerBuffer)
        if int(abs(_gateData.max() - 1)) == 1:
            self.trialFlagger.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(5), None)
        else:
            self.trialFlagger.WriteDigitalScalarU32(np.bool_(1), np.float64(1), np.uint32(0), None)

    def startCamera(self):
        self.master_camera.start()
        self.master_camera.cam_1.file_prefix = "".join([self.burrow_preference_config.data_path, "\\", "_cam1_"])
        self.master_camera.cam_2.file_prefix = "".join([self.burrow_preference_config.data_path, "\\", "_cam2_"])
        self.cameras_on = True
        return

    def startAll(self):
        self.startCamera()
        self.startBehavior()
        self.burrow_preference_machine.start_run = True

    @staticmethod
    def calculate_percentage_complete(start, current, end):
        return ((current-start)/(end-start))*100


class MasterGUI(QtWidgets.QMainWindow):

    catchSignals = QtCore.pyqtSignal()
    drawSignals = QtCore.pyqtSignal()
    updateStateSignals = QtCore.pyqtSignal()
    update_progress_bar = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.catch_times = []

        # Connect Signal Throwers
        self.catchSignals.connect(self.catchingSignals)
        self.drawSignals.connect(self.drawingSignals)
        self.updateStateSignals.connect(self.updateBehavior)
        self.update_progress_bar.connect(self.updateProgressBars)

        # Instance DAQ
        self.DAQ = DAQtoBurrow()

        # Update State
        self.ui.currrent_stage_var.setText("Setup")

        # State Indicators
        self.habituation_complete = False
        self.preference_complete = False
        self.saving_complete = False

        # Set Parameters
        self.ui.mouse_id_var.setText(self.DAQ.burrow_preference_config.animal_id)
        self.ui.habituation_duration_var.setText("".join([str(
            self.DAQ.burrow_preference_config.habituation_duration_minutes), " Minutes"]))
        self.ui.preference_duration_var.setText("".join([str(
            self.DAQ.burrow_preference_config.behavior_duration_minutes), " Minutes"]))

        # Plotting Buffer Construction & Parameters
        self.plotPeriod = int(1)
        self.plottingRange = int(5000)  # Length of plotting x-axis (units: ms, integer)
        self.plottingSamples = int(round((self.plottingRange / 1000) * self.DAQ.sampling_rate))
        # Number of Samples in plots (units: samples, round integer)
        self.plottingIterations = int(self.plottingSamples / self.DAQ.buffer_size)  # number of grabs in one plot
        self.plottingIndex = int(self.plottingIterations - 1)  # Index for most recent data
        # Vector of time to plot on X-axis (below)
        self.plottingTimeVector = np.linspace(start=-self.plottingRange, stop=0, num=self.plottingSamples)
        self.plottingMotor = np.zeros(self.plottingSamples, dtype=np.float32)

        # for speed
        pg.setConfigOptions(antialias=False)

        # Motor Plot
        self.ui.MotorPlot.setBackground((255, 255, 255, 0))
        self.motor_plot_item = self.ui.MotorPlot.getPlotItem()
        self.motor_plot_item.setMouseEnabled(x=False, y=False)
        self.motor_plot_item.setRange(xRange=(-5000, 0), yRange=(0, 10), disableAutoRange=True)

        # Make Pen
        self._pen_ = pg.mkPen(color=(19, 159, 255))
        self.motor_data_item = self.motor_plot_item.plot([], pen=self._pen_)

        # Connect Buttons
        self.ui.startButton.clicked.connect(self.startTask)
        self.ui.StartBehavior.clicked.connect(self.startBehavior)
        self.ui.StartCameras.clicked.connect(self.startCameras)
        self.ui.closeButton.clicked.connect(self.closeGUI)

        # Set Colors for Each GraphicsView Object
        self.RED = QtGui.QPalette()
        self.RED.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(255, 110, 110))
        self.GREEN = QtGui.QPalette()
        self.GREEN.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(64, 204, 138))

        # Set Graphics View Indicators to RED
        self.ui.behavior_indicator.setPalette(self.RED)
        self.ui.body_cam_indicator.setPalette(self.RED)
        self.ui.face_cam_indicator.setPalette(self.RED)
        self.ui.daq_indicator.setPalette(self.RED)
        self.ui.sync_image_indicator.setPalette(self.RED)
        self.ui.data_saved_indicator.setPalette(self.RED)

        # Initialize Motor Control
        self.ui.motor_controller.valueChanged.connect(self.moveMotor)

        # Initiate DAQ Acquisition
        try:
            self.DAQ.startAcquisition()
            self.ui.daq_indicator.setPalette(self.GREEN)
        except DAQException or DAQError or DAQWarning or AttributeError or RuntimeError or ReferenceError:
            self.ui.daq_indicator.setPalette(self.RED)
            print("ERROR INITIATING DATA ACQUISITION!!!")

    def catchingSignals(self):
        _start_catch = time()

        # index for adding recent data
        _indexLong = [self.plottingIndex*self.DAQ.buffer_size, self.plottingIndex*self.DAQ.buffer_size+self.DAQ.buffer_size]

        self.plottingMotor = np.roll(self.plottingMotor, -self.DAQ.buffer_size)

        self.plottingMotor[_indexLong[0]:_indexLong[1]] = self.DAQ.grabbedAnalogBuffer[self.DAQ.propChannel, ]

        if self.DAQ.totNumBuffers % self.plotPeriod == 0:    # Determine if we're going to plot this iteration
            # self.drawSignals.emit()  # Throw signals to plotting!
            pass

        # Sanity Check on Signal Processing/Loop Time
        _timeToCatch = (time()-_start_catch)*1000

        self.catch_times.append(_timeToCatch)

        if(self.DAQ.buffer_time/2) < _timeToCatch:
            print("Signals are being acquired faster than they can be caught")
            print("Time to catch: ", _timeToCatch)
            print("Buffer Length: ", self.DAQ.buffer_time)

    def drawingSignals(self):
        self.updatePlots()

    def updatePlots(self):
        self.motor_data_item.setData(self.plottingTimeVector, self.plottingMotor)

    def updateBehavior(self):
        self.ui.currrent_stage_var.setText(self.DAQ.current_state)

        if self.DAQ.current_state == "Retract":
            self.retractMotor()

        if self.DAQ.current_state == "Release":
            self.releaseMotor()

        if self.saving_complete != self.DAQ.saving_complete:
            self.ui.data_saved_indicator.setPalette(self.GREEN)
            self.saving_complete = True

        self.checkImagingSync()

    def updateProgressBars(self):
        self.ui.behavioral_progress_bar.setValue(self.DAQ.task_percentage)

    def checkImagingSync(self):
        if self.DAQ.grabbedAnalogBuffer[0, ].max() > 1:
            self.ui.sync_image_indicator.setPalette(self.GREEN)
        else:
            self.ui.sync_image_indicator.setPalette(self.RED)

    def startTask(self):
        self.DAQ.burrow_preference_machine.start_run = True

    # noinspection PyBroadException
    def startBehavior(self):
        try:
            self.DAQ.startBehavior()
            self.ui.behavior_indicator.setPalette(self.GREEN)
        except Exception:
            self.ui.behavior_indicator.setPalette(self.RED)
            print("Behavioral Machine could not be initiated!!!")

    # noinspection PyBroadException
    def startCameras(self):
        try:
            self.DAQ.startCamera()
            self.ui.body_cam_indicator.setPalette(self.GREEN)
            self.ui.face_cam_indicator.setPalette(self.GREEN)
        except Exception:
            self.ui.body_cam_indicator.setPalette(self.RED)
            self.ui.face_cam_indicator.setPalette(self.RED)
            print("Unable to start cameras!!!")

    def closeGUI(self):
        try:
            np.save("C:\\ProgramData\\Anaconda3\\envs\\LickingBehavior\\catches.npy", self.catch_time, allow_pickle=True)
        except AttributeError:
            pass
        self.DAQ.clearDAQ()
        self.close()
        return

    def retractMotor(self):
        self.ui.motor_controller.setValue(0)

    def releaseMotor(self):
        self.ui.motor_controller.setValue(100)

    def moveMotor(self):
        _sliderValue = np.float64(self.ui.motor_controller.value()*(self.DAQ.motor_voltage_range[1]/self.ui.motor_controller.maximum()))
        self.DAQ.motorOut.WriteAnalogF64(self.DAQ.motorOut.numSamples, np.bool_(1),
                                         self.DAQ.timeout, DAQmx_Val_GroupByChannel, np.array([_sliderValue]),
                                         self.DAQ.motorOut.units, None)


# Execute if Main Module
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MasterGUI()
    myapp.show()
    sys.exit(app.exec())
