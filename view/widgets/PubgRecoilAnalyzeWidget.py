import os
import cv2
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout,QFileDialog,QPushButton,QScrollArea,QLineEdit,QTextEdit,QSlider,QInputDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from superqt import QLabeledDoubleSlider
import numpy as np

from myutils.IMGutil import cv_img_to_qimg, qt_img_to_cv

class ImageRecoilAnalyze(QWidget):

    dresult = None
    qimg = None

    def __init__(self) -> None:
        super().__init__()

        selectbutton = QPushButton()
        selectbutton.setText("Choose File")
        selectbutton.clicked.connect(self.select_file)
        self.selectbutton = selectbutton

        self.pathLabel = QLabel()
        self.avgLabel = QLabel()

        imgArea = QScrollArea()
        imgArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imgArea.setWidgetResizable(True)
        self.imgArea = imgArea

        textEdit = QTextEdit()
        self.textEdit = textEdit

        xrangeSlider = QSlider(Qt.Orientation.Horizontal)
        yrangeSlider = QSlider(Qt.Orientation.Horizontal)

        xrangeSlider.valueChanged.connect(self.get_detect_range)
        yrangeSlider.valueChanged.connect(self.get_detect_range)

        self.xrangeSlider = xrangeSlider
        self.yrangeSlider = yrangeSlider

        xoffset = QSlider(Qt.Orientation.Horizontal)
        yoffset = QSlider(Qt.Orientation.Horizontal)

        xoffset.valueChanged.connect(self.get_detect_range)
        yoffset.valueChanged.connect(self.get_detect_range)

        self.xoffset = xoffset
        self.yoffset = yoffset


        imagelabel = QLabel()
        self.imagelabel = imagelabel
        self.imgArea.setWidget(imagelabel)

        calButton = QPushButton("analyze")
        calButton.clicked.connect(self.analyze)

        bulletRGBEdit = QLineEdit()
        bulletRGBEdit.setText("50 50 50")
        self.bulletRGBEdit = bulletRGBEdit

        bulletSize = QLineEdit()
        bulletSize.setText("5")
        self.bulletSize = bulletSize

        rate = QSlider(Qt.Orientation.Horizontal)
        rate.setMaximum(200)
        rate.setMinimum(0)
        rate.setTickInterval(1)
        rate.setValue(100)
        rate.valueChanged.connect(self.change_rate)
        self.rate = rate

        #layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(selectbutton,1,0)
        grid.addWidget(self.pathLabel,2,0)
        grid.addWidget(xrangeSlider,3,0)
        grid.addWidget(yrangeSlider,3,1)
        grid.addWidget(calButton,3,2)
        grid.addWidget(xoffset,4,0)
        grid.addWidget(yoffset,4,1)
        grid.addWidget(self.avgLabel,5,0)
        grid.addWidget(self.bulletRGBEdit,6,0)
        grid.addWidget(self.bulletSize,6,1)
        grid.addWidget(self.rate,6,2)
        grid.addWidget(self.imgArea,7,0,1,2)
        grid.addWidget(self.textEdit,7,2)

        self.setLayout(grid)

        # self.c = Communicate()
        # self.c.updateWeapon.connect(self.updateWeapon)
        # self.c.updatePose.connect(self.updatePose)
        # self.c.updateUI.connect(self.updateUI)
        
        # self.thread = QThread(parent=self)

        # self.recoginizer = Recognizer(self.c)
        # self.recoginizer.moveToThread(self.thread)
        # self.recoginizer.start.emit(True)

        # self.thread.start()
    def select_file(self):
        path = os.path.expanduser("~")
        fname = QFileDialog.getOpenFileName(self,'select file',path)
        if not (fname and (fname[0].endswith("png") or fname[0].endswith("jpg"))):
            return None
        return fname
    
    def change_rate(self):
        resultavg = ""
        resultd = ""

        if not self.dresult:
            return

        for index,d in enumerate(self.dresult):
            txt = str.format("{{{},{},0}},\n",index+1, round(d*self.rate.value()/100))
            resultd += txt
            txt = str.format("{{{},{},0}},\n",index+1, round(self.avgresult[index]*self.rate.value()/100))
            resultavg += txt

        self.textEdit.setText(resultd + "\n" + resultavg)


    def analyze(self):
        if not self.qimg:
            return
        qimg = self.qimg
        cvimg = qt_img_to_cv(qimg)

        #分析区域
        p1,p2 = self.get_detect_range()

        count = 0
        img = cvimg[p1[1]:p2[1],p1[0]:p2[0],:]
        finded = []
        try:
            RGB = [int(i) for i in self.bulletRGBEdit.text().split(" ")]
        except:
            RGB = [50,50,50]
        try:
            bulletszie = int(self.bulletSize.text())
        except:
            bulletszie = 5

        # for y in range(p2[1]-p1[1],-1,-1):
        #     for x in range(0,p2[0]-p1[0],1):
        #         if y-1<0:
        #             continue
        #         dot = img[y-1,x,:3]
        #         if dot[0]<RGB[2] and dot[1]<RGB[1] and dot[2]<RGB[0]:
        #             for d in finded:
        #                 if x >= d[0]-bulletszie and x<=d[0]+bulletszie and y>=d[1]-bulletszie and y<=d[1]+bulletszie:
        #                     break
        #             else:
        #                 # print("添加",x,y)
        #                 finded.append((x,y))
        #                 cv2.rectangle(img, (x-2,y-2), (x+2,y+2),(0,255,0))
        #                 count += 1

        for x in range(0,p2[0]-p1[0],1):
            for y in range(p2[1]-p1[1],-1,-1):
                dot = img[y-1,x,:3]
                if dot[0]<=RGB[2] and dot[1]<=RGB[1] and dot[2]<=RGB[0]:
                    for d in finded:
                        if x >= d[0]-bulletszie and x<=d[0]+bulletszie and y>=d[1]-bulletszie and y<=d[1]+bulletszie:
                            break
                    else:
                        finded.append((x,y))
                        cv2.rectangle(img, (x-2,y-2), (x+2,y+2),(0,255,0))
                        # cv2.putText(img,str(count),(x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.1, (255, 255, 255), 2)
                        count += 1

        sum = 0
        avg = 0
        resultavg = ""
        resultd = ""
        self.avgresult = []
        self.dresult = []
        for index,d in enumerate(finded):
            if index==len(finded)-1:
                break
            nextdot = finded[index+1]
            d = -(nextdot[1]-d[1])
            sum =  d + sum
            avg = round(sum / (index+1))

            txt = str.format("{{{},{},0}},\n",index+1, avg)
            resultavg += txt
            txt = str.format("{{{},{},0}},\n",index+1, d)
            resultd += txt
            self.avgresult.append(avg)
            self.dresult.append(d)

        self.textEdit.setText(resultd + "\n" + resultavg)

        qimg = cv_img_to_qimg(cvimg)
        self.imagelabel.setPixmap(QPixmap.fromImage(qimg))

        # return cvimg, result
        
    def set_slider_range(self,maxwidth,maxheight):
        self.xrangeSlider.setMaximum(maxwidth)
        self.yrangeSlider.setMaximum(maxheight)
        self.xoffset.setMaximum(maxwidth)
        self.yoffset.setMaximum(maxheight)


    def analyze_picture(self):
        fname = self.select_file()
        if not fname:
            return

        path = fname[0]
        self.pathLabel.setText(path)

        qimg = QPixmap(path)
        self.qimg = qimg

        self.set_slider_range(qimg.width(),qimg.height())

        self.analyze()

    def get_detect_range(self):
        if not self.qimg:
            return
        qimg = self.qimg
        cvimg = qt_img_to_cv(qimg)
        xoffset = self.xoffset.value()
        yoffset = self.yoffset.value()
        # center=(round(qimg.width()/2+xoffset),round(qimg.height()/2+yoffset))
        xrange = self.xrangeSlider.value()
        yrange = self.yrangeSlider.value()

        p1=(xrange,yrange)
        p2=(xoffset,yoffset)

        cv2.rectangle(cvimg,p1,p2,(0,255,0))
        qimg = cv_img_to_qimg(cvimg)
        self.imagelabel.setPixmap(QPixmap.fromImage(qimg))
        return p1,p2

