import numpy as np


class HardConfig:
    """
    Configuration for Hardware in licking behaviors
    """
    def __init__(self):

        self.device_dictionary = {
            'Device1': 'NI USB-6001',
            'Device2': 'Arduino Due',
            'Device3': 'NI USB-6008',
            'Device4': 'NI USB-6001',
            'Device5': 'Arduino Uno'
        }

        # Device 2
        self.device_2_dictionary = {
            "Device 2 Ground A": "J4, Interfaces wit L293D HBridge",
            "Device 2 Ground B": "Sucrose Capacitive Touch Breakout, GND",
            "Device 2 Ground C": "Water Capacitive Touch Breakout, GND",
            "Device 2 5V Source A": "Sucrose Capacitive Touch Breakout, VDD",
            "Device 2 5V Source B": "Water Capacitive Touch Breakout, VDD",
            "Device 2 Digital Pin 7": "Sucrose Capacitive Touch Breakout, OUT",
            "Device 2 Digital Pin 6": "Water Capacitive Touch Breakout, OUT",
        }

        # Dev5
        self.device_5_dictionary = {
            "Dev5 Ground": "Dev4/ao1_gnd to Dev5 ground",
            "Dev5 5V Pin": "G14, Lick Swapper Power Supply",
            "Dev5 Ground 2": "H13, Lick Swapper Power Ground",
            "Dev5 Digital Pin 3": "F15, Lick Swapper Signal",
            "Dev5 Digital Pin 5": "Remover Swapper Signal",
        }

        # External Board
        self.external_board_dictionary = {
            "C3": "Jumper from L293D 1Y C3 to C12 to (Sucrose Solenoid)",
            "I6": "Jumper from L293D 4Y I6 to E14 to (Water Solenoid)",
            "B29": "Jumper from B29 to B30 to link 12V input grounds",
            "A4": "A4 L293D GND connects to IO 32 Digital Ground on Device 3",
            "J1": "J1 L293D VCC1 Logic Power connects to IO 31 5V Source on Device 3",
            "C28": "C28 to L293D VVC2 Power D8",
            "E28": "E28 to 12V Power",
            "E30": "E30 to 12V Ground B",
            "J13": "J13 to Lick Swapper Motor Ground",
            "J14": "J14 to Lick Swapper Motor Power",
            "J15": "J15 to Lick Swapper Motor Signal",
        }

        self.external_components_dictionary = {
            "Lick Spout Swapping Servo": "GWS PICO STD",
            "Capacitive Touch Breakouts": "AT42QT-1010",
            "HBridge": "L293D",
            "Solenoids": "Parker 003-0218-900",
        }

        # General DAQ Parameters
        self.timeout = np.float64(10)  # timeout parameter must be type floating 64 (units: seconds, double)
        self.samplingRate = int(1000)  # DAQ sampling rate (units: Hz, integer)
        self.bufferTime = int(100)  # DAQ buffering time (units: ms, integer)
        # noinspection PyTypeChecker
        self.buffersPerSecond = int(round(self.samplingRate/self.bufferTime))  # DAQ buffers each second (units: Hz, round integer)
        # Samples per Buffer (units: samples, round integer) (Comment for below)
        # noinspection PyTypeChecker
        self.bufferSize = int(round(self.samplingRate/self.buffersPerSecond))
        # Analog Voltage Range LIMITS (*NOTE*) (units: V, floating 64 (double))
        self.analogVoltageRange = np.array([-10, 10], dtype=np.float64)


        # Burrow Configuration

        # Motor Settings # Note the external motor power source is 12V
        self.motorPhysicalRange = np.array([0, 100], dtype=np.float64)
        self.motorVoltageRange = np.array([0.001, 4.999], dtype=np.float64)

        # UCS Settings
        self.ucsOutRange = np.array([0, 5], dtype=np.float64)

        # Analog Outputs - Burrow
        self.numAnalogOut = int(2)
        self.motorChannel = "Dev1/ao0"
        self.uCSChannel = "Dev1/ao1"
        self.analogChansOut = "Dev1/ao0:1"

        # Analog Inputs - Burrow
        self.numAnalogIn = int(2)
        self.imagingChannel = "Dev1/ai0"
        self.imagingChannelInt = int(0)
        self.propChannel = "Dev1/ai1"
        self.propChannelInt = int(1)
        self.analogChansIn = "Dev1/ai0:1"

        # Digital Outputs - Burrow
        self.numDigitalOut = int(3)  # number of digital out channels
        self.cSChannel = "Dev1/port0/line1"
        self.trialFlaggerChannel = "Dev1/port1/line2"
        self.digitalChansOut = "Dev1/port1/line0:2"
        self.gateOutDriveChannel = "Dev1/port1/line0"

        # Digital Inputs (format reflects maintainability)
        self.numDigitalIn = int(1)  # number of digital out channels
        self.gateChannel = "Dev1/port0/line3"
        self.digitalChansIn = "Dev1/port0/line3"
        self.gateChannelInt = int(0)  # For maintainability

        # Reward Configuration

        # Digital Outputs - Reward
        self.numDigitalOut_Reward = int(3)
        self.waterChannel = "Dev4/port1/line1" # Water H-bridge enable out to L293D 3,4EN, "G8"
        self.sucroseChannel = "Dev4/port1/line0" # Sucrose H-bridge enable out to L293D 1,2EN, "A1"
        self.lickSwapChannel = "Dev4/port1/line2" # Motor command out to Dev5 Digital Pin "7"

        # Digital Inputs - Lick-Swapper
        self.numDigitalIn_Reward = int(4)
        self.deliveredSucroseChannel = "Dev4/port0/line0" # Input from Device 2 Digital Pin "13"
        self.deliveredWaterChannel = "Dev4/port0/line1" # Input from Device 2 Digital Pin "12"
        self.lickedSucroseChannel = "Dev4/port0/line2" # Input from Device 2 Digital Pin "11"
        self.lickedWaterChannel = "Dev4/port0/line3" # Input from Device 2 Digital Pin "10"
        self.sucrose_calibration_pin = "Dev4/port0/line6" # Output to Device 2 Digital Pin "5"
        self.water_calibration_pin = "Dev4/port0/line7" # Output to Device 2 Digital Pin "4"
        self.lickedWaterChannelInt = int(3)
        self.lickedSucroseChannelInt = int(2)
        self.deliveredWaterChannelInt = int(1)
        self.deliveredSucroseChannelInt = int(0)
