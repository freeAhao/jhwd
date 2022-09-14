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
from model.Status import Status
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from myutils.AIwithoutTorch import ORDML,OVINO
# from utils.Yolov5Utils import Yolov5Utils

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
        icon_width = round(185 * self.resize_rate)
        icon_height = round(45 * self.resize_rate)
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
        icon_width = round(180 * self.resize_rate)
        icon_height = round(45 * self.resize_rate)

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

class BloodRecoginzer(Recognizer):

    xrate = 0
    yrate = 0
    h = 156
    s = 43
    v = 46

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0):
        super().__init__(qt_comunicate, sleeptime)

    def recognize(self):
        box = (round(self.resolution[0]/2 - round(40/1920*self.resolution[0])),
               round(self.resolution[1]/2 - round(40/1080*self.resolution[1])),
               round(self.resolution[0]/2 + round(40/1920*self.resolution[0])),
               round(self.resolution[1]/2 + round(40/1080*self.resolution[1])))
        width = (box[2]-box[0])
        height = (box[3]-box[1])
        center = (int((width/2)),int((height/2)))

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        cvimg = resize_img(cvimg,self.resize_rate)
        hsv = cv.cvtColor(cvimg,cv.COLOR_BGR2HSV)

        lower = np.array([self.h, self.s, self.v], np.uint8)
        upper = np.array([180, 255, 255], np.uint8)

        hsv = cv.medianBlur(hsv,9)
        mask = cv.inRange(hsv, lower, upper)

        if np.sum(mask[:,:])>30000:

            blood = np.where(mask[:,:]==255)
            dot1 = (np.min(blood[1]),np.min(blood[0]))
            dot2 = (np.max(blood[1]),np.max(blood[0]))
            blood_area = (dot2[1] - dot1[1]) * (dot2[0] -dot1[0])
            screen_area = width * height

            # if blood_area/screen_area>1/5 or (center[0]>dot2[0] or center[0]<dot1[0]):
            #     qimg = cv_img_to_qimg(cvimg)
            #     self.qt_comunicate.update.emit({"move":(0,0)})
            # else:
            if not (center[0]>= dot1[0] -5 and center[0] <= dot2[0] +5 and center[1] >= dot1[1]-5 and center[1] <= dot2[1]+5):
                qimg = cv_img_to_qimg(cvimg)
                self.qt_comunicate.update.emit({"move":(0,0)})
            else:
                cv.rectangle(mask,dot1,dot2,(255,255,255))
                blood_center = (round((dot2[0]-dot1[0])/2)+dot1[0], round((dot2[1]-dot1[1])/2)+dot1[1])
                cv.line(mask,center,blood_center,(255,255,255))
                # movex = int((blood_center[0]-center[0])*self.xrate  * (blood_area/screen_area))
                # movey = int((blood_center[1]-center[1])*self.yrate * (blood_area/screen_area))
                movex = int((blood_center[0]-center[0])*self.xrate)
                movey = int((blood_center[1]-center[1])*self.yrate)
                # movex = int((blood_center[0]-center[0])*self.xrate)
                # movey = -int((blood_center[1]-center[1])*self.yrate)
                # if movey < 0:
                #     movey = 0
                self.qt_comunicate.update.emit({"move":(movex,movey)})
                qimg = cv_img_to_qimg(mask)
        else:
            qimg = cv_img_to_qimg(cvimg)
            self.qt_comunicate.update.emit({"move":(0,0)})

        self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None

class AIRecoginzer(Recognizer):

    xrate = 0
    yrate = 0

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0):
        super().__init__(qt_comunicate, sleeptime)
        self.ai = ORDML(Settings().resource_dir+"weights/best.onnx")
        # self.ai = OVINO()
        # self.ai = PTORCH()

    def recognize(self):
        box = (round(self.resolution[0]/2 - round(350/1920*self.resolution[0])),
               round(self.resolution[1]/2 - round(350/1080*self.resolution[1])),
               round(self.resolution[0]/2 + round(350/1920*self.resolution[0])),
               round(self.resolution[1]/2 + round(350/1080*self.resolution[1])))
        width = (box[2]-box[0])
        height = (box[3]-box[1])
        center = (int((width/2)),int((height/2)))

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        # cvimg = resize_img(cvimg,self.resize_rate)

        img,box = self.ai.detect(cvimg)
        if box:
            boxcenter = self.findclose(box,center,width,height)
            if boxcenter:
                cv.line(img,center,boxcenter,(255,255,255))

                movex = int((boxcenter[0]-center[0])*self.xrate)
                movey = int((boxcenter[1]-center[1])*self.yrate)
                self.qt_comunicate.update.emit({"move":(movex,movey)})
                # filename = "E:/Video/ai/"+str(time.time())+".jpg"
                # cv.imwrite(filename,img)
        else:
            self.qt_comunicate.update.emit({"move":(0,0)})

        qimg = cv_img_to_qimg(img)
        self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None
    
    def findclose(self,boxs,center,w,h):
        count = 0
        boxcenter = None
        # 找到离中心最近的目标
        closebox = None
        for b in boxs:
            # if ((b[2]*b[3])/(w*h)<0.01):
            #     print(b[2]*b[3],w*h,(b[2]*b[3])/(w*h))
            #     continue
            # print(b[2]*b[3],w*h,(b[2]*b[3])/(w*h))
            boxcenter_t = (
                round(b[0]+(b[2]/2)),
                round(b[1]+(b[3]/2)),
            )
            x = int(boxcenter_t[0]-center[0])
            y = int(boxcenter_t[1]-center[1])
            sumxy = x*x+y*y
            if count == 0 or sumxy < count:
                count == sumxy
                boxcenter = boxcenter_t
                closebox = b
            else:
                continue
        # 识别率不高的情况下，不锁准心外的目标
        if center[0] > closebox[0]-(self.ai.fixregion/100)*closebox[2] and center[0] < closebox[0]+(self.ai.fixregion/100+1)*closebox[2]:
            return boxcenter
        return None
    
    def changeEngine(self,engine):
        print(engine)
        if engine == "onnxruntime":
            self.ai = ORDML(Settings().resource_dir+"weights/best.onnx")
        if engine == "openvino":
            self.ai = OVINO(Settings().resource_dir+"weights/best.xml")
        if engine == "pytorch":
            self.ai = PTORCH()
        if engine == "tensortrt":
            pass
                    
                    
                    
                    