from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QGridLayout, QCheckBox, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont
from warp import calculateDelaunayTriangles, draw_triangulation
from cvhelper import cv_toQimage, sample_rect, q_toCVimage


class ImageDrawLabel(QLabel):

    def __init__(self, pts, pm):
        super(ImageDrawLabel, self).__init__()
        self.points = pts
        self.qPixmap = pm
        self.is_show_tri = 1  # 0 for not show, 1 for show
        self.setFixedSize(pm.size())
        self._initUI()
        img = self.qPixmap.toImage()
        cvim = q_toCVimage(img)
        size = cvim.shape
        rect = (0, 0, size[1], size[0])
        ptlist = [(p.x(), p.y()) for p in self.points] + sample_rect(rect, 1)
        delaunay_indexes = calculateDelaunayTriangles(rect, ptlist)
        self.tri_img = draw_triangulation(cvim, ptlist, delaunay_indexes)
        self.qtri_img = cv_toQimage(self.tri_img)

        # self.updateImage()
        pass



    def _initUI(self):
        self.setAlignment(Qt.AlignCenter)

        pass

    # def updateImage(self):
    #     font = QFont("宋体", 20, QFont.Black, True)
    #     painter = QPainter(self)
    #     pixmap = QPixmap(self.size())
    #     pixmap.fill(Qt.white)
    #     painter.begin(pixmap)
    #
    #
    #     if self.is_show_tri:
    #         painter.drawPixmap(self.rect(), QPixmap(
    #             self.qtri_img.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
    #     else:
    #         painter.drawPixmap(self.rect(), self.qPixmap)
    #
    #     pen = QPen()
    #     pen.setCapStyle(Qt.RoundCap)
    #     pen.setWidth(10)
    #     pen.setBrush(QColor(255, 0, 0))
    #     painter.setRenderHint(QPainter.Antialiasing, True)
    #     painter.setFont(font)
    #     for i, pos in enumerate(self.points):
    #         pen.setBrush(QColor(255, 0, 0))
    #         painter.setPen(pen)
    #         painter.drawPoint(pos)
    #         pen.setBrush(QColor(218, 112, 214))
    #         painter.setPen(pen)
    #         painter.drawText(pos, str(i))
    #
    #     painter.end()
    #     self.setPixmap(pixmap)

    def paintEvent(self, QPaintEvent):
        font = QFont("宋体", 20, QFont.Black, True)
        painter = QPainter(self)

        if self.is_show_tri:
            painter.drawPixmap(self.rect(), QPixmap(self.qtri_img.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        else:
            painter.drawPixmap(self.rect(), self.qPixmap)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(10)
        pen.setBrush(QColor(255, 0, 0))
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(font)
        for i, pos in enumerate(self.points):
            pen.setBrush(QColor(255, 0, 0))
            painter.setPen(pen)
            painter.drawPoint(pos)
            pen.setBrush(QColor(218, 112, 214))
            painter.setPen(pen)
            painter.drawText(pos, str(i))


class ImagePreviewWidget(QWidget):

    def __init__(self, lpts, rpts, lpm, rpm):
        super(ImagePreviewWidget, self).__init__()
        self.lpts, self.rpts = lpts, rpts
        self.lpm, self.rpm = lpm, rpm
        self.image_ratio = 5
        self._initUI()
        self.show_triangulation.stateChanged.connect(self.updateTriangulation)
        self.button_download.clicked.connect(self._download)
        pass

    def _initUI(self):
        layout = QGridLayout()

        self.show_triangulation = QCheckBox("显示三角化")
        self.show_triangulation.setChecked(True)
        self.button_download = QPushButton("下载")
        self.button_start_morphing = QPushButton("开始融合")
        self.button_start_morphing.setMinimumSize(200, 50)
        hbo = QHBoxLayout()
        hbo.addStretch(1)
        hbo.addWidget(self.button_start_morphing)
        hbo.addWidget(self.show_triangulation)
        hbo.addWidget(self.button_download)
        hbo.addStretch(1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, self.image_ratio)

        layout.addLayout(hbo, 0, 0, 1, 2)
        self.leftim = ImageDrawLabel(self.lpts, self.lpm)
        layout.addWidget(self.leftim, 1, 0)
        self.rightim = ImageDrawLabel(self.rpts, self.rpm)
        layout.addWidget(self.rightim, 1, 1)
        self.setLayout(layout)

    def updateTriangulation(self, state):
        self.leftim.is_show_tri = state
        self.rightim.is_show_tri = state
        self.update()

    def _download(self):

        import time
        import cv2
        import os
        # 取当前时间
        dir_name = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        dir_name = os.path.join('triangulation', dir_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        cv2.imwrite(os.path.join(dir_name, 'left.jpg'), self.leftim.tri_img)
        cv2.imwrite(os.path.join(dir_name, 'right.jpg'), self.rightim.tri_img)

        self.msgbox = QMessageBox()
        self.msgbox.setText("下载至:{0}".format(dir_name))
        self.msgbox.show()


