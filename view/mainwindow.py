from fileinput import filename
import sys
import traceback

from PyQt6.QtWidgets import QMainWindow,QTabWidget, QWidget, QGridLayout
# from controller.MacroConfigController import MacroConfigController
# from controller.WeaponConfigController import WeaponConfigController
# from myutils.QtUtils import start_q_thread
# from view.widgets.RecognizerWidget import QAttachmentRecognizer, QPoseRecognizer,QWeaponRecognizer,QBloodFix,QAiFix
# from view.widgets.HttpServerWidget import QHttpServer
# from view.widgets.RecoilAnalyzeWidget import ImageRecoilAnalyze2
from view.widgets.SettingWidget import QSettingWidget
# from view.widgets.WeaponConfigWidget import QWeaponConfig

class Gui(QMainWindow):

    i = None

    def __init__(self) -> None:
        super().__init__()
        try:
            self.ui()
            self.show()
        except Exception as e:
            traceback.print_exc()
            sys.exit()

    def ui(self):
        w = QTabWidget()
        w.addTab(QSettingWidget(apptab=w),"设置")
        self.setWindowTitle("鸡壶吴迪")
        self.setCentralWidget(w)