from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout,QPushButton,QLineEdit,QSlider,QCheckBox
from PyQt6.QtCore import Qt
from model.Settings import Settings

from myutils.QtUtils import set_label_img
from controller.ApexRecognizeController import  WeaponRecognizeController

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
