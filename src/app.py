from Qt5 import *
import os
import cv2
import utils
import transforms as t

class FileMenu(QMenu):
    '''File menu options'''

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

        save = QAction('Set android wallpaper', self)
        save.setShortcut('Ctrl+W')
        save.triggered.connect(parent.file_set_wallpaper)
        self.addAction(save)

        close = QAction('Close', self)
        close.setShortcut('Ctrl+F4')
        close.triggered.connect(parent.file_close)
        self.addAction(close)

        exit = QAction('Exit', self)
        exit.triggered.connect(parent.file_exit)
        self.addAction(exit)

class EditMenu(QMenu):
    '''Edit menu options'''

    def __init__(self, parent=None):
        super().__init__('&Edit', parent)
        self.setEnabled(False)

        self.addActions([
            t.Clahe(self),
            t.Sharpen(self),
            t.Grayscale(self),
            t.Blur(self),
            t.Vignette(self),
            t.Saturation(self),
            t.Negative(self),
            t.ColorChannel(self),
            t.HueRotate(self),
            t.Mirror(self),
        ])

class ImageLabel(QLabel):
    '''Section for showing image'''

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

class ToolsLabel(QScrollArea):
    '''Section for showing tools'''

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        widget = QWidget(self)
        widget.setMaximumWidth(500)
        widget.setLayout(layout)

        self.setWidgetResizable(True)
        self.setWidget(widget)
        self.setMinimumWidth(300)

class App(QMainWindow):
    '''The main application window'''

    def __init__(self):
        super().__init__()
        self.title = 'Image editor'
        self.infile = None
        self.outfile = None
        self.og_img = None
        self.img = None

        self.setWindowTitle(self.title)

        # create the menu bar
        menubar = self.menuBar()
        self.menu_file = FileMenu(self)
        self.menu_edit = EditMenu(self)
        menubar.addMenu(self.menu_file)
        menubar.addMenu(self.menu_edit)

        # create the central layout
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
        if not ret:
            return

        self.infile, _ = QFileDialog.getOpenFileName(self,"Open file", "","All files(*) ;; Images(*.png *.jpeg *.bmp)")
        if not self.infile:
            return

        self.outfile = None
        self.menu_edit.setEnabled(True)
        self.og_img = cv2.imread(self.infile)
        self.img = self.og_img.copy()
        self.show_img()

    def file_save(self):
        if not self.outfile:
            self.file_save_as()
        if self.outfile:
            cv2.imwrite(self.outfile, self.img)

    def file_save_as(self):
        self.outfile, _ = QFileDialog.getSaveFileName(self,"Save file", "","PNG file(*.png) ;; JPEG file(*.jpeg) ;; Bitmap file(*.bmp)")
        if self.outfile:
            self.file_save()

    def file_close(self):
        if self.og_img is None:
            return True

        if t.applied:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Do you want to save the changes?")
            msg.setWindowTitle(self.title)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            ret = msg.exec()
        else:
            ret = QMessageBox.No

        if ret == QMessageBox.Cancel:
            return False
        elif ret == QMessageBox.Yes:
            self.file_save()

        self.img_frame.setPixmap(QPixmap())
        self.infile = None
        self.outfile = None
        self.og_img = None
        self.img = None
        self.menu_edit.setEnabled(False)

        for i in t.applied:
            i.wid.close()
        t.applied = []

        return True

    def file_exit(self):
        ret = self.file_close()
        if ret:
            exit()

    def file_set_wallpaper(self):
        if self.img is not None:
            cv2.imwrite('x.png', self.img)
            os.system(f'adb push x.png /storage/emulated/0/x.png')
            os.system(
                "adb shell am start \
                -a android.intent.action.ATTACH_DATA \
                -c android.intent.category.DEFAULT \
                -d file:///sdcard/x.png \
                -t 'image/*' \
                -e mimeType 'image/*'"
            )
            os.remove('x.png')

    def show_img(self):
        '''To update the displayed image during various events'''
        if self.og_img is None:
            return

        composite = utils.compose(t.applied)
        self.img = composite(self.og_img.copy())
        pixmap = utils.toPixmap(self.img)

        w, h = self.img_frame.width(), self.img_frame.height()
        pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio)
        self.img_frame.setPixmap(pixmap)
