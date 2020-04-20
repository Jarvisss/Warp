from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel,QHBoxLayout,QGridLayout, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from math import sqrt

class ImageDrawLabel(QLabel):

    def __init__(self, size, imgUrl):
        super(ImageDrawLabel, self).__init__()
        self.size = size
        print(size)
        self.state = 0 # 0 for add, 1 for select
        self.setFixedSize(size)
        self._initUI()
        self.imgUrl = imgUrl
        self._initImg(imgUrl)
        self.points=[]
        self.selected_point = -1
        self.setFocusPolicy(Qt.ClickFocus)
        self.font = QFont("宋体",20, QFont.Black,True)
        pass

    def _initUI(self):
        self.setAlignment(Qt.AlignCenter)
        pass

    def _initImg(self, url):
        self.qimage = QImage(url)
        self.qimage = self.qimage.scaled(self.size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.qPixmap = QPixmap(self.qimage)

    def _getDist(self,p1,p2):
        return sqrt((p1.x()-p2.x())**2 + (p1.y()-p2.y())**2)

    def _getNearestPoint(self, center):
        dist_min = self._getDist(QPoint(0,0), QPoint(self.size.width(),self.size.height()))
        index_min = -1
        for i, p in enumerate(self.points):
            dist = self._getDist(p, center)
            if dist < dist_min:
                dist_min = dist
                index_min = i
            else:
                dist_min = dist_min

        return index_min,dist_min

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_D or e.key() == Qt.Key_Delete or e.key()==Qt.Key_Backspace and self.selected_point>0 and self.state:
            if self.selected_point >= 0 and self.selected_point < len(self.points):
                del self.points[self.selected_point]
                print('delete:', str(self.selected_point))
                self.selected_point = -1
            else:
                print('delete index out of range')
        self.update()

    def mousePressEvent(self, event):
        self.prev_x = event.x()
        self.prev_y = event.y()

        if event.buttons() == Qt.LeftButton:
            if not self.state:
                print(event.pos())
                self.points.append(event.pos())
                self.selected_point = -1
            else:
                id, dist = self._getNearestPoint(event.pos())
                self.selected_point = id
                print('select:', str(id))
                self.setMouseTracking(True)



    def mouseMoveEvent(self, event):
        offset_x = event.x() - self.prev_x
        offset_y = event.y() - self.prev_y

        self.points[self.selected_point] += QPoint(offset_x,offset_y)
        x = self.points[self.selected_point].x()
        y = self.points[self.selected_point].y()
        x = x if 0<=x<self.size.width() else 0 if x < 0 else self.size.width()-1
        y = y if 0<=y<self.size.height() else 0 if y < 0 else self.size.height()-1
        self.points[self.selected_point] = QPoint(x,y)
        print(self.points[self.selected_point])
        self.prev_x = event.x()
        self.prev_y = event.y()
        self.update()

    def mouseReleaseEvent(self, event):
        self.setMouseTracking(False)
        self.update()

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.qPixmap)
        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidth(10)
        pen.setBrush(QColor(255, 0, 0))


        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(self.font)
        for i,pos in enumerate(self.points):
            if i == self.selected_point and self.state:
                pen.setBrush(QColor(0, 255, 0))
            else:
                pen.setBrush(QColor(255, 0, 0))

            painter.setPen(pen)

            painter.drawPoint(pos)
            pen.setBrush(QColor(218,112,214))
            painter.setPen(pen)
            painter.drawText(pos, str(i))
        pass

    def setState(self, state):
        self.state = state
        self.update()


class ImageLabelWidget(QWidget):

    def __init__(self,ww,hh, lurl, rurl):
        super(ImageLabelWidget, self).__init__()
        self.w,self.h = ww,hh
        self.lurl, self.rurl = lurl,rurl
        self.image_ratio = 5
        self.img_length = min(self.w // 2, int(self.h * self.image_ratio / (self.image_ratio + 1)))
        self.img_size = QSize(self.img_length, self.img_length)
        self._initUI()
        self._connect()
        pass

    def _initUI(self):
        layout = QGridLayout()

        self.button = QPushButton("下一步")
        self.button.setMinimumSize(200, 50)
        self.check_button = QPushButton("检查")
        self.check_button.setMinimumSize(200, 50)

        self.button.setEnabled(False)
        self.select = QRadioButton('选择')
        self.add = QRadioButton('添加')
        self.add.setChecked(True)
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.add, 1)
        self.buttonGroup.addButton(self.select, 2)
        hbo = QHBoxLayout()
        hbo.addStretch(2)

        hbo.addWidget(self.add)
        hbo.addWidget(self.select)
        hbo.addStretch(1)
        hbo.addWidget(self.check_button)
        hbo.addWidget(self.button)
        hbo.addStretch(1)

        layout.addLayout(hbo, 0, 0, 1, 2)
        layout.setRowStretch(0,1)
        layout.setRowStretch(1, self.image_ratio)

        self.leftim = ImageDrawLabel(self.img_size,self.lurl)
        layout.addWidget(self.leftim, 1, 0)
        self.rightim = ImageDrawLabel(self.img_size, self.rurl)
        layout.addWidget(self.rightim, 1, 1)

        self.setLayout(layout)

        pass

    def _connect(self):
        self.buttonGroup.buttonClicked[int].connect(self.setState)
        self.check_button.clicked.connect(self.check)


    def setState(self, buttonid):
        print(buttonid)
        if buttonid == 1:
            self.leftim.setState(0)
            self.rightim.setState(0)
        elif buttonid==2:
            self.leftim.setState(1)
            self.rightim.setState(1)


    def check(self):
        if len(self.leftim.points) != len(self.rightim.points):
            self.button.setEnabled(False)
        else:
            self.button.setEnabled(True)


