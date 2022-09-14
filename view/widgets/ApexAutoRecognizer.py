from PyQt6.QtWidgets import QWidget, QGridLayout,QComboBox
from view.widgets.ApexRecognizerWidget import QWeaponRecognizer

class ApexAutoRecognizer(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setUI()

    def setUI(self):
        grid = QGridLayout()

        wrec = QWeaponRecognizer()
        # http = QHttpServer()


        grid.addWidget(wrec, 0, 0)
        # grid.addWidget(http, 1, 0)


        self.setLayout(grid)
