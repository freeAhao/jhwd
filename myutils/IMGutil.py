import math
import numpy as np
import cv2 as cv
from mss import mss
from mss import tools as msstools
from PyQt6.QtGui import QImage



sct = mss()

# 截图
def screenshot(box):
    shot = sct.grab(box)
    return shot

def full_screenshot(screenum=1):
    shot = sct.grab(sct.monitors[screenum])
    return np.array(shot)

def get_screen_nums():
    return sct.monitors

def pHash(img):
    # 感知哈希算法
    # 缩放32*32
    img = cv.resize(img, (32, 32))   # , interpolation=cv2.INTER_CUBIC

    # 转换为灰度图
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash

def dHash(img):
    # 差值哈希算法
    # 缩放8*8
    img = cv.resize(img, (9, 8))
    # 转换灰度图
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j+1]:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    return hash_str

# 对比图片特征点
# 均值哈希算法
def aHash(img):
    # 缩放为8*8
    img = cv.resize(img, (8, 8))
    # 转换为灰度图
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    hash_str = ''
    # 遍历累加求像素和
    for i in range(8):
        for j in range(8):
            s = s + gray[i, j]
    # 求平均灰度
    avg = s / 64
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str

# # Hash值对比
def cmpHash(hash1, hash2):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1)!=len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n

resource_hash_table = {}
# 资源匹配
def similarity(im, resource_list,jqd,printJQD=False):
    im = np.array(im, dtype=np.uint8)
    pp_table = {}
    for resource_img in resource_list:
        if not str(resource_img).endswith(".png"):
            continue
        # 缓存资源图片hash计算结果
        if resource_img not in resource_hash_table.keys():
            img1 = cv.imread(resource_img)

            hash1 = pHash(img1)
            resource_hash_table[resource_img] = hash1
        else:
            hash1 = resource_hash_table[resource_img]
        # img2 = cv.cvtColor(im)
        img2 = im
        hash2 = pHash(img2)
        result = cmpHash(hash1, hash2)

        if result not in pp_table.keys():
            pp_table[result]=resource_img
        else:
            if isinstance(pp_table[result],list):
                pp_table[result].append(resource_img)
            else:
                pp_table[result] = [pp_table[result], resource_img]
    results = list(pp_table.keys())
    results.sort()

    if printJQD:
        print(results[0])

    if len(results)>0 and results[0] <= jqd:
    # if len(results)>0 and results[0]:
        if isinstance(pp_table[results[0]],list):
            # print("多个匹配图像",pp_table[results[0]])
            return True, pp_table[results[0]][0], results[0]
        return True, pp_table[results[0]], results[0]
    return False,None,None

def cv_match(img,resource_list,acc):
    datas = []

    for resource in resource_list:
        template = resource_list[resource]
        # img = np.asarray(img)
        # img = cv.cvtColor(img,cv.COLOR_RGB2BGR)
        result = cv.matchTemplate(img, template, cv.TM_SQDIFF_NORMED)
        min, _,_,_ = cv.minMaxLoc(result)
        if min > 0:
            datas.append((min,resource))
    datas.sort(key=lambda x:float(x[0]))
    if len(datas)>0 and datas[0][0] < acc:
        return True, datas[0][1],datas[0][0]
    return False,None,None

def screenshot_to_cv(screenshot):
    cvimg = np.array(screenshot,dtype=np.uint8)
    # cvimg = cv.cvtColor(cvimg, cv.COLOR_RGB2BGR)
    return cvimg


def pil_to_cv(pimg):
    open_cv_image = np.array(pimg) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() 
    return open_cv_image


def find_center(img):
    center = [960,540]
    for h in range(center[1]-100,center[1]+100):
        for l in range(center[0]-50, center[0]+50):
            dot  = (l,h)
            color  = img.getpixel(dot)
            if color[0] > 250 and color[1] > 200 and color[2] > 150 :
                return True, dot
    else:
        return False, None


def cv_img_to_qimg(img):
    img = cv.cvtColor(img,cv.COLOR_BGR2RGB)
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
    return qImg

def qt_img_to_cv(qimg):
    width = qimg.width()
    height = qimg.height()
    qimg = qimg.toImage()

    s = qimg.bits().asstring(width * height * 4)
    arr = np.fromstring(s, dtype=np.uint8).reshape((height, width, 4)) 
    return arr

def video_to_img_list(video_path, timeF):
    vc = cv.VideoCapture(video_path)
    n = 1
    if vc.isOpened():  # 判断是否正常打开
        rval, frame = vc.read()
    else:
        rval = False
        
    i = 0
    imglist = []
    while rval:  # 循环读取视频帧
        rval, frame = vc.read()
        if (n % timeF == 0):  # 每隔timeF帧进行存储操作
            i += 1
            try:
                # cv.imwrite('framesplit/{}.jpg'.format(i), frame)  # 存储为图像
                imglist.append(frame)
            except Exception as e:
                print(e)
                continue
        n = n + 1
    vc.release()
    return imglist

def analyze_position(cvimg):
    x=0
    y=0
    d=0
    return x,y,d

def to_black_white(cvimg):
    b=cvimg[:,:,0]
    g=cvimg[:,:,1]
    r=cvimg[:,:,2]
    blackwhite = np.where(((b>200)&(g>200)&(r>200)),255,0)
    blackwhite = cv.merge((blackwhite,blackwhite,blackwhite))
    blackwhite = blackwhite.astype(np.uint8)
    return blackwhite

def to_black_white2(cvimg):
    b=cvimg[:,:,0]
    g=cvimg[:,:,1]
    r=cvimg[:,:,2]
    blackwhite = np.where(((b<30)&(g<30)&(r<30)),255,0)
    blackwhite = cv.merge((blackwhite,blackwhite,blackwhite))
    blackwhite = blackwhite.astype(np.uint8)
    return blackwhite

def resize_img(cvimg, resize_rate):
    if resize_rate != 1:
        height,width,_= cvimg.shape
        icon_scale = width/height
        newHeight = math.ceil(height/resize_rate)
        newWidth = math.ceil(icon_scale*newHeight)
        cvimg = cv.resize(cvimg,(newWidth,newHeight))
    return cvimg