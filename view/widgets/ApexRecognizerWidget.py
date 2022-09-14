import os
import cv2
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout,QFileDialog,QPushButton,QScrollArea,QLineEdit,QTextEdit,QSlider,QCheckBox,QGroupBox,QRadioButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import numpy as np
from model.Settings import Settings

from myutils.IMGutil import cv_img_to_qimg, qt_img_to_cv
from myutils.QtUtils import set_label_img, qimg_to_qpix
from controller.ApexRecognizeController import BloodRecognizeController, WeaponRecognizeController, AIRecognizeController

class QRecognizer(QWidget):

    controller = None

    def __init__(self) -> None:
        super().__init__()

        self.setUI()

    def setUI(self):
        pass
        
    def set_fps(self,fps):
        pass

    def updateUI(self, d:dict):
        pass

class QWeaponRecognizer(QRecognizer):


    def __init__(self) -> None:
        super().__init__()

        self.controller = WeaponRecognizeController(self,True)

    def setUI(self):

        # self.labelWeapongrab = QLabel('weapon grab')

        self.labelWeapon2 = QLabel('weapon2')
        set_label_img(self.labelWeapon2, Settings().resource_dir+"weapon_null.png")

        self.labelWeapon1 = QLabel('weapon1')
        set_label_img(self.labelWeapon1, Settings().resource_dir+"weapon_null.png")

        self.screenshotBtn = QPushButton("截图")

        self.accuracy = QLineEdit("5")

        self.fpsText = QLabel('fps')

        self.startBtn = QCheckBox("disable")

        timeSlider = QSlider(Qt.Orientation.Horizontal)
        timeSlider.setMaximum(500)
        timeSlider.setMinimum(0)
        timeSlider.setValue(100)
        self.timeSlider = timeSlider

        #layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.labelWeapon2,0,0,2,1)
        grid.addWidget(self.labelWeapon1,2,0,2,1)
        grid.addWidget(self.screenshotBtn,4,0)
        grid.addWidget(self.accuracy,5,0)
        grid.addWidget(self.fpsText,6,0)
        grid.addWidget(self.timeSlider,7,0)
        grid.addWidget(self.startBtn,8,0)

        self.setLayout(grid)
    
    def set_fps(self, fps:int):
        self.fpsText.setText(str(fps)+"fps")
    
    def set_img1(self,imgpath):
        set_label_img(self.labelWeapon1, imgpath)

    def set_img2(self,img):
        set_label_img(self.labelWeapon2, img)

class QBloodFix(QRecognizer):

    def __init__(self) -> None:
        super().__init__()

        self.controller = BloodRecognizeController(self,False)

    def setUI(self):

        imgLabel = QLabel()
        self.imgLabel = imgLabel

        startBtn = QCheckBox("disable")
        startBtn.setChecked(True)
        self.startBtn = startBtn

        fpsLabel = QLabel("fps")
        moveLabel = QLabel("")

        xRate = QSlider(Qt.Orientation.Horizontal)
        yRate = QSlider(Qt.Orientation.Horizontal)
        xRate.setMaximum(500)
        xRate.setMinimum(0)
        xRate.setSingleStep(10)
        yRate.setMaximum(100)
        yRate.setMinimum(0)
        yRate.setSingleStep(10)
        xRate.setValue(0)
        yRate.setValue(0)

        self.xRate = xRate
        self.yRate = yRate

        h = QSlider(Qt.Orientation.Horizontal)
        h.setMaximum(180)
        h.setMinimum(0)
        h.setSingleStep(1)
        h.setValue(156)
        s = QSlider(Qt.Orientation.Horizontal)
        s.setMaximum(255)
        s.setMinimum(0)
        s.setSingleStep(1)
        s.setValue(43)
        v = QSlider(Qt.Orientation.Horizontal)
        v.setMaximum(255)
        v.setMinimum(0)
        v.setSingleStep(1)
        v.setValue(46)
        self.h=h
        self.s=s
        self.v=v
        grouphsv = QGroupBox("hsv")
        gridhsv =QGridLayout()
        gridhsv.addWidget(h,0,0)
        gridhsv.addWidget(s,1,0)
        gridhsv.addWidget(v,2,0)
        grouphsv.setLayout(gridhsv)

        
        group = QGroupBox("fix rate")
        grid =QGridLayout()

        grid.addWidget(xRate,0,0)
        grid.addWidget(yRate,1,0)

        group.setLayout(grid)

        self.fpsLabel = fpsLabel
        self.moveLabel = moveLabel

        grid =QGridLayout()


        # self.c = Communicate()
        # self.c.updateFPS.connect(self.updateFPS)
        # self.c.updateImage.connect(self.updateImage)
        # self.c.updateMOVE.connect(self.updateMove)

        # thread = QThread(parent=self)
        # self.recoginizer = Recognizer(Recognizer.RecType.BLOODFIX,self.c,0.001)
        # self.recoginizer.moveToThread(thread)
        # self.recoginizer.start.emit(False)
        # thread.start()

        grid.addWidget(imgLabel,0,0)
        grid.addWidget(moveLabel,1,0)
        grid.addWidget(group,2,0)
        grid.addWidget(grouphsv,3,0)
        grid.addWidget(fpsLabel,4,0)
        grid.addWidget(startBtn,4,1)

        self.setLayout(grid)


    def set_fps(self,fps):
        self.fpsLabel.setText(str.format("{} fps",fps))

    def set_img(self, img):
        self.imgLabel.setPixmap(qimg_to_qpix(img))

    def set_move(self,x,y):
        self.moveLabel.setText(str.format("x:{},y:{}",x,y))

