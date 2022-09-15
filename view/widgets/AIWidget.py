
from model.Settings import Settings
from myutils.QtUtils import set_label_img,qimg_to_qpix
from controller.AiController import AIRecognizeController,BloodRecognizeController


from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QCheckBox,QSlider,QGroupBox,QLineEdit,QPushButton,QRadioButton
from PyQt6.QtCore import Qt
from superqt.sliders import QLabeledRangeSlider,QLabeledDoubleSlider

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