from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel,QHBoxLayout,QVBoxLayout, QGridLayout, QLineEdit,QMessageBox
from PyQt5.QtGui import QPixmap
from cvhelper import cv_toQimage, sample_rect, q_toCVimage
from warp import warpTriangle, calculateDelaunayTriangles

import numpy as np
import cv2
import os

class ImageDrawLabel(QLabel):
    # dropImgSignal = pyqtSignal(object)

    def __init__(self, qimg, size):
        super(ImageDrawLabel, self).__init__()
        self.setFixedSize(size)
        self.size = size
        self.setPixmap(QPixmap(qimg.scaled(size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self._initUI()
        self.setMouseTracking(True)
        self.selected_stylesheet = \
            'border: 2px dashed black;\
            border-radius:10px;'
        self.no_selected_stylesheet = \
            ''
        self.selected = False
        pass

    def _initUI(self):

        self.setAlignment(Qt.AlignCenter)
        pass

    def mousePressEvent(self, ev):
        if ev.buttons() == Qt.LeftButton:
            self.selected = not self.selected
            if self.selected:
                self.setStyleSheet(self.selected_stylesheet)
            else:
                self.setStyleSheet(self.no_selected_stylesheet)
        pass



class MorphingResultWidget(QWidget):

    def __init__(self,ww,hh,lpts,rpts, lpm, rpm):
        super(MorphingResultWidget, self).__init__()
        self.lpixelMap, self.rpixelMap = lpm,rpm
        self.w = ww
        self.h = hh
        self.lpts = lpts
        self.rpts = rpts
        self.rwarps = []
        self.morphs = []
        self.image_ratio=3
        self.grid_spacing = 10
        self.grid_margin = 20
        self.grid_width = (self.w - 6 * self.grid_spacing - 2 * self.grid_margin) // 7
        self.rwarp_grids = []
        self.alphas = [1 / 6, 1 / 3, 1 / 2, 2 / 3, 5 / 6]
        self.morph_grids= []
        self._getMorphResults()
        self._initUI()
        self.download.clicked.connect(self._download)
        pass

    def _initUI(self):
        grid = QGridLayout()
        grid.setSpacing(self.grid_spacing)

        for i,rwarp in enumerate(self.rwarps):
            qrwarp = cv_toQimage(rwarp)
            qrwarp_label = ImageDrawLabel(qrwarp, QSize(self.grid_width, self.grid_width))
            self.rwarp_grids.append(qrwarp_label)
            grid.addWidget(qrwarp_label, 0, i)
            pass

        for i,morph in enumerate(self.morphs):
            qmorph = cv_toQimage(morph)
            qmorph_label = ImageDrawLabel(qmorph, QSize(self.grid_width, self.grid_width))
            self.morph_grids.append(qmorph_label)
            grid.addWidget(qmorph_label, 1, i)
            pass

        for i,alpha in enumerate(self.alphas):
            label = QLabel('%.4f'%alpha)
            grid.addWidget(label, 2, i, alignment=Qt.AlignCenter)
            pass


        self.button = QPushButton("回到首页")
        self.button.setMinimumSize(200, 50)
        self.download = QPushButton("下载图片")
        self.download.setMinimumSize(200, 50)
        self.path = QLineEdit()
        self.path.setPlaceholderText("输入下载文件夹名称(默认yymmdd_hhmmss, 200420_114432)")
        self.path.setMinimumSize(400, 50)

        vbox = QVBoxLayout()
        BacktoFirst = QHBoxLayout()
        BacktoFirst.addStretch(1)
        BacktoFirst.addWidget(self.button)
        BacktoFirst.addStretch(1)

        vbox.setStretch(0,1)
        vbox.setStretch(1,self.image_ratio)
        vbox.setStretch(2,1)
        vbox.addStretch(2)
        vbox.addLayout(BacktoFirst)
        ImageHbox = QHBoxLayout()

        self.leftim = ImageDrawLabel(self.lpixelMap, QSize(self.grid_width, self.grid_width))
        self.rightim = ImageDrawLabel(self.rpixelMap, QSize(self.grid_width, self.grid_width))

        ImageHbox.setContentsMargins(self.grid_margin, self.grid_margin, self.grid_margin, self.grid_margin)
        ImageHbox.addWidget(self.rightim,alignment=Qt.AlignCenter)
        ImageHbox.addLayout(grid)
        ImageHbox.addWidget(self.leftim,alignment=Qt.AlignCenter)

        vbox.addStretch(1)
        vbox.addLayout(ImageHbox)
        vbox.addStretch(1)

        downloadHbox = QHBoxLayout()
        downloadHbox.addStretch(1)
        downloadHbox.addWidget(self.download)
        downloadHbox.addWidget(self.path)
        downloadHbox.addStretch(1)
        vbox.addLayout(downloadHbox)

        vbox.addStretch(2)


        self.setLayout(vbox)

        pass

    def _getMorphResults(self):

        morph_alpha = 0.5
        edge_samples = 1
        lqimg = self.lpixelMap.toImage()
        rqimg = self.rpixelMap.toImage()

        ### convert qimage to cvimage
        lcvim, rcvim = q_toCVimage(lqimg),q_toCVimage(rqimg)
        lsize, rsize = lcvim.shape, rcvim.shape
        lrect, rrect = (0, 0, lsize[1], lsize[0]), (0, 0, rsize[1], rsize[0])

        ### convert Qpoint List to normal List
        llist, rlist = [(p.x(),p.y()) for p in self.lpts], [(p.x(),p.y()) for p in self.rpts]

        ### Add Corner points to features
        llist = llist + sample_rect(rrect, edge_samples)
        rlist = rlist + sample_rect(lrect, edge_samples)

        ### Get delaunay indexes
        l_delaunay_indexes = calculateDelaunayTriangles(lrect, llist)
        r_delaunay_indexes = calculateDelaunayTriangles(rrect, rlist)
        self.rwarps, self.morphs = [], []
        for i,aa in enumerate(self.alphas):
            print(aa)
            warp_pts = []
            lwarp = np.zeros(lsize, dtype=lcvim.dtype)
            rwarp = np.zeros(rsize, dtype=lcvim.dtype)

            ### Get warp mesh
            for i in range(0, len(rlist)):
                x = aa * llist[i][0] + (1 - aa) * rlist[i][0]
                y = aa * llist[i][1] + (1 - aa) * rlist[i][1]
                warp_pts.append((x, y))

            for (i, j, k) in l_delaunay_indexes:
                lt = [llist[i], llist[j], llist[k]]
                tw = [warp_pts[i], warp_pts[j], warp_pts[k]]
                warpTriangle(lcvim, lwarp, lt, tw)

            for (i, j, k) in r_delaunay_indexes:
                rt = [rlist[i], rlist[j], rlist[k]]
                tw = [warp_pts[i], warp_pts[j], warp_pts[k]]
                warpTriangle(rcvim, rwarp, rt, tw)


            imgMorph = ((1-morph_alpha)*lwarp + morph_alpha*rwarp).astype(np.uint8)
            self.rwarps.append(rwarp)
            self.morphs.append(imgMorph)

    def getSelectedId(self):
        r_id = []
        m_id = []
        for i,rwarp in enumerate(self.rwarp_grids):
            if rwarp.selected:
                r_id.append(i)

        for i,morph in enumerate(self.morph_grids):
            if morph.selected:
                m_id.append(i)

        return r_id, m_id

    def _download(self):
        r_id, m_id = self.getSelectedId()
        dir = self.path.text()
        if dir == '':
            import time
            # 取当前时间
            dir_name = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        else:
            dir_name = dir

        dir_name = os.path.join('result', dir_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        for i in r_id:
            cv2.imwrite(os.path.join(dir_name, 'warp_%.3f.jpg' % self.alphas[i]), self.rwarps[i])

        for i in m_id:
            cv2.imwrite(os.path.join(dir_name, 'morph_%.3f.jpg' % self.alphas[i]), self.morphs[i])

        self.msgbox = QMessageBox()
        self.msgbox.setText("下载完成")
        self.msgbox.show()