class QAiFix(QRecognizer):

    def __init__(self) -> None:
        super().__init__()

        self.controller = AIRecognizeController(self,False)

    def setUI(self):

        imgLabel = QLabel()
        self.imgLabel = imgLabel

        startBtn = QCheckBox("disable")
        startBtn.setChecked(True)
        self.startBtn = startBtn

        fpsLabel = QLabel("fps")
        moveLabel = QLabel("")

        xRate = QSlider(Qt.Orientation.Horizontal)
        yRate = QSlider(Qt.Orientation.Horizontal)
        xRate.setMaximum(100)
        xRate.setMinimum(0)
        xRate.setSingleStep(10)
        yRate.setMaximum(100)
        yRate.setMinimum(0)
        yRate.setSingleStep(10)
        xRate.setValue(0)
        yRate.setValue(0)

        self.xRate = xRate
        self.yRate = yRate

        group = QGroupBox("fix rate")
        grid =QGridLayout()

        grid.addWidget(xRate,0,0)
        grid.addWidget(yRate,1,0)

        group.setLayout(grid)

        self.fpsLabel = fpsLabel
        self.moveLabel = moveLabel

        enginegroup = QGroupBox("推理框架")

        grid =QGridLayout()

        ordmlBTN = QRadioButton("onnxruntime DirectML (AMD-GPU)") #onnxruntime dml (GPU)
        ovinoBTN = QRadioButton("OpenVINO (CPU)") #openvino (CPU)
        ptorchBTN = QRadioButton("PyTorch (CPU/CUDA)") #pytorch
        tensortBTN = QRadioButton("TensortRT (CUDA)") #pytorch

        self.ordmlBTN = ordmlBTN 
        self.ovinoBTN = ovinoBTN 
        self.ptorchBTN = ptorchBTN
        self.tensortBTN = tensortBTN

        grid.addWidget(ordmlBTN, 0,0)
        grid.addWidget(ovinoBTN, 0,1)
        grid.addWidget(ptorchBTN, 1,0)
        grid.addWidget(tensortBTN, 1,1)

        enginegroup.setLayout(grid)

        airegion = QSlider(Qt.Orientation.Horizontal)
        airegion.setMaximum(50)
        airegion.setMinimum(0)
        airegion.setSingleStep(1)
        airegion.setValue(25)
        self.airegion = airegion

        fixregion = QSlider(Qt.Orientation.Horizontal)
        fixregion.setMaximum(100)
        fixregion.setMinimum(0)
        fixregion.setSingleStep(1)
        fixregion.setValue(30)
        self.fixregion = fixregion

        regiongroup = QGroupBox("区域设置")
        grid =QGridLayout()
        grid.addWidget(airegion,0,0)
        grid.addWidget(fixregion,1,0)
        regiongroup.setLayout(grid)


        grid =QGridLayout()


        # self.c = Communicate()
        # self.c.updateFPS.connect(self.updateFPS)
        # self.c.updateImage.connect(self.updateImage)
        # self.c.updateMOVE.connect(self.updateMove)

        # thread = QThread(parent=self)
        # self.recoginizer = Recognizer(Recognizer.RecType.BLOODFIX,self.c,0.001)
        # self.recoginizer.moveToThread(thread)
        # self.recoginizer.start.emit(False)
        # thread.start()

        grid.addWidget(imgLabel,0,0)
        grid.addWidget(moveLabel,1,0)
        grid.addWidget(enginegroup,2,0)
        grid.addWidget(group,3,0)
        grid.addWidget(regiongroup,4,0)
        grid.addWidget(fpsLabel,5,0)
        grid.addWidget(startBtn,5,1)

        self.setLayout(grid)


    def set_fps(self,fps):
        self.fpsLabel.setText(str.format("{} fps",fps))

    def set_img(self, img):
        self.imgLabel.setPixmap(qimg_to_qpix(img))

    def set_move(self,x,y):
        self.moveLabel.setText(str.format("x:{},y:{}",x,y))