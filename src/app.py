from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
from image import Image
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
        self.addAction(t.FalseClahe(self))
        self.addAction(t.Sharpen(self))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Image editor'
        self.img = None

        self.setWindowTitle(self.title)
        self.resize(800, 800)

        menubar = self.menuBar()
        menubar.addMenu(FileMenu(self))
        menubar.addMenu(EditMenu(self))

        self.img_frame = QLabel()
        self.setCentralWidget(self.img_frame)

        self.show()

    def file_open(self):
        self.infile, _ = QFileDialog.getOpenFileName(self,"Open file", "","All files(*) ;; Images(*.png *.jpeg *.bmp)")
        self.outfile = None

        self.og_img = Image(cv2.imread(self.infile))
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
        print("File close")

    def file_exit(self):
        exit()

    def show_img(self):
        self.img = Image(t.compose(t.applied)(self.og_img))
        self.img_frame.setPixmap(self.img.toPixmap())
