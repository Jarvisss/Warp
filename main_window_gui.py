from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QDesktopWidget
import sys
from cvhelper import q_toCVimage, cv_toQimage, sample_rect
from image_upload_gui import ImageUploadWidget
from image_label_gui import ImageLabelWidget
from image_morphing_gui import ImagePreviewWidget
from morphing_result_gui import MorphingResultWidget
from warp import calculateDelaunayTriangles, warpTriangle
import numpy as np
import cv2

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self._initUI()
        self._connect()
        self.setMouseTracking(True)

    def _initUI(self):
        desktop_rect = QDesktopWidget().availableGeometry()
        self.w, self.h = desktop_rect.width(), desktop_rect.height()
        self.setMinimumSize(self.w, self.h)
        self.step1Widget = ImageUploadWidget(self.w, self.h)
        self.setWindowTitle('STEP1:  图片上传')
        self.setCentralWidget(self.step1Widget)
        self.showMaximized()

        pass

    def _connect(self):
        self.step1Widget.button.clicked.connect(lambda:self._showLabelView(self.step1Widget.leftim.imgUrl, self.step1Widget.rightim.imgUrl))
    """
    SLOTS
    """
    def _showLabelView(self, lUrl, rUrl):
        print(lUrl,rUrl)
        self.setWindowTitle('STEP2:  特征点标注')
        self.step2Widget = ImageLabelWidget(self.w, self.h, lUrl, rUrl)
        self.setCentralWidget(self.step2Widget)
        self.step2Widget.button.clicked.connect(
            lambda:self._showPreview(
                self.step2Widget.leftim.points,
                self.step2Widget.rightim.points,
                self.step2Widget.leftim.qPixmap,
                self.step2Widget.rightim.qPixmap
            )
        )

        pass

    def _showPreview(self, lpts, rpts, lpixelMap, rpixelMap):
        self.setWindowTitle('STEP3:  仿生融合')
        self.lpts = lpts
        self.rpts = rpts
        self.lpixelMap = lpixelMap
        self.rpixelMap = rpixelMap
        self.step3Widget = ImagePreviewWidget(lpts, rpts, lpixelMap, rpixelMap)
        self.setCentralWidget(self.step3Widget)
        self.step3Widget.button_start_morphing.clicked.connect(
            self._showResult
        )
        pass

    def _showResult(self):
        self.setWindowTitle('STEP4:  融合结果')
        self._getMorphResults()
        self.step4Widget = MorphingResultWidget(self.lpixelMap, self.rpixelMap, self.rwarps, self.morphs)
        self.setCentralWidget(self.step4Widget)
        self.step4Widget.button.clicked.connect(
            self._backToFirst
        )

    def _backToFirst(self):
        self.rwarps = []
        self.morphs = []
        self.step1Widget = ImageUploadWidget(self.w, self.h)
        self.setCentralWidget(self.step1Widget)
        self.setWindowTitle('STEP1:  图片上传')


    def _getMorphResults(self):
        alphas = [1 / 6, 1 / 3, 1 / 2, 2 / 3, 5 / 6]
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
        for i,aa in enumerate(alphas):
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




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    sys.exit(app.exec_())
