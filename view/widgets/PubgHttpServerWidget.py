from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout

from controller.PubgHttpServerController import HttpServerController


class QHttpServer(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setUI()
        self.controller = HttpServerController(self)

    def setUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.link = QLabel()
        self.link.setOpenExternalLinks(True)
        grid.addWidget(self.link,0, 0)
        self.setLayout(grid)

    def set_url_link(self, link):
        self.link.setText(link)
