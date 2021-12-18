from Qt5 import *
import cv2
import numpy as np
from utils import Slider

applied = []

class Transform(QAction):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.triggered.connect(self.check_transform)

        self.show_img = self.parent().parent().show_img

    def check_transform(self):
        if any(isinstance(i, self.__class__) for i in applied):
            return
        else:
            self.setup()

    def setup(self):
        applied.append(self)

        self.wid = QWidget()
        self.wid.setLayout(QVBoxLayout())
        self.parent().parent().tool_frame.widget().layout().addWidget(self.wid)

        self.enabled = QCheckBox()
        self.enabled.setMaximumWidth(20)
        self.enabled.setChecked(True)
        self.enabled.stateChanged.connect(self.show_img)

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.title = QLabel(self.text())
        self.title.setFont(font)

        header = QWidget()
        header.setLayout(QHBoxLayout())
        header.layout().addWidget(self.enabled)
        header.layout().addWidget(self.title)
        self.wid.layout().addWidget(header)

class Clahe(Transform):
    def __init__(self, parent=None):
        super().__init__('Contrast', parent)

    def setup(self):
        super().setup()

        self.grid_slider = Slider(1, 100, 'Grid size')
        self.grid_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.grid_slider)

        self.clip_slider = Slider(1, 100, 'Clip limit')
        self.clip_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.clip_slider)

        self.split_channel = QCheckBox('Equalise RGB channels separately')
        self.split_channel.stateChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.split_channel)

    def __call__(self, img):
        clip = self.clip_slider.value() * 0.1
        grid = self.grid_slider.value()
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))

        if self.split_channel.isChecked():
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

        self.k_slider = Slider(-100, 100)
        self.k_slider.setValue(0)
        self.k_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.k_slider)

    def __call__(self, img):
        k = self.k_slider.value() * 0.01
        kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ])

        img2 = cv2.filter2D(img, 0, kernel)
        img = cv2.addWeighted(img, 1, img2, k, 0)

        return img

class Blur(Transform):
    def __init__(self, parent=None):
        super().__init__('Blur', parent)

    def setup(self):
        super().setup()

        self.k_slider = Slider(1, 100)
        self.k_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.k_slider)

    def __call__(self, img):
        k = self.k_slider.value()

        img = cv2.blur(img, (k, k))
        return img

class Grayscale(Transform):
    def __init__(self, parent=None):
        super().__init__('Grayscale', parent)

    def setup(self):
        super().setup()

        self.channel_weighted = QCheckBox('Channel weighted grayscale')
        self.channel_weighted.stateChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.channel_weighted)

        self.show_img()

    def __call__(self, img):
        if self.channel_weighted.isChecked():
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img = np.sum(img, axis=2)
            img = (img*0.33).astype('uint8')
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        return img

class Vignette(Transform):
    def __init__(self, parent=None):
        super().__init__('Vignette', parent)

    def setup(self):
        super().setup()

        self.k_slider = Slider(0, 1000)
        self.k_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.k_slider)

    def __call__(self, img):
        k = self.k_slider.maximum() - self.k_slider.value() + 1

        a = cv2.getGaussianKernel(img.shape[0], k)
        b = cv2.getGaussianKernel(img.shape[1], k)
        mask = a * b.T
        mask = mask / mask.max()

        for i in range(3):
            img[..., i] = img[..., i] * mask
        img = img.astype(np.uint8)
        return img

class Saturation(Transform):
    def __init__(self, parent=None):
        super().__init__('Saturation', parent)

    def setup(self):
        super().setup()

        self.k_slider = Slider(0, 200)
        self.k_slider.setValue(100)
        self.k_slider.valueChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.k_slider)

    def __call__(self, img):
        k = self.k_slider.value() * 0.01

        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img[..., 1] = (img[..., 1] * k).clip(0, 255)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        return img

class Negative(Transform):
    def __init__(self, parent=None):
        super().__init__('Negative', parent)

    def setup(self):
        super().setup()
        self.show_img()

    def __call__(self, img):
        return cv2.bitwise_not(img)
