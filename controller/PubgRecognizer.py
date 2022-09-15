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
from model.PubgStatus import Status
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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
        
        height, width, _ = full_screenshot(screenum=int(Settings().app_config["monitor"])).shape
        filename  = Settings().resource_dir+"resolution/{}_{}.json".format(width,height)
        if not (height == 1080 and width == 1920):
            self.resize_rate = float(height/1080)
        self.resolution = [width,height]
        try:
            with open(filename,"r") as f:
                self.boxs = json.load(f)
            monitor = get_screen_nums()[int(Settings().app_config["monitor"])]
            for k in self.boxs:
                point = self.boxs[k]
                newpoint = [point[0]+monitor["left"],point[1]+monitor["top"]]
                self.boxs[k] = newpoint
        except FileNotFoundError:
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
    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0.5):
        super().__init__(qt_comunicate, sleeptime,accuracy)
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
        icon_width = round(150 * self.resize_rate)
        icon_height = round(55 * self.resize_rate)

        box2 = (self.boxs["weapon2"][0],
                self.boxs["weapon2"][1],
                self.boxs["weapon2"][0] + icon_width,
                self.boxs["weapon2"][1] + icon_height)
        box1 = (self.boxs["weapon1"][0],
                self.boxs["weapon1"][1],
                self.boxs["weapon1"][0] + icon_width,
                self.boxs["weapon1"][1] + icon_height)

        img1 = screenshot(box1)
        img2 = screenshot(box2)

        cvimg1 = screenshot_to_cv(img1)
        cvimg2 = screenshot_to_cv(img2)

        if self.resize_rate != 1:
            cvimg1 = resize_img(cvimg1,self.resize_rate)
            cvimg2 = resize_img(cvimg2,self.resize_rate)

        blackwhite_img1 = to_black_white(cvimg1)
        blackwhite_img2 = to_black_white(cvimg2)

        finded1 = False
        finded2 = False

        if self.isweapon_icon(blackwhite_img1):
            # finded1,weapon1,s1 = similarity(blackwhite_img1, self.gun_list,self.accuracy)
            finded1,weapon1,s1 = cv_match(blackwhite_img1, self.gun_list,self.accuracy)
        if self.isweapon_icon(blackwhite_img2):
            # finded2,weapon2,s2 = similarity(blackwhite_img2, self.gun_list,self.accuracy)
            finded2,weapon2,s2 = cv_match(blackwhite_img2, self.gun_list,self.accuracy)

        if finded2 :
            d = {"weapon2":{"path":weapon2,"similarity":s2}}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None

        if finded1:
            d = {"weapon1":{"path":weapon1,"similarity":s1}}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None

        if finded2 and np.sum(blackwhite_img2) > np.sum(blackwhite_img1):
            d = {"currentweapon": 2}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None
        elif finded1:
            d = {"currentweapon": 1}
            self.qt_comunicate.update.emit(d) if self.qt_comunicate else None

    def screenshot(self):
        icon_width = round(150 * self.resize_rate)
        icon_height = round(55 * self.resize_rate)

        box2 = (self.boxs["weapon2"][0],
                self.boxs["weapon2"][1],
                self.boxs["weapon2"][0] + icon_width,
                self.boxs["weapon2"][1] + icon_height)
        box1 = (self.boxs["weapon1"][0],
                self.boxs["weapon1"][1],
                self.boxs["weapon1"][0] + icon_width,
                self.boxs["weapon1"][1] + icon_height)

        img1 = screenshot(box1)
        img2 = screenshot(box2)

        cvimg1 = screenshot_to_cv(img1)
        cvimg2 = screenshot_to_cv(img2)

        if self.resize_rate != 1:
            cvimg1 = resize_img(cvimg1,self.resize_rate)
            cvimg2 = resize_img(cvimg2,self.resize_rate)

        blackwhite_img1 = to_black_white(cvimg1)
        blackwhite_img2 = to_black_white(cvimg2)
        filename = "{}_{:.2f}.png".format(datetime.now().timestamp(),self.resize_rate)

        cv.imwrite("1"+filename,blackwhite_img1)
        cv.imwrite("2"+filename,blackwhite_img2)

