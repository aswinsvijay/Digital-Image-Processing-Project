import numpy as np
import cv2
from PyQt5.QtGui import QImage, QPixmap

class Image(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(cls)

    @property
    def height(self):
        return self.shape[0]

    @property
    def width(self):
        return self.shape[1]

    @property
    def ch(self):
        return self.shape[2]

    def toPixmap(self):
        img = QImage(self.data, self.width, self.height, self.ch*self.width, QImage.Format_BGR888)
        return QPixmap.fromImage(img)
