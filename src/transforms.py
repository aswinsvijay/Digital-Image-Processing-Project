import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from functools import reduce

applied = []

def compose(funcs):
    def inner(f, g):
        return lambda x: g(f(x))

    return reduce(inner, funcs, lambda x: x)

class Transform(QAction):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.triggered.connect(self.setup)

    def setup(self):
        applied.append(self)

        wid = QWidget()
        self.layout = QVBoxLayout()
        wid.setLayout(self.layout)

        self.parent().parent().tool_frame.layout().addWidget(wid)

class Slider(QSlider):
    def __init__(self, min, max, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(min, max)

class Clahe(Transform):
    def __init__(self, parent=None):
        super().__init__('Adaptive Histogram Equalization', parent)

    def setup(self):
        super().setup()

        self.grid = 1
        grid_slider = Slider(1, 100)
        grid_slider.valueChanged.connect(self.update_grid)

        self.clip = 1
        clip_slider = Slider(1, 100)
        clip_slider.valueChanged.connect(self.update_clip)

        self.split_channel = QCheckBox('Equalise RGB channels separately')
        self.split_channel.stateChanged.connect(self.parent().parent().show_img)

        self.layout.addWidget(clip_slider)
        self.layout.addWidget(grid_slider)
        self.layout.addWidget(self.split_channel)

    def update_grid(self, value):
        self.grid = value
        self.parent().parent().show_img()

    def update_clip(self, value):
        self.clip = value*0.1
        self.parent().parent().show_img()

    def __call__(self, img):
        clahe = cv2.createCLAHE(clipLimit=self.clip, tileGridSize=(self.grid, self.grid))

        if self.split_channel.isChecked():
            img = img.copy()
            for i in range(3):
                img[..., i] = clahe.apply(img[..., i])
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            img[..., 0] = clahe.apply(img[..., 0])
            img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR)

        return img

class Sharpen(Transform):
    def __init__(self, parent=None):
        super().__init__('Sharpen', parent)

    def setup(self):
        super().setup()

        self.k = 0
        k_slider = Slider(0, 100)
        k_slider.valueChanged.connect(self.update_k)

        self.layout.addWidget(k_slider)

    def update_k(self, value):
        self.k = value*0.01
        self.parent().parent().show_img()

    def __call__(self, img):
        kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ])

        img2 = cv2.filter2D(img, 0, kernel)
        img = cv2.addWeighted(img, 1, img2, self.k, 0)

        return img

# class Blur(Transform):
    # def __call__(self, img):
    #     return img

# class Grayscale(Transform):
    # def __call__(self, img):
    #     img = np.sum(img, axis=2)
    #     img = (img*0.33).astype('uint8')
    #     img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    #     return img

# class Vignette(Transform):
    # def __call__(self, img):
    #     return img
