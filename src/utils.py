from PyQt5.QtGui import QImage, QPixmap

def toPixmap(img):
    h, w, ch = img.shape
    img = QImage(img.data, w, h, ch*w, QImage.Format_BGR888)
    return QPixmap.fromImage(img)
