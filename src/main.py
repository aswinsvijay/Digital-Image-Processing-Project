from Qt5 import QApplication
import sys
from app import App

app = QApplication(sys.argv)
ex = App()
app.exec()
