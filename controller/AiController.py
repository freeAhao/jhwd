from datetime import datetime
import json
import os
from tempfile import gettempdir
import time
from time import sleep
import traceback

import numpy as np
import cv2 as cv
from model.Settings import Settings
from myutils.IMGutil import *
from myutils.AIwithoutTorch import ORDML
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from myutils.QtUtils import apprestart, start_q_thread

class RecognizeCommunicate(QObject):
    update = pyqtSignal(dict)
    updateFPS = pyqtSignal(int)

class RecognizeController:

    status = None
    recoginizer = None

    def __init__(self,view) -> None:
        self.view = view
        self.c = RecognizeCommunicate()

        if Settings().app_config["game"] == "APEX":
            from model.ApexStatus import Status
            self.status = Status()
        elif Settings().app_config["game"] == "PUBG":
            from model.PubgStatus import Status
            self.status = Status()

        if "accuracy" in dir(self.view):
            self.view.accuracy.textChanged.connect(self.change_accuracy)
        self.view.startBtn.stateChanged.connect(self.toggle_rec)
        if "timeSlider" in dir(self.view):
            self.view.timeSlider.valueChanged.connect(self.updateSleepTime)
        if "screenshotBtn" in dir(self.view):
            self.view.screenshotBtn.clicked.connect(self.screenshot)

        self.c.update.connect(self.update)
        self.c.updateFPS.connect(self.updateFPS)

        self.init_ui_with_conf()
    
    def screenshot(self):
        self.recoginizer.screenshot()

    def change_accuracy(self):
        try:
            self.recoginizer.accuracy = float(self.view.accuracy.text())
            self.config["accuracy"] = float(self.view.accuracy.text())
            Settings().save_config_to_json()
        except:
            pass

    def toggle_rec(self):
        if self.recoginizer.run:
            self.recoginizer.run=False
        else:
            self.recoginizer.start.emit(True)
    
    def updateSleepTime(self):
        value = self.view.timeSlider.value() / 1000
        self.recoginizer.sleeptime = value
        self.config["sleep"] = self.view.timeSlider.value()
        Settings().save_config_to_json()

    def updateFPS(self,fps):
        fps = int(fps)
        self.view.set_fps(fps)

    def toggle_rec(self):
        if self.recoginizer.run:
            self.recoginizer.run=False
        else:
            self.recoginizer.start.emit(True)
        
    def load_config(self,name):
        self.config = Settings().get_config(name)
    
    def init_ui_with_conf(self):
        if "config" not in dir(self):
            return

        if "accuracy" not in self.config.keys():
            self.config["accuracy"] = float(self.view.accuracy.text())
        else:
            self.view.accuracy.blockSignals(True)
            self.view.accuracy.setText(str(self.config["accuracy"]))
            self.view.accuracy.blockSignals(False)

        if "sleep" not in self.config.keys():
            self.config["sleep"] = float(self.view.timeSlider.value())
        else:
            self.view.timeSlider.blockSignals(True)
            self.view.timeSlider.setValue(int(self.config["sleep"]))
            self.view.timeSlider.blockSignals(False)

class AIRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        super().__init__(view)
        self.start_rec(start)

        self.view.track.stateChanged.connect(self.toggleTrack)
        self.view.tracktime.valueChanged.connect(self.changeTrackTime)

        self.view.xRate.valueChanged.connect(self.changeRate)
        self.view.yRate.valueChanged.connect(self.changeRate)
        self.view.airegion.valueChanged.connect(self.changeAiRegion)
        self.view.fixregion.valueChanged.connect(self.changeFixRegion)

        for slider in [ self.view.ai_SCORE_THRESHOLD, self.view.ai_NMS_THRESHOLD, self.view.ai_CONFIDENCE_THRESHOLD]:
            slider.valueChanged.connect(self.changeThreshold)

        # for btn in [ self.view.ordmlBTN, self.view.ovinoBTN, self.view.ptorchBTN, self.view.tensortBTN]:
        #     btn.clicked.connect(self.changeEngine)
        self.view.providerBox.setCurrentIndex(self.view.providerBox.findData(Settings().app_config["ai"]))
        self.view.providerBox.currentTextChanged.connect(self.changeEngine)

    def start_rec(self,start:bool=True):
        provider = Settings().app_config["ai"] if "ai" in Settings().app_config else 'CPUExecutionProvider'
        self.recoginizer = AIRecoginzer(self.c,0.001,0,provider=provider)
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self, d:dict):
        if "img" in d:
            self.view.set_img(d["img"])
        elif "move" in d:
            movex = d["move"][0]
            movey = d["move"][1]
            self.status.change_fix(movex,movey)
            self.view.set_move(movex,movey)
    
    def changeEngine(self):
        provider = self.view.providerBox.currentData()
        self.recoginizer.changeEngine(provider)
        # for btn in [self.view.ordmlBTN, self.view.ovinoBTN, self.view.ptorchBTN, self.view.tensortBTN]:
        #     if btn.isChecked():
        #         if btn == self.view.ordmlBTN:
        #             self.recoginizer.changeEngine("onnxruntime")
        #         elif btn == self.view.ovinoBTN:
        #             self.recoginizer.changeEngine("openvino")
        #         elif btn == self.view.ptorchBTN:
        #             # self.recoginizer.changeEngine("pytorch")
        #             pass
        #         elif btn == self.view.tensortBTN:
        #             self.recoginizer.changeEngine("tensorrt")
        #             pass
        #         break

    def changeRate(self):
        xRate = self.view.xRate.value()
        yRate = self.view.yRate.value()
        self.recoginizer.xrate = xRate
        self.recoginizer.yrate = yRate

    def changeAiRegion(self):
        airegion = self.view.airegion.value()
        self.recoginizer.ai.airegion = airegion

    def changeFixRegion(self):
        fixregion = self.view.fixregion.value()
        self.recoginizer.ai.fixregion = fixregion
    
    def changeThreshold(self):
        score=self.view.ai_SCORE_THRESHOLD.value()
        nms=self.view.ai_NMS_THRESHOLD.value()
        confidence=self.view.ai_CONFIDENCE_THRESHOLD.value()

        self.recoginizer.ai.SCORE_THRESHOLD=score
        self.recoginizer.ai.NMS_THRESHOLD=nms
        self.recoginizer.ai.CONFIDENCE_THRESHOLD=confidence

    def toggleTrack(self):
        self.recoginizer.track = self.view.track.isChecked()
    
    def changeTrackTime(self):
        self.recoginizer.tracktime = self.view.tracktime.value()

class Recognizer(QObject):
    status = None
    start = pyqtSignal(bool)
    resolution = []
    resize_rate = 1
    boxs = {}

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy:int=10):
        super(Recognizer, self).__init__()
        self.qt_comunicate = qt_comunicate
        self.sleeptime = sleeptime
        self.accuracy = accuracy

        if Settings().app_config["game"] == "APEX":
            from model.ApexStatus import Status
            self.status = Status()
        elif Settings().app_config["game"] == "PUBG":
            from model.PubgStatus import Status
            self.status = Status()

        self.start.connect(self.rec)
        self.check_resolution()
        self.generate_config()
    
    def generate_config(self):
        if not os.path.exists((gettempdir()+"/x.lua").replace("\\","/")):
            self.status.write_config()

    def check_resolution(self):
        
        # height, width, _ = full_screenshot(screenum=int(Settings().app_config["monitor"])).shape
        monitor = get_screen_nums()[int(Settings().app_config["monitor"])]
        
        self.left = monitor["left"]
        self.top = monitor["top"]
        self.resolution = [monitor["width"],monitor["height"]]

    @pyqtSlot(bool)
    def rec(self, run):
        self.run = run 
        while self.run:
            start_time = time.time()
            self.strat_time = start_time
            self.recognize()
            sleep(self.sleeptime)
            end_time = time.time()
            self.qt_comunicate.updateFPS.emit(round(1/(end_time-start_time))) if self.qt_comunicate else None

