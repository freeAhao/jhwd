import sys

from view.mainwindow import Gui
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
gui = Gui()
sys.exit(app.exec())