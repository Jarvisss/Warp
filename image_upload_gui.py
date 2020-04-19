from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel,QHBoxLayout,QGridLayout
from PyQt5.QtGui import QPixmap, QImage

class ImageDropLabel(QLabel):
    dropImgSignal = pyqtSignal(object)

    def __init__(self, size):
        super(ImageDropLabel, self).__init__()
        self.size = size
        self.setAcceptDrops(True)
        self.setFixedSize(size)
        self._initUI()
        self.imgUrl = ''
        pass

    def _initUI(self):
        self.setStyleSheet(
            'border: 2px dashed black;\
            border-radius:10px;\
            background-color: lightgray;\
            min-width:300px;\
            min-height:300px;'
        )
        self.setAlignment(Qt.AlignCenter)

        pass

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        pass

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].path()[-4:] == '.jpg':
                self.imgUrl = urls[0].path()[1:]
                qimage = QImage(self.imgUrl)
                qimage = qimage.scaled(self.size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.dropImgSignal.emit(str(self.imgUrl))
                self.setPixmap(QPixmap(qimage))
        pass


class ImageUploadWidget(QWidget):

    def __init__(self,ww,hh):
        super(ImageUploadWidget, self).__init__()
        self.w,self.h = ww,hh
        self.image_ratio = 4
        self.img_length = min(self.w // 2, int(self.h * self.image_ratio / (self.image_ratio + 1)))
        self.img_size = QSize(self.img_length, self.img_length)
        self._initUI()
        self._connect()
        pass

    def _initUI(self):
        layout = QGridLayout()

        self.button = QPushButton("下一步")
        self.button.setMinimumSize(200,50)
        self.button.setEnabled(False)
        hbo = QHBoxLayout()

        hbo.addStretch(1)
        hbo.addWidget(self.button)
        hbo.addStretch(1)
        # layout.addWidget(self.button, 1, 1, 1, 1)

        layout.addLayout(hbo, 0, 0, 1, 2)
        layout.setRowStretch(0,1)
        layout.setRowStretch(1, self.image_ratio)

        self.leftim = ImageDropLabel(self.img_size)
        self.leftim.setText("拖入生物图片")
        layout.addWidget(self.leftim, 1, 0)
        self.rightim = ImageDropLabel(self.img_size)
        self.rightim.setText("拖入产品图片")
        layout.addWidget(self.rightim, 1, 1)

        self.setLayout(layout)

        pass

    def _connect(self):
        self.leftim.dropImgSignal.connect(self.dropUpdate)
        self.rightim.dropImgSignal.connect(self.dropUpdate)

    def dropUpdate(self,url):
        if self.leftim.imgUrl != '' and self.rightim.imgUrl!='':
            self.button.setEnabled(True)