class PoseRecoginzer(Recognizer):
    pose_list={}
    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0.5):
        super().__init__(qt_comunicate, sleeptime,accuracy)
        self.get_resources()

    def get_resources(self):
        self.pose_list={}
        for files in os.listdir(Settings().resource_dir+"pos/"):
            if not str(files).endswith(".png"):
                continue
            resource = Settings().resource_dir+"pos/"+str(files)
            template = cv.imread(resource)
            self.pose_list[resource] = template

    def recognize(self):
        icon_width = round(50 * self.resize_rate)
        icon_height = round(55 * self.resize_rate)

        box = (self.boxs["pose"][0],
               self.boxs["pose"][1],
               self.boxs["pose"][0]+icon_width,
               self.boxs["pose"][1]+icon_height)

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        cvimg = resize_img(cvimg,self.resize_rate)
        bwimg = to_black_white(cvimg)
        finded,pose,s = cv_match(bwimg, self.pose_list,self.accuracy)

        # self.qt_comunicate.updatePose.emit(cv_img_to_qimg(bwimg)) if self.qt_comunicate else None

        if finded:
            if self.status.pose != pose:
                self.qt_comunicate.update.emit({"posepath":pose,"similarity":s}) if self.qt_comunicate else None

    def screenshot(self):
        icon_width = round(50 * self.resize_rate)
        icon_height = round(55 * self.resize_rate)

        box = (self.boxs["pose"][0],
               self.boxs["pose"][1],
               self.boxs["pose"][0]+icon_width,
               self.boxs["pose"][1]+icon_height)

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        cvimg = resize_img(cvimg,self.resize_rate)
        bwimg = to_black_white(cvimg)
        filename = "{}_{:.2f}.png".format(datetime.now().timestamp(),self.resize_rate)
        cv.imwrite(filename, bwimg)

