from PyQt5.QtWidgets import QApplication
import sys
from app import App

app = QApplication(sys.argv)
ex = App()
app.exec_()
