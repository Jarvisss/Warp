import cv2
import numpy as np
from PyQt5.QtGui import QImage


def cv_toQimage(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    height, width, channel = cv_img.shape
    bytesPerLine = 3 * width
    q_img = QImage(cv_img.data, width
                   , height, bytesPerLine, QImage.Format_RGB888)
    return q_img

def q_toCVimage(q_img):
    q_img = q_img.convertToFormat(QImage.Format_RGBA8888)
    w,h = q_img.width(),q_img.height()
    ptr = q_img.bits()
    ptr.setsize(w*h*4)
    arr = np.frombuffer(ptr,np.uint8).reshape((h, w, 4))
    cv_img = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
    return cv_img


def cv_imread(filePath):
    cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.float32),-1)
    ## imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
    # cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
    return cv_img

def rectContains(rect,pt):
    logic = rect[0] <= pt[0] < rect[0]+rect[2] and rect[1] <= pt[1] < rect[1]+rect[3]
    return logic


def sample_line(pstart, pend, samples):
    pts = []
    segments = samples+1
    delta = (pend[0] - pstart[0], pend[1]-pstart[1])
    delta_step = (delta[0] / segments, delta[1] / segments)
    for i in range(1, samples+1):
        pts.append((int(pstart[0]+delta_step[0]*i), int(pstart[1]+delta_step[1]*i)))

    return pts

def sample_rect(rect, samples):
    (left, top, w, h) = rect
    pts = []

    right = left + w - 1
    bottom = top + h - 1

    pts.append((left,top))
    pts.append((left,bottom))
    pts.append((right,bottom))
    pts.append((right,top))

    pts = pts + sample_line((left, top), (left, bottom),samples)
    pts = pts + sample_line((left, bottom), (right, bottom),samples)
    pts = pts + sample_line((right, bottom), (right, top), samples)
    pts = pts + sample_line((right, top), (left, top), samples)

    return pts


if __name__ == '__main__':
    fp = './samples/qie.jpg'
    cvim = cv_imread(fp)
    cv2.imshow('before', cvim)
    cv2.waitKey()
    qimg = cv_toQimage(cvim)
    cvimg = q_toCVimage(qimg)
    cv2.imshow('before', cvim)
    cv2.waitKey()
