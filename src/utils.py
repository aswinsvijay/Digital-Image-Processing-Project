from Qt5 import *
from functools import reduce

def toPixmap(img):
    '''Converts OpenCV image (numpy array) to PyQt5 compatible PixMap'''

    h, w, ch = img.shape
    img = QImage(img.tobytes(), w, h, ch*w, QImage.Format_BGR888)
    return QPixmap.fromImage(img)

class Slider(QSlider):
    '''Subclass for easily creating a slider'''

    def __init__(self, min, max, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(min, max)

def compose(funcs):
    '''Compose a list of functions to a single callable function'''

    # the binary function to use for reduction
    # takes two functions and return a callable equivalent to
    # the composition of the two functions
    def inner(f, g):
        return lambda x: g(f(x))

    # filter out only the enabled options from the list
    applied_enabled = list(filter(
        lambda x: x.enabled.isChecked(), funcs
    ))
    return reduce(inner, applied_enabled, lambda x: x)