class AttachmentRecoginzer(Recognizer):
    printed = False
    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0.5):
        super().__init__(qt_comunicate, sleeptime,accuracy)
        self.get_resources()

    def get_resources(self):
        self.attachments={}

        for i in range(0,5):
            self.attachments[i] = {}
            for files in os.listdir(Settings().resource_dir+"attachments/"+str(i+1)):
                if not str(files).endswith(".png"):
                    continue
                resource = Settings().resource_dir+"attachments/"+str(i+1)+"/"+str(files)
                template = cv.imread(resource)
                # template = to_black_white2(template)
                self.attachments[i][resource] = template

        self.bp = {}
        for files in os.listdir(Settings().resource_dir+"bp/"):
            if not str(files).endswith(".png"):
                continue
            resource = Settings().resource_dir+"bp/"+str(files)
            template = cv.imread(resource)
            self.bp[resource] = template

    def is_backpack_open(self,weapon_info_img):
        icon_width=round(27*self.resize_rate)
        icon_height=round(27*self.resize_rate)
        img = weapon_info_img[self.boxs["bp1"][1]:self.boxs["bp1"][1]+icon_height,
                                self.boxs["bp1"][0]:self.boxs["bp1"][0]+icon_width, :]
        if self.resize_rate != 1:
            img = cv.resize(img,(27,27))
        img = to_black_white(img)
        finded,f,s = cv_match(img,self.bp,self.accuracy)
        if finded:
            return True,f

        img = weapon_info_img[self.boxs["bp2"][1]:self.boxs["bp2"][1]+icon_height,
                                self.boxs["bp2"][0]:self.boxs["bp2"][0]+icon_width, :]
        if self.resize_rate != 1:
            img = cv.resize(img,(27,27))
        img = to_black_white(img)
        finded,f,s = cv_match(img,self.bp,self.accuracy)
        if finded:
            return True,f
        return False,f
        
    def recognize(self):
        weapon_info_img = screenshot((0,0,self.resolution[0],self.resolution[1]))
        weapon_info_img = screenshot_to_cv(weapon_info_img)
        open,r = self.is_backpack_open(weapon_info_img)
        if not open:
            self.printed = False
            return
        if self.printed == False:
            print("打开背包", r)
            self.printed = True
        icon_width =  round(48*self.resize_rate)
        icon_height = round(48*self.resize_rate)
        self.boxs["w1scope"][0]
        self.boxs["w1a1"][0]

        w1scope_box = weapon_info_img[self.boxs["w1scope"][1]:self.boxs["w1scope"][1]+icon_height,
            self.boxs["w1scope"][0]:self.boxs["w1scope"][0]+icon_width, :]
        w11 = weapon_info_img[self.boxs["w1a1"][1]:self.boxs["w1a1"][1]+icon_height,
                              self.boxs["w1a1"][0]:self.boxs["w1a1"][0]+icon_width, :]
        w12 = weapon_info_img[self.boxs["w1a2"][1]:self.boxs["w1a2"][1]+icon_height,
                              self.boxs["w1a2"][0]:self.boxs["w1a2"][0]+icon_width, :]
        w13 = weapon_info_img[self.boxs["w1a3"][1]:self.boxs["w1a3"][1]+icon_height,
                              self.boxs["w1a3"][0]:self.boxs["w1a3"][0]+icon_width, :]
        w14 = weapon_info_img[self.boxs["w1a4"][1]:self.boxs["w1a4"][1]+icon_height,
                              self.boxs["w1a4"][0]:self.boxs["w1a4"][0]+icon_width, :]

        w2scope_box = weapon_info_img[self.boxs["w2scope"][1]:self.boxs["w2scope"][1]+icon_height,
            self.boxs["w2scope"][0]:self.boxs["w2scope"][0]+icon_width, :]
        w21 = weapon_info_img[self.boxs["w2a1"][1]:self.boxs["w2a1"][1]+icon_height,
                              self.boxs["w2a1"][0]:self.boxs["w2a1"][0]+icon_width, :]
        w22 = weapon_info_img[self.boxs["w2a2"][1]:self.boxs["w2a2"][1]+icon_height,
                              self.boxs["w2a2"][0]:self.boxs["w2a2"][0]+icon_width, :]
        w23 = weapon_info_img[self.boxs["w2a3"][1]:self.boxs["w2a3"][1]+icon_height,
                              self.boxs["w2a3"][0]:self.boxs["w2a3"][0]+icon_width, :]
        w24 = weapon_info_img[self.boxs["w2a4"][1]:self.boxs["w2a4"][1]+icon_height,
                              self.boxs["w2a4"][0]:self.boxs["w2a4"][0]+icon_width, :]

        weapon1_attachments = [w1scope_box,w11,w12,w13,w14]
        weapon2_attachments = [w2scope_box,w21,w22,w23,w24]


        findany = False

        result1 = []
        result2 = []

        for index,cvimg in enumerate(weapon1_attachments):
            blackwhite_img = to_black_white2(cvimg)
            if self.resize_rate:
                blackwhite_img = cv.resize(blackwhite_img,(round(blackwhite_img.shape[1]/self.resize_rate), round(blackwhite_img.shape[1]/self.resize_rate)))
            finded,attachment,s = cv_match(blackwhite_img, self.attachments[index], self.accuracy)
            result1.append([finded,attachment,s])
            if finded:
                findany = True

        for index,cvimg in enumerate(weapon2_attachments):
            blackwhite_img = to_black_white2(cvimg)
            if self.resize_rate:
                blackwhite_img = cv.resize(blackwhite_img,(round(blackwhite_img.shape[1]/self.resize_rate), round(blackwhite_img.shape[1]/self.resize_rate)))
            finded,attachment,s = cv_match(blackwhite_img, self.attachments[index], self.accuracy)
            result2.append([finded,attachment,s])
            if finded:
                findany = True

        self.qt_comunicate.update.emit({"weapon1":result1,"weapon2":result2})
        
    def screenshot(self):
        weapon_info_img = screenshot((0,0,self.resolution[0],self.resolution[1]))
        weapon_info_img = screenshot_to_cv(weapon_info_img)

        icon_width =  round(48*self.resize_rate)
        icon_height = round(48*self.resize_rate)
        self.boxs["w1scope"][0]
        self.boxs["w1a1"][0]

        w1scope_box = weapon_info_img[self.boxs["w1scope"][1]:self.boxs["w1scope"][1]+icon_height,
            self.boxs["w1scope"][0]:self.boxs["w1scope"][0]+icon_width, :]
        w11 = weapon_info_img[self.boxs["w1a1"][1]:self.boxs["w1a1"][1]+icon_height,
                              self.boxs["w1a1"][0]:self.boxs["w1a1"][0]+icon_width, :]
        w12 = weapon_info_img[self.boxs["w1a2"][1]:self.boxs["w1a2"][1]+icon_height,
                              self.boxs["w1a2"][0]:self.boxs["w1a2"][0]+icon_width, :]
        w13 = weapon_info_img[self.boxs["w1a3"][1]:self.boxs["w1a3"][1]+icon_height,
                              self.boxs["w1a3"][0]:self.boxs["w1a3"][0]+icon_width, :]
        w14 = weapon_info_img[self.boxs["w1a4"][1]:self.boxs["w1a4"][1]+icon_height,
                              self.boxs["w1a4"][0]:self.boxs["w1a4"][0]+icon_width, :]

        w2scope_box = weapon_info_img[self.boxs["w2scope"][1]:self.boxs["w2scope"][1]+icon_height,
            self.boxs["w2scope"][0]:self.boxs["w2scope"][0]+icon_width, :]
        w21 = weapon_info_img[self.boxs["w2a1"][1]:self.boxs["w2a1"][1]+icon_height,
                              self.boxs["w2a1"][0]:self.boxs["w2a1"][0]+icon_width, :]
        w22 = weapon_info_img[self.boxs["w2a2"][1]:self.boxs["w2a2"][1]+icon_height,
                              self.boxs["w2a2"][0]:self.boxs["w2a2"][0]+icon_width, :]
        w23 = weapon_info_img[self.boxs["w2a3"][1]:self.boxs["w2a3"][1]+icon_height,
                              self.boxs["w2a3"][0]:self.boxs["w2a3"][0]+icon_width, :]
        w24 = weapon_info_img[self.boxs["w2a4"][1]:self.boxs["w2a4"][1]+icon_height,
                              self.boxs["w2a4"][0]:self.boxs["w2a4"][0]+icon_width, :]

        bp1 = weapon_info_img[self.boxs["bp1"][1]:self.boxs["bp1"][1]+round(27*self.resize_rate),
                                self.boxs["bp1"][0]:self.boxs["bp1"][0]+round(27*self.resize_rate), :]
        bp2 = weapon_info_img[self.boxs["bp2"][1]:self.boxs["bp2"][1]+round(27*self.resize_rate),
                                self.boxs["bp2"][0]:self.boxs["bp2"][0]+round(27*self.resize_rate), :]

        weapon1_attachments = [w1scope_box,w11,w12,w13,w14]
        weapon2_attachments = [w2scope_box,w21,w22,w23,w24]

        result1 = []
        result2 = []

        for index,cvimg in enumerate(weapon1_attachments):
            blackwhite_img = cvimg
            blackwhite_img = to_black_white2(cvimg)
            if self.resize_rate:
                blackwhite_img = cv.resize(blackwhite_img,(round(blackwhite_img.shape[1]/self.resize_rate), round(blackwhite_img.shape[1]/self.resize_rate)))
                filename="w1{}-{}_{:.2f}.png".format(datetime.now().timestamp(),index+1,self.resize_rate,)
                cv.imwrite(filename,blackwhite_img)
        for index,cvimg in enumerate(weapon2_attachments):
            blackwhite_img = cvimg
            blackwhite_img = to_black_white2(cvimg)
            if self.resize_rate:
                blackwhite_img = cv.resize(blackwhite_img,(round(blackwhite_img.shape[1]/self.resize_rate), round(blackwhite_img.shape[1]/self.resize_rate)))
                filename="w2{}-{}_{:.2f}.png".format(datetime.now().timestamp(),index+1,self.resize_rate,)
                cv.imwrite(filename,blackwhite_img)

        for index,cvimg in enumerate([bp1,bp2]):

            if self.resize_rate != 1:
                cvimg = cv.resize(cvimg,(27,27))
            cvimg = to_black_white(cvimg)
            cv.imwrite("./bp{}_{:.2f}.png".format(index+1,self.resize_rate),cvimg)
