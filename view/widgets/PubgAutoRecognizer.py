from model.Settings import Settings
from myutils.QtUtils import set_label_img,qimg_to_qpix
from controller.PubgRecognizeController import  AttachmentRecognizeController,  PoseRecognizeController, WeaponRecognizeController


from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QCheckBox,QSlider,QGroupBox,QLineEdit,QPushButton,QRadioButton
from PyQt6.QtCore import Qt

class PubgAutoRecognizer(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setUI()

    def setUI(self):
        grid = QGridLayout()

        prec = QPoseRecognizer()
        arec = QAttachmentRecognizer()
        wrec = QWeaponRecognizer()
        # http = QHttpServer()


        grid.addWidget(prec, 0, 0)
        grid.addWidget(wrec, 0, 1)
        grid.addWidget(arec, 0, 2)
        # monitors = QComboBox()
        # monitors.addItem("显示器1")
        # monitors.addItem("显示器2")
        # grid.addWidget(monitors,1,0)
        # grid.addWidget(http, 2, 0)

        self.setLayout(grid)

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

class QPoseRecognizer(QRecognizer):


    def __init__(self) -> None:
        super().__init__()
        self.controller = PoseRecognizeController(self,True)

    def setUI(self):
        # self.labelPosegrab = QLabel('pose grab')

        self.labelPose = QLabel('pose')
        set_label_img(self.labelPose, Settings().resource_dir+'pose_null.png')
        self.labelAccuracy = QLabel("1")

        self.screenshotBtn = QPushButton("截图")

        self.accuracy = QLineEdit("0.5")

        self.fpsText = QLabel('fps')

        self.startBtn = QCheckBox("disable")

        timeSlider = QSlider(Qt.Orientation.Horizontal)
        timeSlider.setMaximum(500)
        timeSlider.setMinimum(0)
        timeSlider.setValue(50)
        self.timeSlider = timeSlider

        #layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.labelPose,0,0,4,1)
        # grid.addWidget(self.labelAccuracy,0,1,4,1)
        grid.addWidget(self.screenshotBtn,4,0,1,2)
        grid.addWidget(self.accuracy,5,0,1,2)
        grid.addWidget(self.fpsText,6,0,1,2)
        grid.addWidget(self.timeSlider,7,0,1,2)
        grid.addWidget(self.startBtn,8,0,1,2)
        self.setLayout(grid)

    def set_fps(self,fps):
        self.fpsText.setText(str(fps)+"fps")

    def set_img(self, imgpath):
        set_label_img(self.labelPose,imgpath)

    def set_similarity(self,similarity:float):
        self.labelAccuracy.setText("精确度{:.2f}".format(similarity))
    
    def set_tips(self,s):
        self.labelPose.setToolTip(s)

class QWeaponRecognizer(QRecognizer):


    def __init__(self) -> None:
        super().__init__()

        self.controller = WeaponRecognizeController(self,True)

    def setUI(self):

        # self.labelWeapongrab = QLabel('weapon grab')

        self.labelWeapon2 = QLabel('weapon2')
        set_label_img(self.labelWeapon2, Settings().resource_dir+"weapon_null.png")
        self.labelAccuracy2 = QLabel("1")

        self.labelWeapon1 = QLabel('weapon1')
        set_label_img(self.labelWeapon1, Settings().resource_dir+"weapon_null.png")
        self.labelAccuracy1 = QLabel("1")

        self.screenshotBtn = QPushButton("截图")

        self.accuracy = QLineEdit("0.5")

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
        # grid.addWidget(self.labelAccuracy2,0,1,2,1)
        grid.addWidget(self.labelWeapon1,2,0,2,1)
        # grid.addWidget(self.labelAccuracy1,2,1,2,1)
        grid.addWidget(self.screenshotBtn,4,0,1,2)
        grid.addWidget(self.accuracy,5,0,1,2)
        grid.addWidget(self.fpsText,6,0,1,2)
        grid.addWidget(self.timeSlider,7,0,1,2)
        grid.addWidget(self.startBtn,8,0,1,2)

        self.setLayout(grid)
    
    def set_fps(self, fps:int):
        self.fpsText.setText(str(fps)+"fps")
    
    def set_img1(self,imgpath):
        set_label_img(self.labelWeapon1, imgpath)

    def set_img2(self,imgpath):
        set_label_img(self.labelWeapon2, imgpath)

    def set_similarity(self,similarity:float,num):
        if num == 1:
            self.labelAccuracy1.setText("精确度{:.2f}".format(similarity))
        if num == 2:
            self.labelAccuracy2.setText("精确度{:.2f}".format(similarity))

    def set_tips(self,s,num):
        if num==1:
            self.labelWeapon1.setToolTip(s)
        elif num==2:
            self.labelWeapon2.setToolTip(s)

class QAttachmentRecognizer(QRecognizer):

    result1 = None
    result2 = None

    def __init__(self) -> None:
        super().__init__()

        self.controller = AttachmentRecognizeController(self,True)

    def setUI(self):
        # self.label1 = QLabel('scope grab')
        # self.label2 = QLabel('attachment1 grab')
        # self.label3 = QLabel('attachment2 grab')
        # self.label4 = QLabel('attachment3 grab')
        # self.label5 = QLabel('attachment4 grab')


        self.r2label1 = QLabel('scope grab')
        self.r2label2 = QLabel('attachment1 grab')
        self.r2label3 = QLabel('attachment2 grab')
        self.r2label4 = QLabel('attachment3 grab')
        self.r2label5 = QLabel('attachment4 grab')

        self.r1label1 = QLabel('scope grab')
        self.r1label2 = QLabel('attachment1 grab')
        self.r1label3 = QLabel('attachment2 grab')
        self.r1label4 = QLabel('attachment3 grab')
        self.r1label5 = QLabel('attachment4 grab')

        self.labelAccuracy11 = QLabel("1")
        self.labelAccuracy12 = QLabel("1")
        self.labelAccuracy13 = QLabel("1")
        self.labelAccuracy14 = QLabel("1")
        self.labelAccuracy15 = QLabel("1")
        self.labelAccuracy21 = QLabel("1")
        self.labelAccuracy22 = QLabel("1")
        self.labelAccuracy23 = QLabel("1")
        self.labelAccuracy24 = QLabel("1")
        self.labelAccuracy25 = QLabel("1")

        [ set_label_img(l,Settings().resource_dir+"attachments/null.png") for l in [self.r1label1, self.r1label2, self.r1label3, self.r1label4, self.r1label5]]
        [ set_label_img(l,Settings().resource_dir+"attachments/null.png") for l in [self.r2label1, self.r2label2, self.r2label3, self.r2label4, self.r2label5]]

        self.screenshotBtn = QPushButton("截图")

        self.accuracy = QLineEdit("0.9")
        self.fpsText = QLabel('fps')
        self.startBtn = QCheckBox("disable")
        timeSlider = QSlider(Qt.Orientation.Horizontal)
        timeSlider.setMaximum(500)
        timeSlider.setMinimum(0)
        timeSlider.setValue(100)
        self.timeSlider = timeSlider

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.r2label1,0,0)
        # grid.addWidget(self.labelAccuracy21,0,1)
        grid.addWidget(self.r2label2,1,0)
        # grid.addWidget(self.labelAccuracy22,1,1)
        grid.addWidget(self.r2label3,1,2)
        # grid.addWidget(self.labelAccuracy23,1,3)
        grid.addWidget(self.r2label4,1,4)
        # grid.addWidget(self.labelAccuracy24,1,5)
        grid.addWidget(self.r2label5,1,6)
        # grid.addWidget(self.labelAccuracy25,1,7)

        grid.addWidget(self.r1label1,2,0)
        # grid.addWidget(self.labelAccuracy11,2,1)
        grid.addWidget(self.r1label2,3,0)
        # grid.addWidget(self.labelAccuracy12,3,1)
        grid.addWidget(self.r1label3,3,2)
        # grid.addWidget(self.labelAccuracy13,3,3)
        grid.addWidget(self.r1label4,3,4)
        # grid.addWidget(self.labelAccuracy14,3,5)
        grid.addWidget(self.r1label5,3,6)
        # grid.addWidget(self.labelAccuracy15,3,7)

        grid.addWidget(self.screenshotBtn,4,0,1,8)
        grid.addWidget(self.accuracy,5,0,1,8)
        grid.addWidget(self.fpsText,6,0,1,8)
        grid.addWidget(self.timeSlider,7,0,1,8)
        grid.addWidget(self.startBtn,8,0,1,8)

        self.setLayout(grid)

        # self.c = AttachmentCommunicate()
        # self.c.updateResult.connect(self.updateResult)
        # self.c.updateFPS.connect(self.updateFPS)
        # # self.c.updateIMG.connect(self.updateIMG)
        # self.c.updateIMG2.connect(self.updateIMG2)
        # self.c.changeWeapon.connect(self.changeWeapon)
        
        # self.thread = QThread(parent=self)
        # self.recoginizerweapon = Recognizer(Recognizer.RecType.ATTACHMENT,self.c,0.1)
        # self.recoginizerweapon.moveToThread(self.thread)
        # self.recoginizerweapon.start.emit(True)
        # self.thread.start()

    def set_fps(self,fps):
        self.fpsText.setText(str(fps)+"fps")

    def set_attachment1(self, i, imgpath,similarity):
        labels = [self.r1label1, self.r1label2, self.r1label3, self.r1label4, self.r1label5]
        set_label_img(labels[i], imgpath)
        accuracys = [self.labelAccuracy11,self.labelAccuracy12,self.labelAccuracy13,self.labelAccuracy14,self.labelAccuracy15]
        if similarity:
            accuracys[i].setText("{:.2f}".format(similarity))
        else:
            accuracys[i].setText("{:.2f}".format(1))

    def set_attachment2(self, i, imgpath,similarity):
        labels = [self.r2label1, self.r2label2, self.r2label3, self.r2label4, self.r2label5]
        set_label_img(labels[i], imgpath)
        accuracys = [self.labelAccuracy21,self.labelAccuracy22,self.labelAccuracy23,self.labelAccuracy24,self.labelAccuracy25]
        if similarity:
            accuracys[i].setText("{:.2f}".format(similarity))
        else:
            accuracys[i].setText("{:.2f}".format(1))

    def set_tips(self,index,s,num):
        labels1 = [self.r1label1, self.r1label2, self.r1label3, self.r1label4, self.r1label5]
        labels2 = [self.r2label1, self.r2label2, self.r2label3, self.r2label4, self.r2label5]
        if num==1:
            labels1[index].setToolTip(s)
        elif num==2:
            labels2[index].setToolTip(s)