from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QDesktopWidget, QMessageBox
import sys
from image_upload_gui import ImageUploadWidget
from image_label_gui import ImageLabelWidget
from image_morphing_gui import ImagePreviewWidget
from morphing_result_gui import MorphingResultWidget
import cv2
import os

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
        self.step4Widget = MorphingResultWidget(self.w, self.h,self.lpts, self.rpts, self.lpixelMap, self.rpixelMap)
        self.setCentralWidget(self.step4Widget)
        self.step4Widget.button.clicked.connect(
            self._backToFirst
        )
        self.step4Widget.download.clicked.connect(
            self._download
        )

    def _backToFirst(self):
        self.step1Widget = ImageUploadWidget(self.w, self.h)
        self.setCentralWidget(self.step1Widget)
        self.setWindowTitle('STEP1:  图片上传')
        self._connect()

    def _download(self):
        r_id, m_id = self.step4Widget.getSelectedId()
        dir = self.step4Widget.path.text()
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
            cv2.imwrite(os.path.join(dir_name, 'warp_%.3f.jpg'%self.step4Widget.alphas[i]),self.step4Widget.rwarps[i])

        for i in m_id:
            cv2.imwrite(os.path.join(dir_name, 'morph_%.3f.jpg'%self.step4Widget.alphas[i]),self.step4Widget.morphs[i])

        self.msgbox = QMessageBox()
        self.msgbox.setText("下载完成")
        self.msgbox.show()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    sys.exit(app.exec_())
