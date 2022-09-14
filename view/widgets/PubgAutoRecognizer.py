from model.Settings import Settings
from myutils.QtUtils import set_label_img,qimg_to_qpix
from controller.PubgRecognizeController import AIRecognizeController, AttachmentRecognizeController, BloodRecognizeController, PoseRecognizeController, WeaponRecognizeController


from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QCheckBox,QSlider,QGroupBox,QLineEdit,QPushButton,QRadioButton
from PyQt6.QtCore import Qt
from superqt.sliders import QLabeledRangeSlider,QLabeledDoubleSlider

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

        # xRate = QSlider(Qt.Orientation.Horizontal)
        # yRate = QSlider(Qt.Orientation.Horizontal)
        xRate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        yRate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        xRate.setMaximum(5)
        xRate.setMinimum(0)
        yRate.setMaximum(1)
        yRate.setMinimum(0)
        xRate.setValue(1)
        yRate.setValue(0)

        self.xRate = xRate
        self.yRate = yRate

        # h = QSlider(Qt.Orientation.Horizontal)
        # h.setMaximum(180)
        # h.setMinimum(0)
        # h.setSingleStep(1)
        # h.setValue(156)
        # s = QSlider(Qt.Orientation.Horizontal)
        # s.setMaximum(255)
        # s.setMinimum(0)
        # s.setSingleStep(1)
        # s.setValue(43)
        # v = QSlider(Qt.Orientation.Horizontal)
        # v.setMaximum(255)
        # v.setMinimum(0)
        # v.setSingleStep(1)
        # v.setValue(46)
        # self.h=h
        # self.s=s
        # self.v=v
        hslider = QLabeledRangeSlider()
        hslider.setMinimum(0)
        hslider.setMaximum(255)
        hslider.setValue((156, 180))
        hslider.setSingleStep(1)
        hslider.setOrientation(Qt.Orientation.Horizontal)
        sslider = QLabeledRangeSlider()
        sslider.setMaximum(255)
        sslider.setMinimum(0)
        sslider.setSingleStep(1)
        sslider.setValue((43, 255))
        sslider.setOrientation(Qt.Orientation.Horizontal)
        vslider = QLabeledRangeSlider()
        vslider.setMaximum(255)
        vslider.setMinimum(0)
        vslider.setSingleStep(1)
        vslider.setValue((43, 255))
        vslider.setOrientation(Qt.Orientation.Horizontal)
        self.h=hslider
        self.s=sslider
        self.v=vslider

        grouphsv = QGroupBox("HSV颜色调整")
        gridhsv =QGridLayout()
        gridhsv.addWidget(hslider,0,0)
        gridhsv.addWidget(sslider,1,0)
        gridhsv.addWidget(vslider,2,0)
        grouphsv.setLayout(gridhsv)

        
        group = QGroupBox("X/Y 修正强度")
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

        xRate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        yRate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        xRate.setMaximum(5)
        xRate.setMinimum(0)
        yRate.setMaximum(1)
        yRate.setMinimum(0)
        xRate.setValue(0.2)
        yRate.setValue(0)

        self.xRate = xRate
        self.yRate = yRate

        group = QGroupBox("X/Y 修正强度")
        grid =QGridLayout()

        grid.addWidget(xRate,0,0)
        grid.addWidget(yRate,1,0)

        group.setLayout(grid)

        self.fpsLabel = fpsLabel
        self.moveLabel = moveLabel

        enginegroup = QGroupBox("推理框架")

        grid =QGridLayout()

        ordmlBTN = QRadioButton("onnxruntime DirectML (AMD-GPU)") #onnxruntime dml (GPU)
        ordmlBTN.setChecked(True)
        ovinoBTN = QRadioButton("OpenVINO (CPU)") #openvino (CPU)
        ptorchBTN = QRadioButton("PyTorch (CPU/CUDA)") #pytorch
        tensortBTN = QRadioButton("TensortRT (CUDA)") #pytorch

        self.ordmlBTN = ordmlBTN 
        self.ovinoBTN = ovinoBTN 
        self.ptorchBTN = ptorchBTN
        self.tensortBTN = tensortBTN

        grid.addWidget(ordmlBTN, 0,0)
        grid.addWidget(ovinoBTN, 0,1)
        # grid.addWidget(ptorchBTN, 1,0)
        # grid.addWidget(tensortBTN, 1,1)

        enginegroup.setLayout(grid)

        airegion = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        airegion.setMaximum(0.5)
        airegion.setMinimum(0)
        airegion.setSingleStep(1)
        airegion.setValue(0.25)
        self.airegion = airegion

        fixregion = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        fixregion.setMaximum(5)
        fixregion.setMinimum(0)
        fixregion.setValue(1.5)
        self.fixregion = fixregion

        regiongroup = QGroupBox("检测/修正 区域设置")
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