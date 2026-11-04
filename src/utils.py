from Qt5 import *
from functools import reduce

def toPixmap(img):
    '''Converts OpenCV image (numpy array) to PyQt5 compatible PixMap'''

    h, w, ch = img.shape
    img = QImage(img[..., ::-1].tobytes(), w, h, ch*w, QImage.Format_RGB888)
    return QPixmap.fromImage(img)

class Slider(QWidget):
    '''Subclass for easily creating a slider'''

    def __init__(self, min, max, text=None, parent=None):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())

        if text is not None:
            self.label = QLabel(text)
            self.layout().addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(min, max)
        self.layout().addWidget(self.slider)

        # proxy methods
        self.minimum = self.slider.minimum
        self.maximum = self.slider.maximum
        self.setValue = self.slider.setValue
        self.value = self.slider.value
        self.valueChanged = self.slider.valueChanged

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
