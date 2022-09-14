
import os
import sys
from PyQt6.QtCore import QObject, QThread
from PyQt6.QtGui import QPixmap,QImageReader
from PyQt6.QtWidgets import QMessageBox

from myutils.IMGutil import cv_img_to_qimg

def start_q_thread(parent,object:QObject,start=True):
    thread = QThread(parent)

    object.moveToThread(thread)

    if start:
        if 'start' in dir(object):
            object.start.emit(True)
    else:
        object.start.emit(False)
    thread.start()

def set_label_img(label,path_or_img):
    if isinstance(path_or_img,str):
        reader = QImageReader(path_or_img)
        img = QPixmap.fromImageReader(reader)
        label.setPixmap(img)
    else:
        qimg = cv_img_to_qimg(path_or_img)
        img = QPixmap.fromImage(qimg)
        label.setPixmap(img)

def qimg_to_qpix(qimg):
    return QPixmap.fromImage(qimg)

def message_info(title:str, message:str):
    QMessageBox.information(None,title,message)

def message_critical(title:str, message:str):
    QMessageBox.critical(None,title,message)

def appexit():
    sys.exit()

def apprestart():
    message_info("提示","即将重启")
    p = sys.executable
    os.execl(p,p,*sys.argv)