class ImageRecoilAnalyze2(QWidget):

    dresult = None
    qimg = None
    cvimg = np.zeros([3])
    datas = {}

    def __init__(self) -> None:
        super().__init__()

        selectbutton = QPushButton()
        selectbutton.setText("选择弹道截图")
        selectbutton.clicked.connect(self.select_file)
        self.selectbutton = selectbutton

        self.pathLabel = QLabel()
        self.avgLabel = QLabel()

        imgArea = QScrollArea()
        imgArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        imgArea.setWidgetResizable(True)
        self.imgArea = imgArea

        textEdit = QTextEdit()
        self.textEdit = textEdit

        rate = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
        rate.setMaximum(100)
        rate.setMinimum(0)
        rate.setValue(1)
        rate.valueChanged.connect(self.render)
        self.rate = rate

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
        grid.addWidget(self.rate,4,0)
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
        self.datas = {}
    
    def render(self):
        keys_sorted = list(self.datas.keys())
        keys_sorted = sorted(keys_sorted,key=lambda x:int(x))
        img = self.cvimg.copy()
        for i,x in enumerate(keys_sorted):
            y = self.datas[x][0]
            cv2.putText(img,str(self.datas[x][1]),(x-10,y-10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
            cv2.rectangle(img,(x-5,y-5),(x+5,y+5),(0,255,0),2)
            if i != 0 :
                cv2.line(img,(x,y),(keys_sorted[i-1],self.datas[keys_sorted[i-1]][0]),(0,255,0),2)
        self.imagelabel.setPixmap(QPixmap(cv_img_to_qimg(img)))

        result = ""
        try:
            for i,x in enumerate(keys_sorted):
                if i !=0:
                    y0 = self.datas[keys_sorted[i-1]][0]
                    num0 = self.datas[keys_sorted[i-1]][1]
                    y1 = self.datas[x][0]
                    num1 = self.datas[x][1]

                    s = "{{{},{},0}}\n".format(num0,round((y0-y1)*(self.rate.value()/100)/(num1-num0)))
                    result += s
                if i == len(keys_sorted)-1:
                    num = self.datas[keys_sorted[-1]][1]
                    result += "{{{},0,0}}\n".format(num)
        except:
            result = "数据错误"

        self.textEdit.setText(result)


    def image_click(self, event):
        if not self.cvimg.any():
            return
        
        if event.buttons() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            if x > self.cvimg.shape[1] or y > self.cvimg.shape[0]:
                return
            for i,xx in enumerate(self.datas):
                if x >= xx-5 and x <= xx+5:
                    return
                
            self.datas[x] = [y,len(self.datas)+1]

        if event.buttons() == Qt.MouseButton.RightButton:
            x = event.pos().x()
            y = event.pos().y()
            for i,xx in enumerate(self.datas):
                if x >= xx-5 and x <= xx+5:
                    if y >= self.datas[xx][0]-5 and y <= self.datas[xx][0]+5:
                        del self.datas[xx]
                        break
        if event.buttons() == Qt.MouseButton.MiddleButton:
            x = event.pos().x()
            y = event.pos().y()
            for i,xx in enumerate(self.datas):
                if x >= xx-5 and x <= xx+5:
                    if y >= self.datas[xx][0]-5 and y <= self.datas[xx][0]+5:
                        num, ok = QInputDialog.getText(self, '子弹数', '输入:')
                        if ok and int(num):
                            self.datas[xx][1] = int(num)
                        break
        self.render()
