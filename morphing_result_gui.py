from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel,QHBoxLayout,QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from math import sqrt

class ImageDrawLabel(QLabel):
    # dropImgSignal = pyqtSignal(object)

    def __init__(self, pm):
        super(ImageDrawLabel, self).__init__()
        self.setPixmap(pm)
        self._initUI()

        pass

    def _initUI(self):
        self.setAlignment(Qt.AlignCenter)
        pass



class MorphingResultWidget(QWidget):

    def __init__(self, lpm, rpm, rwarps, morphs):
        super(MorphingResultWidget, self).__init__()
        self.lpm, self.rpm = lpm,rpm
        self.rwarps = rwarps
        self.morphs = morphs
        self.image_ratio=3
        self._initUI()

        pass

    def _initUI(self):
        grid = QGridLayout()

        self.button = QPushButton("回到首页")
        self.button.setMinimumSize(200, 50)
        self.download = QPushButton("下载图片")
        self.download.setMinimumSize(200, 50)
        vbox = QVBoxLayout()
        BacktoFirst = QHBoxLayout()
        BacktoFirst.addStretch(1)
        BacktoFirst.addWidget(self.button)
        BacktoFirst.addStretch(1)

        vbox.setStretch(0,1)
        vbox.setStretch(1,1)
        vbox.setStretch(2,self.image_ratio)
        vbox.setStretch(3,1)
        vbox.addLayout(BacktoFirst)
        ImageHbox = QHBoxLayout()

        self.leftim = ImageDrawLabel(self.lpm)
        self.rightim = ImageDrawLabel(self.rpm)
        ImageHbox.addWidget(self.rightim)
        ImageHbox.addLayout(grid)
        ImageHbox.addWidget(self.leftim)
        vbox.addStretch(3)
        vbox.addLayout(ImageHbox)
        vbox.addStretch(1)
        downloadHbox = QHBoxLayout()
        downloadHbox.addStretch(1)
        downloadHbox.addWidget(self.download)
        downloadHbox.addStretch(1)
        vbox.addLayout(downloadHbox)


        self.setLayout(vbox)

        pass


