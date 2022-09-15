import cv2 as cv
import numpy as np
from time import time
from threading import Thread
import imageio


class BehavCam(Thread):

    # Instance Factory for Behavioral Camera

    def __init__(self, deviceID, height, width, window_name):
        self.deviceID = deviceID
        self.height = height
        self.width = width
        self.window_name = window_name
        self.cam = None
        self.cam_started = False
        #
        self.is_recording_time = False
        self.shutdown_mode = False
        self.isTrial = False
        self.runFrames = []
        self.runFramesIDs = []
        self.video = []
        self.currentTrial = 1
        self.unsaved = bool(1)
        self.file_prefix = "C:\\Users\\YUSTE\\Desktop\\"
        self.filename1 = []
        self.filename2 = []
        self.filename3 = []
        self.bufferNum = []
        self.currentBuffer = []
        self.isRunning1 = False
        self.isRunning2 = False
        Thread.__init__(self)

    def run(self):
        while True:
            if not self.cam_started:
                # cv.namedWindow("Dingus", 0)
                cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
                self.cam = cv.VideoCapture(self.deviceID, cv.CAP_DSHOW)
                self.cam.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
                self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cam.set(cv.CAP_PROP_FPS, 30.0)
                self.cam.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                self.cam_started = True
            if self.cam_started:
                while(self.cam.isOpened()):
                    ret, frame = self.cam.read()
                    if ret == True:
                        if self.isRunning2:
                            cv.imshow(self.window_name, frame)
                            cv.waitKey(1) & 0xFF
                            if self.is_recording_time:
                                self.runFrames.append(frame)
                                self.runFramesIDs.append(self.currentTrial)
                                self.bufferNum.append(self.currentBuffer)
                        elif self.isRunning1:
                            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                            cv.imshow(self.window_name, frame)
                            cv.waitKey(1) & 0xFF
                            if self.is_recording_time:
                                self.runFrames.append(frame)
                                self.runFramesIDs.append(self.currentTrial)
                                self.bufferNum.append(self.currentBuffer)
                        elif self.shutdown_mode:
                            break
                    else:
                        break
                if self.shutdown_mode:
                    self.cam.release()
                    cv.waitKey(1) & 0xFF
                    # cv.destroyWindow(self.window_name)
                    cv.waitKey(1) & 0xFF
                    if self.unsaved:
                        self.unsaved = True
                        self.filename1 = self.file_prefix + "_Frame.npy"
                        self.filename2 = self.file_prefix + "_FramesIDS.npy"
                        self.filename3 = self.file_prefix + "_BufferIDs.npy"
                        np.save(self.filename3, self.bufferNum, allow_pickle=True)
                        print(self.window_name + "Buffer IDs Saved")
                        np.save(self.filename2, self.runFramesIDs, allow_pickle=True)
                        print(self.window_name + "Frames IDs Saved")
                        np.save(self.filename1, self.runFrames, allow_pickle=True)
                        print(self.window_name + "Frames Saved")
                        self.unsaved = False
                        return


if __name__ == '__main__':
    behavCam = BehavCam(1, 640, 480, "DARIK")
    behavCam.start()
    print("behavCam Instantiated")
