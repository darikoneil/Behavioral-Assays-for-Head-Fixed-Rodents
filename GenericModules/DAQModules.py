import numpy as np
from PyDAQmx import *
from ctypes import byref

global DAQmx_Val_RSE, DAQmx_Val_Volts, DAQmx_Val_Rising, DAQmx_Val_ContSamps, DAQmx_Val_Acquired_Into_Buffer
global DAQmx_Val_GroupByScanNumber, DAQmx_Val_GroupByChannel, DAQmx_Val_ChanForAllLines, DAQmx_Val_OnDemand
global DAQmx_Val_ChanPerLine


class DigitalGroupReader(Task):
    """
    Read a group of digital inputs simultaneously
    """
    def __init__(self, NumberofChannels, StringIdentifier, Timeout, SamplesPerRead, ReaderName):
        Task.__init__(self)
        # Collect
        self.timeout = Timeout
        self.samples_per_read = SamplesPerRead
        self.reader_name = ReaderName
        self.num_channels = NumberofChannels
        self.use_channels = StringIdentifier

        # Defaults (Always)
        self.fillMode = np.bool_(0)
        self.sampsPerChanRead = int32(100)
        self.numBytesPerSamp = int32()

        # Derivations
        self.readData = np.full((self.num_channels, self.samples_per_read), 2, dtype=np.uint8)
        self.numSampsPerChan = np.int32(self.readData.shape[1])
        self.arraySizeInBytes = np.uint32(self.readData.shape[0]*self.readData.shape[1])

        self.CreateDIChan(self.use_channels, self.reader_name, DAQmx_Val_ChanPerLine)

    def ReadSignals(self):
        self.ReadDigitalLines(self.numSampsPerChan, self.timeout, self.fillMode, self.readData,
                              self.arraySizeInBytes, self.sampsPerChanRead,
                              byref(self.numBytesPerSamp), None)
        return 0
