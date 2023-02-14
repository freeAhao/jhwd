from datetime import datetime
import json
import os
from tempfile import gettempdir
import time
from time import sleep

import numpy as np
import cv2 as cv
from model.Settings import Settings
from myutils.IMGutil import *
from model.ApexStatus import Status
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from myutils.QtUtils import message_info

class Recognizer(QObject):
    status = Status()
    start = pyqtSignal(bool)
    resolution = []
    resize_rate = 1
    boxs = {}

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy:int=10):
        super(Recognizer, self).__init__()
        self.qt_comunicate = qt_comunicate
        self.sleeptime = sleeptime
        self.accuracy = accuracy

        self.check_resolution()

        self.start.connect(self.rec)

        self.generate_config()
    
    def generate_config(self):
        if not os.path.exists((gettempdir()+"/x.lua").replace("\\","/")):
            self.status.write_config()

    def check_resolution(self):
        height, width, _ = full_screenshot(int(Settings().app_config["monitor"])).shape
        self.resolution = [width,height]
        filename  = Settings().resource_dir+"resolution/{}_{}.json".format(width,height)
        try:
            filename  = Settings().resource_dir+"resolution/{}_{}.json".format(width,height)
            with open(filename,"r") as f:
                self.boxs = json.load(f)
            monitor = get_screen_nums()[int(Settings().app_config["monitor"])]
            for k in self.boxs:
                point = self.boxs[k]
                newpoint = [point[0]+monitor["left"],point[1]+monitor["top"]]
                self.boxs[k] = newpoint
                self.boxs[k].extend(point[2:])
            self.resize_rate = float(height/1080)
        except FileNotFoundError as e:
            raise FileNotFoundError("不支持的分辨率{}x{}".format(width,height))

    @pyqtSlot(bool)
    def rec(self, run):
        self.run = run 
        while self.run:
            start_time = time.time()
            self.recognize()
            sleep(self.sleeptime)
            end_time = time.time()
            self.qt_comunicate.updateFPS.emit(round(1/(end_time-start_time))) if self.qt_comunicate else None

class WeaponRecoginzer(Recognizer):
    gun_list=[]
    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=5):
        super().__init__(qt_comunicate, sleeptime)
        self.accuracy=accuracy
        self.get_resources()

    def get_resources(self):
        self.gun_list={}
        for files in os.listdir(Settings().resource_dir+"gun/"):
            if not str(files).endswith(".png"):
                continue
            resource = Settings().resource_dir+"gun/"+str(files)
            template = cv.imread(resource)
            self.gun_list[resource] = template


    def isweapon_icon(self, cvimg):
        return round(np.sum(cvimg)/6311250*100)>=8

    def recognize(self):
        icon_width = self.boxs["weapon1"][2]
        icon_height = self.boxs["weapon1"][3]
        icon_scale = icon_width/icon_height
        icon_height = round(icon_height * self.resize_rate)
        icon_width = round(icon_height * icon_scale)

        box1 = (self.boxs["weapon1"][0],
                self.boxs["weapon1"][1],
                self.boxs["weapon1"][0] + icon_width,
                self.boxs["weapon1"][1] + icon_height)

        img1 = screenshot(box1)

        cvimg1 = screenshot_to_cv(img1)

        if self.resize_rate != 1:
            cvimg1 = resize_img(cvimg1,self.resize_rate)
        # cvimg1 = cv.medianBlur(cvimg1,1)
        blackwhite_img = to_black_white(cvimg1)

        finded1 = False

        # if self.isweapon_icon(blackwhite_img1):
        # finded1,weapon1,s1 = similarity(blackwhite_img, self.gun_list,self.accuracy,False)
        finded1,weapon1,s1 = cv_match(blackwhite_img, self.gun_list,self.accuracy)

        if finded1:
            d = {"weapon":{"weaponpath":weapon1,"weapon_similarity":s1}}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None
        else:
            d = {"error":"not found"}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None

        d = {"currentimg":blackwhite_img}
        self.qt_comunicate.update.emit(d) if self.qt_comunicate else None

    def screenshot(self):
        icon_width = self.boxs["weapon1"][2]
        icon_height = self.boxs["weapon1"][3]
        icon_scale = icon_width/icon_height
        icon_height = round(icon_height * self.resize_rate)
        icon_width = round(icon_height * icon_scale)

        box1 = (self.boxs["weapon1"][0],
                self.boxs["weapon1"][1],
                self.boxs["weapon1"][0] + icon_width,
                self.boxs["weapon1"][1] + icon_height)

        img1 = screenshot(box1)

        cvimg1 = screenshot_to_cv(img1)

        if self.resize_rate != 1:
            cvimg1 = resize_img(cvimg1,self.resize_rate)

        # cvimg1 = cv.medianBlur(cvimg1,1)
        blackwhite_img1 = to_black_white(cvimg1)

        cv.imwrite("screenshot-weapon1-"+str(int(datetime.now().timestamp()))+".png",blackwhite_img1)