from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel,QHBoxLayout,QGridLayout
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

class ImageDrawLabel(QLabel):

    def __init__(self, pts, pm):
        super(ImageDrawLabel, self).__init__()
        self.points = pts
        self.qPixmap = pm
        self.state = 0 # 0 for add, 1 for select
        self.setFixedSize(pm.size())
        self._initUI()

        pass

    def _initUI(self):
        self.setAlignment(Qt.AlignCenter)
        pass

    def paintEvent(self, QPaintEvent):
        self.font = QFont("宋体", 20, QFont.Black, True)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.qPixmap)
        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(10)
        pen.setBrush(QColor(255, 0, 0))
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(self.font)
        for i, pos in enumerate(self.points):
            pen.setBrush(QColor(255, 0, 0))
            painter.setPen(pen)
            painter.drawPoint(pos)
            pen.setBrush(QColor(218, 112, 214))
            painter.setPen(pen)
            painter.drawText(pos, str(i))



class ImagePreviewWidget(QWidget):

    def __init__(self,lpts,rpts, lpm, rpm):
        super(ImagePreviewWidget, self).__init__()
        self.lpts,self.rpts = lpts,rpts
        self.lpm, self.rpm = lpm,rpm
        self.image_ratio = 5
        self._initUI()
        pass

    def _initUI(self):
        layout = QGridLayout()

        self.button_start_morphing = QPushButton("开始融合")
        self.button_start_morphing.setMinimumSize(200, 50)
        hbo = QHBoxLayout()
        hbo.addStretch(1)
        hbo.addWidget(self.button_start_morphing)
        hbo.addStretch(1)


        layout.setRowStretch(0,1)
        layout.setRowStretch(1,self.image_ratio)

        layout.addLayout(hbo, 0, 0, 1, 2)
        self.leftim = ImageDrawLabel(self.lpts,self.lpm)
        layout.addWidget(self.leftim, 1, 0)
        self.rightim = ImageDrawLabel(self.rpts, self.rpm)
        layout.addWidget(self.rightim, 1, 1)
        self.setLayout(layout)

        pass


