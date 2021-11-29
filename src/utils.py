from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

def toPixmap(img):
    h, w, ch = img.shape
    img = QImage(img.data, w, h, ch*w, QImage.Format_BGR888)
    return QPixmap.fromImage(img)

class Slider(QSlider):
    def __init__(self, min, max, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(min, max)
