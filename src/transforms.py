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

        self.setup()
        self.show_img()

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

class ContrastStretching(Transform):
    def __init__(self, parent=None):
        super().__init__('Contrast stretching', parent)

    def setup(self):
        super().setup()

    def __call__(self, img):
        img = img.astype('float')
        img = (img - np.min(img)) / np.ptp(img)
        img = np.uint8(img * 255)
        return img

class HistogramEqualization(Transform):
    def __init__(self, parent=None):
        super().__init__('Histogram equalization', parent)

    def setup(self):
        super().setup()

        self.split_channel = QCheckBox('Equalise RGB channels separately')
        self.split_channel.stateChanged.connect(self.show_img)
        self.wid.layout().addWidget(self.split_channel)

    def __call__(self, img):
        if self.split_channel.isChecked():
            for i in range(3):
                img[..., i] = cv2.equalizeHist(img[..., i])
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            img[..., 0] = cv2.equalizeHist(img[..., 0])
            img = cv2.cvtColor(img, cv2.COLOR_YCrCb2BGR)

        return img

class Clahe(Transform):
    def __init__(self, parent=None):
        super().__init__('Clahe', parent)

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

    def __call__(self, img):
        if self.channel_weighted.isChecked():
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img = np.sum(img, axis=2)
            img = (img*0.33).astype(np.uint8)
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

    def __call__(self, img):
        return cv2.bitwise_not(img)

class ColorChannel(Transform):
    def __init__(self, parent=None):
        super().__init__('Color Channels', parent)

    def setup(self):
        super().setup()

        self.sliders = []
        for c in 'BGR':
            slider = Slider(0, 200, c)
            slider.setValue(100)
            slider.valueChanged.connect(self.show_img)
            self.wid.layout().addWidget(slider)
            self.sliders.append(slider)

    def __call__(self, img):
        for i in range(3):
            k = self.sliders[i].value() * 0.01
            img[..., i] = (img[..., i] * k).clip(0, 255)

        return img

class HueRotate(Transform):
    def __init__(self, parent=None):
        super().__init__('Hue Rotate', parent)

    def setup(self):
        super().setup()

        self.hue_slider = Slider(0, 180)
        self.wid.layout().addWidget(self.hue_slider)
        self.hue_slider.valueChanged.connect(self.show_img)

    def __call__(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hue = img[..., 0].astype(np.uint32)
        val = self.hue_slider.value()
        img[..., 0] = (hue + val) % 180
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        return img

class Mirror(Transform):
    def __init__(self, parent=None):
        super().__init__('Mirror', parent)

    def setup(self):
        super().setup()

    def __call__(self, img):
        return img[:, ::-1]

class Threshold(Transform):
    def __init__(self, parent=None):
        super().__init__('Threshold', parent)

    def setup(self):
        super().setup()

        self.slider = Slider(0, 255)
        self.wid.layout().addWidget(self.slider)
        self.slider.valueChanged.connect(self.show_img)

    def __call__(self, img):
        Y = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)[..., 0]
        thresh = self.slider.value()
        img[Y<thresh] = 0
        return img

class ColourDepth(Transform):
    def __init__(self, parent=None):
        super().__init__('Colour Depth', parent)

    def setup(self):
        super().setup()

        self.slider = Slider(1, 8)
        self.slider.setValue(8)
        self.wid.layout().addWidget(self.slider)
        self.slider.valueChanged.connect(self.show_img)

    def __call__(self, img):
        bits = self.slider.value()
        colours = 2**bits
        img //= 2**(8-bits)
        img *= np.uint8(255 / (colours - 1))
        return img