class AIRecoginzer(Recognizer):

    xrate = 0.2
    yrate = 0
    box = None
    track = True
    tracktime = 0.5

    def __init__(self,qt_comunicate=None, sleeptime=0.01,accuracy=0,provider='CPUExecutionProvider',):
        super().__init__(qt_comunicate, sleeptime,accuracy)
        try:
            self.ai = ORDML(provider)
        except:
            traceback.print_exc()
            self.ai = None

        try:
            self.create_tracker()
        except:
            traceback.print_exc()
            self.track = False

    def create_tracker(self):
        tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        tracker_type = tracker_types[4]
        if tracker_type == 'GOTURN':
            tracker = cv.legacy.TrackerBoosting_create()
        elif tracker_type == 'MIL':
            tracker = cv.legacy.TrackerMIL_create()
        elif tracker_type == 'KCF':
            tracker = cv.legacy.TrackerKCF_create()
        elif tracker_type == 'TLD':
            tracker = cv.legacy.TrackerTLD_create()
        elif tracker_type == 'MEDIANFLOW':
            tracker = cv.legacy.TrackerMedianFlow_create()
        elif tracker_type == 'GOTURN':
            tracker = cv.legacy.TrackerGOTURN_create()
        elif tracker_type == 'MOSSE':
            tracker = cv.legacy.TrackerMOSSE_create()
        elif tracker_type == "CSRT":
            tracker = cv.TrackerCSRT_create()
        self.tracker = tracker

    def recognize(self):
        if not self.ai:
            return
        box = (round(self.resolution[0]/2 - round(320/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 - round(320/1080*self.resolution[1])+self.top),
               round(self.resolution[0]/2 + round(320/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 + round(320/1080*self.resolution[1]))+self.top)
        width = (box[2]-box[0])
        height = (box[3]-box[1])
        center = (int((width/2)),int((height/2)))

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)

        # 目标跟踪
        if self.track and self.box and time.time()-self.detecttime<self.tracktime:
            trackimg = cv.cvtColor(cvimg,cv.COLOR_BGRA2BGR)
            trackimg,simg = self.ai.circle_mask(trackimg)
            ok,bbox = self.tracker.update(trackimg)
            il,it,iw,ih = bbox
            ip1 = (int(il),int(it))
            ip2 = (int(il+iw),int(it+ih))
            op1 = (
                int(il-(self.ai.fixregion/2)*iw),
                int(it-(self.ai.fixregion/3)*ih)
            )
            op2 = (
                int(il+iw+(self.ai.fixregion/2)*iw),
                int(it+ih+(self.ai.fixregion/3)*ih)
            )

            if ok and self.pointer_in_range(center,bbox):
                cv.rectangle(simg,ip1,ip2,(0,255,0),3,cv.LINE_AA)
                cv.putText(simg, "TARGET", ip1, cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3,cv.LINE_AA)
                cv.rectangle(simg,op1,op2,(255,178,50),1,cv.LINE_AA)

                boxcenter = (
                    round(bbox[0]+(bbox[2]/2)),
                    round(bbox[1]+(bbox[3]/5)),
                )
                cv.line(simg,center,boxcenter,(255,255,255),3,cv.LINE_AA)
                cv.circle(simg,center,5,(0,255,0),3,cv.LINE_AA)

                movex = int((boxcenter[0]-center[0])*self.xrate)
                movey = int((boxcenter[1]-center[1])*self.yrate)
                self.qt_comunicate.update.emit({"move":(movex,movey)})

                text = "{}fps".format(round(1/(time.time()-self.strat_time)))
                cv.putText(simg,text,(5,50),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                qimg = cv_img_to_qimg(simg)
                self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None
                return
            else:
                self.qt_comunicate.update.emit({"move":(0,0)})
                self.box = None

        # ai目标检测
        img,box = self.ai.detect(cvimg)

        if box:
            boxcenter,bbox = self.findclose(box,center,width,height)
            if boxcenter:

                trackimg = cv.cvtColor(cvimg,cv.COLOR_BGRA2BGR)
                trackimg,_ = self.ai.circle_mask(cvimg)
                self.box = bbox
                self.detecttime = time.time()

                if self.track:
                    self.create_tracker()
                    self.tracker.init(trackimg,bbox)
                else:
                    if self.pointer_in_range(center,bbox):
                        cv.line(img,center,boxcenter,(255,255,255),3,cv.LINE_AA)
                        movex = int((boxcenter[0]-center[0])*self.xrate)
                        movey = int((boxcenter[1]-center[1])*self.yrate)
                        self.qt_comunicate.update.emit({"move":(movex,movey)})
                    else:
                        self.qt_comunicate.update.emit({"move":(0,0)})
                    # filename = "E:/Video/ai/"+str(time.time())+".jpg"
                    # cv.imwrite(filename,img)
        else:
            self.box = None
            self.qt_comunicate.update.emit({"move":(0,0)})

        text = "{}fps".format(round(1/(time.time()-self.strat_time)))
        cv.putText(img,text,(5,50),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        if box and bbox:
            cv.rectangle(img,(bbox[0],bbox[1]),(bbox[0]+bbox[2],bbox[1]+bbox[3]),(0,255,0),3,cv.LINE_AA)
        cv.circle(img,center,5,(0,255,0),3,cv.LINE_AA)
        qimg = cv_img_to_qimg(img)
        self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None

    def pointer_in_range(self,point,xywh):
        il,it,iw,ih = xywh
        op1 = (
            int(il-(self.ai.fixregion/2)*iw),
            int(it-(self.ai.fixregion/3)*ih)
        )
        op2 = (
            int(il+iw+(self.ai.fixregion/2)*iw),
            int(it+ih+(self.ai.fixregion/3)*ih)
        )
        return point[0] > op1[0] and point[0]<op2[0] and point[1]>op1[1] and point[1]<op2[1]

    def findclose(self,boxs,center,w,h):
        count = 0
        boxcenter = None
        # 找到离中心最近的目标
        closebox = None
        for b in boxs:
            boxcenter_t = (
                round(b[0]+(b[2]/2)),
                round(b[1]+(b[3]/5)),
            )
            x = int(boxcenter_t[0]-center[0])
            y = int(boxcenter_t[1]-center[1])
            sumxy = x*x+y*y
            if count == 0 or sumxy < count:
                count = sumxy
                boxcenter = boxcenter_t
                closebox = b
            else:
                continue
        # 识别率不高的情况下，不锁准心外的目标
        # if center[0] > closebox[0]-(self.ai.fixregion)*closebox[2] and center[0] < closebox[0]+(self.ai.fixregion+1)*closebox[2] and center[1] > closebox[1]-(self.ai.fixregion)*closebox[3] and center[1] < closebox[1]+(self.ai.fixregion+1)*closebox[3]:
        #     return boxcenter,closebox
        return boxcenter,closebox
    
    def changeEngine(self,engine):
        if engine in self.ai.providers.keys():
            Settings().app_config["ai"] = engine
            Settings().save_app_config_to_json()
            apprestart()


class BloodRecoginzer(Recognizer):

    xrate = 1
    yrate = 0
    h = (156,180)
    s = (43,255)
    v = (46,255)
    regionh = 0.5
    regionw = 0.5

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0,regionh=0.5,regionw=0.5):
        super().__init__(qt_comunicate, sleeptime,accuracy)
        self.regionh = regionh
        self.regionw = regionw

    def recognize(self):
        box = (round(self.resolution[0]/2 - round(960*self.regionw/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 - round(540*self.regionh/1080*self.resolution[1])+self.top),
               round(self.resolution[0]/2 + round(960*self.regionw/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 + round(540*self.regionh/1080*self.resolution[1])+self.top))
        width = (box[2]-box[0])
        height = (box[3]-box[1])
        center = (int((width/2)),int((height/2)))

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        cvimg = resize_img(cvimg,self.resize_rate)
        hsv = cv.cvtColor(cvimg,cv.COLOR_BGR2HSV)

        lower = np.array([self.h[0], self.s[0], self.v[0]], np.uint8)
        upper = np.array([self.h[1], self.s[1], self.v[1]], np.uint8)

        hsv = cv.medianBlur(hsv,9)
        mask = cv.inRange(hsv, lower, upper)

        if np.sum(mask[:,:])>30000:

            blood = np.where(mask[:,:]==255)
            dot1 = (np.min(blood[1]),np.min(blood[0]))
            dot2 = (np.max(blood[1]),np.max(blood[0]))
            blood_area = (dot2[1] - dot1[1]) * (dot2[0] -dot1[0])
            screen_area = width * height

            cv.rectangle(mask,dot1,dot2,(255,255,255))
            blood_center = (round((dot2[0]-dot1[0])/2)+dot1[0], round((dot2[1]-dot1[1])/2)+dot1[1])
            cv.line(mask,center,blood_center,(255,255,255))
            movex = int((blood_center[0]-center[0])*self.xrate * (blood_area/screen_area))
            movey = -int((blood_center[1]-center[1])*self.yrate)
            if movey < 0:
                movey = 0
            self.qt_comunicate.update.emit({"move":(movex,movey)})
            qimg = cv_img_to_qimg(mask)
        else:
            qimg = cv_img_to_qimg(cvimg)
            self.qt_comunicate.update.emit({"move":(0,0)})

        self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None

class BloodRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        super().__init__(view)
        self.start_rec(start)

        self.view.xRate.valueChanged.connect(self.changeRate)
        self.view.yRate.valueChanged.connect(self.changeRate)

        self.view.h.valueChanged.connect(self.changeColor)
        self.view.s.valueChanged.connect(self.changeColor)
        self.view.v.valueChanged.connect(self.changeColor)

        self.view.regionh.valueChanged.connect(self.changeRegion)
        self.view.regionw.valueChanged.connect(self.changeRegion)

    def start_rec(self,start:bool=True):
        self.recoginizer = BloodRecoginzer(self.c,0.001,0,self.view.regionh.value(),self.view.regionw.value())
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self, d:dict):
        if "img" in d:
            self.view.set_img(d["img"])
        elif "move" in d:
            movex = d["move"][0]
            movey = d["move"][1]
            self.status.change_fix(movex,movey)
            self.view.set_move(movex,movey)

    def changeRate(self):
        xRate = self.view.xRate.value()
        yRate = self.view.yRate.value()
        self.recoginizer.xrate = xRate
        self.recoginizer.yrate = yRate

    def changeColor(self):
        h = self.view.h.value()
        s = self.view.s.value()
        v = self.view.v.value()
        self.recoginizer.h = h
        self.recoginizer.s = s
        self.recoginizer.v = v 
    
    def changeRegion(self):
        self.recoginizer.regionh=self.view.regionh.value()
        self.recoginizer.regionw=self.view.regionw.value()

class AntiShakeRecoginzer(Recognizer):

    xrate = 1
    yrate = 0
    prevImg = None
    tracks = []
    track_len = 2
    lk_params = dict( winSize  = (15, 15), 
                  maxLevel = 2, 
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))    
 
    feature_params = dict( maxCorners = 500, 
                        qualityLevel = 0.3,
                        minDistance = 7,
                        blockSize = 7 )

    def __init__(self, qt_comunicate=None, sleeptime=0.01,accuracy=0):
        super().__init__(qt_comunicate, sleeptime,accuracy)

    def recognize(self):
        box = (round(self.resolution[0]/2 - round(80/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 - round(80/1080*self.resolution[1])+self.top),
               round(self.resolution[0]/2 + round(80/1920*self.resolution[0])+self.left),
               round(self.resolution[1]/2 + round(80/1080*self.resolution[1])+self.top))
        width = (box[2]-box[0])
        height = (box[3]-box[1])
        center = (int((width/2)),int((height/2)))

        img = screenshot(box)
        cvimg = screenshot_to_cv(img)
        cvimg_gray = cv.cvtColor(cvimg, cv.COLOR_BGR2GRAY)
        mask = np.zeros_like(cvimg_gray) 
        mask[:] = 255

        if len(self.tracks)>0:
            img0, img1 = self.prevImg, cvimg_gray
            p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
            p1, st, err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **self.lk_params)
            p0r, st, err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **self.lk_params)
            d = abs(p0-p0r).reshape(-1, 2).max(-1)
            good = d < 1#判断d内的值是否小于1，大于1跟踪被认为是错误的跟踪点
            new_tracks = []
            for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                x = round(x)
                y = round(y)
                if not good_flag:
                    continue
                tr.append((x, y))
                if len(tr) > self.track_len:
                    del tr[0]
                new_tracks.append(tr)
                cv.circle(cvimg, (x, y), 2, (0, 255, 0), -1)
            self.tracks = new_tracks
            movex = 0
            movey = 0
            ts = [np.int32(tr) for tr in self.tracks]
            for i in ts:
                s = np.subtract(i[1],i[0])
                movex = movex+s[0]
                movey = movey+s[1]
            if len(ts)>0:
                movex = round(movex/len(ts)*self.xrate)
                movey = round(movey/len(ts)*self.yrate)
                self.qt_comunicate.update.emit({"move":(movex,movey)})

            cv.polylines(cvimg, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))

        for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
            cv.circle(mask, (x, y), 5, 0, -1)
        p = cv.goodFeaturesToTrack(cvimg_gray, mask = mask, **self.feature_params)
        if p is not None:
            for x, y in np.float32(p).reshape(-1, 2):
                self.tracks.append([(x, y)])

        self.prevImg = cvimg_gray

        qimg = cv_img_to_qimg(cvimg)
        self.qt_comunicate.update.emit({"img":qimg}) if self.qt_comunicate else None

class AntiShakeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        super().__init__(view)
        self.start_rec(start)

        self.view.xRate.valueChanged.connect(self.changeRate)
        self.view.yRate.valueChanged.connect(self.changeRate)

    def start_rec(self,start:bool=True):
        self.recoginizer = AntiShakeRecoginzer(self.c,0.001)
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self,d:dict):
        if "img" in d:
            self.view.set_img(d["img"])
        elif "move" in d:
            movex = d["move"][0]
            movey = d["move"][1]
            self.status.change_fix(movex,movey)
            self.view.set_move(movex,movey)

    def changeRate(self):
        xRate = self.view.xRate.value()
        yRate = self.view.yRate.value()
        self.recoginizer.xrate=xRate
        self.recoginizer.yrate=yRate