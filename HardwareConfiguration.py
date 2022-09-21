import numpy as np


class HardConfig:
    """
    Configuration for Hardware in licking behaviors
    """
    def __init__(self):

        # Sampling Parameters
        self.timeout = np.float64(10)  # timeout parameter must be type floating 64 (units: seconds, double)
        self.sampling_rate = int(1000)  # DAQ sampling rate (units: Hz, integer)
        self.buffer_time = int(100)  # DAQ buffering time (units: ms, integer)

        # Analog Input Parameters -- Serves as the master clock
        self.analog_voltage_range = np.array([-10.0, 10.0], dtype=np.float64)
        self.num_analog_in = int(4)
        self.analog_chans_in = "BurrowDAQ/ai0:3"
        # Imaging Sync
        self.imaging_sync_channel_name = "BurrowDAQ/ai0"
        self.imaging_sync_channel_id = int(0)
        # Motor Position
        self.motor_pos_channel_name = "BurrowDAQ/ai1"
        self.motor_pos_channel_id = int(1)
        # Force Readout
        self.force_channel_name = "BurrowDAQ/ai2"
        self.force_channel_id = int(2)
        # Dummy Channel - Reserved for future use
        self.dummy_channel_name = "BurrowDAQ/ai3"
        self.dummy_channel_id = int(3)

        # Digital Input Parameters
        self.num_digital_in = int(5)
        self.digital_chans_in = "BurrowDAQ/port0/line0:4"
        # Gate Channel
        self.gate_triggered_channel_name = "BurrowDAQ/port0/line0"
        self.gate_triggered_channel_id = int(0)
        # Reward Sucrose
        self.sucrose_reward_channel_name = "BurrowDAQ/port0/line1"
        self.sucrose_reward_channel_id = int(1)
        # Reward Water
        self.water_reward_channel_name = "BurrowDAQ/port0/line2"
        self.water_reward_channel_id = int(2)
        # Licking Sucrose
        self.licking_sucrose_channel_name = "BurrowDAQ/port0/line3"
        self.licking_sucrose_channel_id = int(3)
        # Licking Water
        self.licking_water_channel_name = "BurrowDAQ/port0/line4"
        self.licking_water_channel_id = int(4)

        # Analog Outputs Parameters
        self.num_analog_out = int(2)
        self.analog_chans_out = "BurrowDAQ/ao0:1"
        # Motor Settings # Note the external motor power source is 12V
        self.motor_channel = "BurrowDAQ/ao0"
        self.motor_voltage_range = np.array([0.001, 4.999], dtype=np.float64)
        self.motor_physical_range = np.array([0, 100], dtype=np.float64)
        # UCS Settings
        self.ucs_out_range = np.array([0, 5], dtype=np.float64)
        self.ucs_channel = "BurrowDAQ/ao1"

        # Digital Outputs Parameters
        self.num_digital_out_port_0 = int(3)
        self.digital_chans_out_port_0 = "BurrowDAQ/port0/line5:7"
        self.num_digital_out_port_1 = int(4)
        self.digital_chans_out_port_1 = "BurrowDAQ/port1/line0:3"
        # Gate Driver
        self.gate_driver_channel_name = "BurrowDAQ/port0/line5"
        self.gate_driver_channel_id = int(5)
        # CS Indicator
        self.cs_channel_name = "BurrowDAQ/port0/line6"

        self.cs_channel_id = int(6)
        # Trial Indicator
        self.trial_channel_name = "BurrowDAQ/port0/line7"
        self.trial_channel_id = int(7)
        # Water Reward Permission
        self.permission_water_channel_name = "BurrowDAQ/port1/line0"
        self.permission_water_channel_id = int(0)
        # Sucrose Reward Permission
        self.permission_sucrose_channel_name = "BurrowDAQ/port1/line1"
        self.permission_sucrose_channel_id = int(1)
        # Swap Licking Spouts
        self.swap_lick_spouts_channel_name = "BurrowDAQ/port1/line2"
        self.swap_lick_spouts_channel_id = int(2)
        # Remove Licking Spouts
        self.remove_lick_spouts_channel_name = "BurrowDAQ/port1/line3"
        self.remove_lick_spots_channel_id = int(3)

    @property
    def buffer_size(self):
        """
        Samples per Buffer (units: samples, round integer) (Comment for below)

        :rtype: int
        """

        try:
            _buffer_size = self.sampling_rate//self.buffers_per_second
            assert(isinstance(_buffer_size, int))
            return _buffer_size
        except AssertionError:
            print("Buffer size must be a round integer!!!")
            return

    @property
    def buffers_per_second(self):
        """
        DAQ buffers each second (units: Hz, round integer)

        :rtype: int
        """
        try:
            _buffers_per_second = self.sampling_rate//self.buffer_time
            assert(isinstance(_buffers_per_second, int))
            return _buffers_per_second
        except AssertionError:
            print("Buffers per second must be a round integer!!!")
            return
