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

class ClaheBase(QAction):
    def setup(self):
        self.grid = 1
        self.clip = 1
        applied.append(self)

        self.win = QMainWindow(self.parent())
        self.win.setWindowTitle(self.text())

        grid_slider = QSlider(Qt.Horizontal, self.win)
        grid_slider.setRange(1, 100)
        grid_slider.setFocusPolicy(Qt.NoFocus)
        grid_slider.setPageStep(5)
        grid_slider.valueChanged.connect(self.update_grid)

        clip_slider = QSlider(Qt.Horizontal, self.win)
        clip_slider.setRange(1, 100)
        clip_slider.setFocusPolicy(Qt.NoFocus)
        clip_slider.setPageStep(5)
        clip_slider.valueChanged.connect(self.update_clip)

        wid = QWidget(self.win)
        layout = QVBoxLayout()
        layout.addWidget(clip_slider)
        layout.addWidget(grid_slider)
        wid.setLayout(layout)
        self.win.setCentralWidget(wid)
        self.win.show()

    def update_grid(self, value):
        self.grid = value
        self.win.parent().parent().show_img()

    def update_clip(self, value):
        self.clip = value*0.1
        self.win.parent().parent().show_img()

class Clahe(ClaheBase):
    def __init__(self, parent=None):
        super().__init__('Adaptive Histogram Equalization', parent)
        self.triggered.connect(self.setup)

    def __call__(self, img):
        clahe = cv2.createCLAHE(clipLimit=self.clip, tileGridSize=(self.grid, self.grid))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        img[..., 0] = clahe.apply(img[..., 0])
        img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR)

        return img

class FalseClahe(ClaheBase):
    def __init__(self, parent=None):
        super().__init__('False Adaptive Histogram Equalization', parent)
        self.triggered.connect(self.setup)

    def __call__(self, img):
        clahe = cv2.createCLAHE(clipLimit=self.clip, tileGridSize=(self.grid, self.grid))

        img = img.copy()
        for i in range(3):
            img[..., i] = clahe.apply(img[..., i])

        return img

class Sharpen(QAction):
    def __init__(self, parent=None):
        super().__init__('Sharpen', parent)
        self.triggered.connect(self.setup)

    def setup(self):
        self.k = 0
        applied.append(self)

        self.win = QMainWindow(self.parent())
        self.win.setWindowTitle(self.text())

        k_slider = QSlider(Qt.Horizontal, self.win)
        k_slider.setRange(0, 100)
        k_slider.setFocusPolicy(Qt.NoFocus)
        k_slider.setPageStep(5)
        k_slider.valueChanged.connect(self.update_k)

        wid = QWidget(self.win)
        layout = QVBoxLayout()
        layout.addWidget(k_slider)
        wid.setLayout(layout)
        self.win.setCentralWidget(wid)
        self.win.show()

    def update_k(self, value):
        self.k = value*0.01
        self.win.parent().parent().show_img()

    def __call__(self, img):
        kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ])

        img2 = cv2.filter2D(img, 0, kernel)
        img = cv2.addWeighted(img, 1, img2, self.k, 0)

        return img

# class Blur(QAction):
    # def __call__(self, img):
    #     return img

# class Grayscale(QAction):
    # def __call__(self, img):
    #     img = np.sum(img, axis=2)
    #     img = (img*0.33).astype('uint8')
    #     img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    #     return img

# class Vignette(QAction):
    # def __call__(self, img):
    #     return img
