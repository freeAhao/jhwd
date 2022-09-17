import os
import cv2
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout,QFileDialog,QPushButton,QScrollArea,QLineEdit,QTextEdit,QSlider,QInputDialog,QCheckBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from superqt import QLabeledDoubleSlider
import numpy as np
from model.Settings import Settings

from myutils.IMGutil import cv_img_to_qimg, qt_img_to_cv

class ImageRecoilAnalyze(QWidget):

    dresult = None
    qimg = None
    cvimg = np.zeros([3])
    datas = []

    def __init__(self) -> None:
        super().__init__()

        selectbutton = QPushButton()
        selectbutton.setText("选择弹道截图")
        selectbutton.clicked.connect(self.select_file)
        self.selectbutton = selectbutton

        self.debugBox = QCheckBox("DEBUG模式弹道")
        self.debugBox.setChecked(Settings().app_config["game"]=="PUBG")
        self.debugBox.stateChanged.connect(self.render)

        self.pathLabel = QLabel()
        self.avgLabel = QLabel()

        imgArea = QScrollArea()
        imgArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imgArea.setWidgetResizable(True)
        self.imgArea = imgArea

        textEdit = QTextEdit()
        self.textEdit = textEdit

        # xrate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        # yrate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        # xrate.setMaximum(100)
        # xrate.setMinimum(0)
        # xrate.setValue(1)
        # yrate.setMaximum(100)
        # yrate.setMinimum(0)
        # yrate.setValue(1)
        # xrate.valueChanged.connect(self.render)
        # yrate.valueChanged.connect(self.render)
        # self.xrate = xrate
        # self.yrate = yrate

        imagelabel = QLabel()
        self.imagelabel = imagelabel
        self.imgArea.setWidget(imagelabel)
        self.imagelabel.setObjectName("image")
        self.imagelabel.mousePressEvent = self.image_click

        #layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(selectbutton,1,0)
        grid.addWidget(self.pathLabel,2,0)
        grid.addWidget(self.avgLabel,3,0)
        grid.addWidget(self.debugBox,4,0)
        # grid.addWidget(self.yrate,5,0)
        # grid.addWidget(self.xrate,6,0)
        grid.addWidget(self.imgArea,5,0)
        grid.addWidget(self.textEdit,5,1)

        self.setLayout(grid)

    def select_file(self):
        path = os.path.expanduser("~")
        fname = QFileDialog.getOpenFileName(self,'select file',path)
        if not (fname and (fname[0].endswith("png") or fname[0].endswith("jpg"))):
            return None

        path = fname[0]
        self.pathLabel.setText(path+"\n左键添加 右键删除 中键修改子弹数")

        qimg = QPixmap(path)
        self.cvimg = qt_img_to_cv(qimg)
        self.imagelabel.setPixmap(qimg)
        self.datas = []
    
    def render(self):
        debug = self.debugBox.isChecked()
        if debug:
            datas = sorted(self.datas,key=lambda x:int(x[0]))
        else:
            datas = self.datas

        img = self.cvimg.copy()

        for i,data in enumerate(datas):
            cv2.putText(img,str(data[2]),(data[0]-10,data[1]-10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
            cv2.rectangle(img,(data[0]-5,data[1]-5),(data[0]+5,data[1]+5),(0,255,0),2)
            if i != 0 :
                cv2.line(img,(data[0],data[1]),(datas[i-1][0],datas[i-1][1]),(0,255,0),2)
        self.imagelabel.setPixmap(QPixmap(cv_img_to_qimg(img)))

        result = ""
        try:
            for i,data in enumerate(datas):
                if i !=0:
                    x0 = datas[i-1][0]
                    y0 = datas[i-1][1]
                    num0 = datas[i-1][2]
                    x1 = data[0]
                    y1 = data[1]
                    num1 = data[2]

                    movey = (y0-y1)/(num1-num0)
                    if debug:
                        movex = 0
                    else:
                        movex = (x0-x1)/(num1-num0)
                    s = "{{{},{:.4f},{:.4f}}}\n".format(num0,movey,movex)
                    result += s
                if i == len(datas)-1:
                    num = datas[-1][2]
                    result += "{{{},0,0}}\n".format(num)
        except:
            result = "数据错误"

        self.textEdit.setText(result)

    def image_click(self, event):
        if not self.cvimg.any():
            return

        debug = self.debugBox.isChecked()

        if event.buttons() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            if x > self.cvimg.shape[1] or y > self.cvimg.shape[0]:
                return
            for i,data in enumerate(self.datas):
                if x >= data[0]-5 and x <= data[0]+5:
                    if y >= data[1]-5 and y<= data[1]+5:
                        # 点击存在的点 忽略
                        break
                    if debug:
                        # debug模式 x相同 修改原点信息
                        newdata = [x,y,self.datas[i][2]]
                        self.datas[i] = newdata
                        break
                    else:
                        self.datas.append([x,y,len(self.datas)+1])
                        break
            else:
                self.datas.append([x,y,len(self.datas)+1])

        if event.buttons() == Qt.MouseButton.RightButton:
            x = event.pos().x()
            y = event.pos().y()
            for i,data in enumerate(self.datas):
                if x >= data[0]-5 and x <= data[0]+5:
                    if y >= data[1]-5 and y <= data[1]+5:
                        self.datas.pop(i)
                        break
        if event.buttons() == Qt.MouseButton.MiddleButton:
            x = event.pos().x()
            y = event.pos().y()
            for i,data in enumerate(self.datas):
                if x >= data[0]-5 and x <= data[0]+5:
                    if y >= data[1]-5 and y <= data[1]+5:
                        num, ok = QInputDialog.getText(self, '子弹数', '输入:')
                        if ok and int(num):
                            self.datas[i][2] = int(num) 
                        break
        self.render()
