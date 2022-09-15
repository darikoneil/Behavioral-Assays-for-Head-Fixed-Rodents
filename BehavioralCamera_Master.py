import numpy as np
import cv2 as cv
from time import time
from threading import Thread
import imageio
from BehavioralCamera_Slave import BehavCam


class BehavCamMaster:
    def __init__(self):
        self.device_id_1 = 0
        self.device_id_2 = 1
        self.height_1 = 720
        self.height_2 = 480
        self.width_1 = 1280
        self.width_2 = 640
        self.cam_1 = None
        self.cam_2 = None
        self.cam_1_started = False
        self.cam_2_started = False

    def start(self):
        if not self.cam_1_started:
            self.cam_1 = BehavCam(self.device_id_1, self.height_1, self.width_1, "CAM1")
            self.cam_1.isRunning1 = True
            self.cam_1.start()

        if not self.cam_2_started:
            self.cam_2 = BehavCam(self.device_id_2, self.height_2, self.width_2, "CAM2")
            self.cam_2.isRunning2 = True
            self.cam_2.start()



if __name__ == '__main__':
    BC = BehavCamMaster()
    BC.start()
