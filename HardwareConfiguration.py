import numpy as np


class HardConfig:
    """
    Configuration for Hardware in licking behaviors
    """
    def __init__(self):
        # General DAQ Parameters
        self.timeout = np.float64(10)  # timeout parameter must be type floating 64 (units: seconds, double)
        self.samplingRate = int(1000)  # DAQ sampling rate (units: Hz, integer)
        self.bufferTime = int(100)  # DAQ buffering time (units: ms, integer)
        # noinspection PyTypeChecker
        self.buffersPerSecond = int(round(self.samplingRate/self.bufferTime))  # DAQ buffers each second (units: Hz, round integer)
        # Samples per Buffer (units: samples, round integer) (Comment for below)
        # noinspection PyTypeChecker
        self.bufferSize = int(round(self.samplingRate/self.buffersPerSecond))

        # Analog Outputs - Burrow
        self.numAnalogOut = int(2)
        self.motorChannel = "Dev1/ai0"
        self.uCSChannel = "Dev1/ao1"
        self.analogChansOut = "Dev1/ao0:1"

        # Analog Inputs
        self.numAnalogIn = int(2)
        self.imagingChannel = "Dev1/ai0"
        self.imagingChannelInt = int(0)

        # Digital Inputs (format reflects maintainability)
        self.numDigitalIn = int(1)  # number of digital out channels
        self.gateChannel = "Dev1/port0/line3"
        self.digitalChansIn = "Dev1/port0/line3"
        self.gateChannelInt = int(0)  # For maintainability

        # Digital Outputs - Burrow
        self.numDigitalOut = int(3)  # number of digital out channels
        self.cSChannel = "Dev1/port0/line1"
        self.trialFlaggerChannel = "Dev1/port1/line2"
        self.digitalChansOut = "Dev1/port1/line0:2"
        self.gateOutDriveChannel = "Dev1/port1/line0"

        # Digital Outputs - Lick-Swapper
        self.numDigitalOut_Swapper = int(3)
        self.lickSwap = "Dev3/port0/line0"
        self.waterChannel = "Dev1/port0/line0"
        self.sucroseChannel = "Dev1/port0/line1"

        # Digital Inputs - Lick-Swapper
        self.numDigitalIn_Swapper = int(2)
        self.lickedWaterChannel = "Dev1/port2/line2"
        self.lickedSucroseChannel = "Dev1/port2/line3"

        # Analog Voltage Range LIMITS (*NOTE*) (units: V, floating 64 (double))
        self.analogVoltageRange = np.array([-10, 10], dtype=np.float64)

        # Motor Settings # Note the external motor power is 12V
        self.motorPhysicalRange = np.array([0, 50], dtype=np.float64)
        self.motorVoltageRange = np.array([0.001, 4.999], dtype=np.float64)

        # UCS Settings
        self.ucsOutRange = np.array([0, 5], dtype=np.float64)

