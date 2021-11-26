from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
from image import toPixmap
import transforms as t

class FileMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__('&File', parent)

        open = QAction('Open', self)
        open.setShortcut('Ctrl+O')
        open.triggered.connect(parent.file_open)
        self.addAction(open)

        save = QAction('Save', self)
        save.setShortcut('Ctrl+S')
        save.triggered.connect(parent.file_save)
        self.addAction(save)

        save = QAction('Save As', self)
        save.triggered.connect(parent.file_save_as)
        self.addAction(save)

        close = QAction('Close', self)
        close.setShortcut('Ctrl+F4')
        close.triggered.connect(parent.file_close)
        self.addAction(close)

        exit = QAction('Exit', self)
        exit.triggered.connect(parent.file_exit)
        self.addAction(exit)

class EditMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__('&Edit', parent)

        self.addAction(t.Clahe(self))
        self.addAction(t.Sharpen(self))
        self.addAction(t.Grayscale(self))
        self.addAction(t.Blur(self))
        self.addAction(t.Vignette(self))

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1, 1)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

class ToolsLabel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QWidget(self)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        widget.setMaximumWidth(500)
        widget.setLayout(layout)

        self.setWidgetResizable(True)
        self.setWidget(widget)
        self.setMinimumWidth(300)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Image editor'
        self.infile = None
        self.outfile = None
        self.og_img = None
        self.img = None

        self.setWindowTitle(self.title)
        self.resize(800, 800)

        menubar = self.menuBar()
        menubar.addMenu(FileMenu(self))
        menubar.addMenu(EditMenu(self))

        self.img_frame = ImageLabel()
        self.tool_frame = ToolsLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.img_frame, stretch=75)
        layout.addWidget(self.tool_frame, stretch=25)
        wid = QWidget()
        wid.setLayout(layout)
        self.setCentralWidget(wid)

        self.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.show_img()

    def file_open(self):
        ret = self.file_close()
        if ret is False:
            return

        self.infile, _ = QFileDialog.getOpenFileName(self,"Open file", "","All files(*) ;; Images(*.png *.jpeg *.bmp)")
        self.outfile = None

        self.og_img = cv2.imread(self.infile)
        self.img = self.og_img.copy()
        self.show_img()

    def file_save(self):
        if self.outfile is None:
            self.file_save_as()
        cv2.imwrite(self.outfile, self.img)

    def file_save_as(self):
        self.outfile, _ = QFileDialog.getSaveFileName(self,"Save file", "","PNG file(*.png) ;; JPEG file(*.jpeg) ;; Bitmap file(*.bmp)")
        self.file_save()

    def file_close(self):
        if self.og_img is None:
            return True

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Do you want to save the changes?")
        msg.setWindowTitle(self.title)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        ret = msg.exec_()

        if ret == QMessageBox.Cancel:
            return False
        elif ret == QMessageBox.Yes:
            self.file_save()

        self.img_frame.setPixmap(QPixmap())
        self.infile = None
        self.outfile = None
        self.og_img = None
        self.img = None

        for i in t.applied:
            i.wid.close()
        t.applied = []

        return True

    def file_exit(self):
        exit()

    def show_img(self):
        if self.og_img is not None:
            self.img = t.compose(t.applied)(self.og_img)
            w, h = self.img_frame.width(), self.img_frame.height()
            self.img_frame.setPixmap(toPixmap(self.img).scaled(w, h, Qt.KeepAspectRatio))
