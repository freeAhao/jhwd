import sys
import tempfile
import traceback
import requests
from lxml import etree
import zipfile
import os
import shutil
from model.Settings import Settings
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import  QWidget, QGridLayout,QMessageBox,QLabel,QPushButton,QRadioButton,QGroupBox

from myutils.IMGutil import  get_screen_nums
from myutils.QtUtils import  apprestart, message_critical
from view.widgets.AIWidget import QAiFix, QAntiShakeFix,QBloodFix
from view.widgets.PubgAutoRecognizer import PubgAutoRecognizer
from view.widgets.RecoilAnalyzeWidget import ImageRecoilAnalyze
from controller.PubgMacroConfigController import MacroConfigController as PubgMacroConfigController
from controller.PubgWeaponConfigController import WeaponConfigController as PubgWeaponConfigController
from view.widgets.ApexAutoRecognizer import ApexAutoRecognizer
from controller.ApexMacroConfigController import MacroConfigController as ApexMacroConfigController
from controller.ApexWeaponConfigController import WeaponConfigController as ApexWeaponConfigController

class QSettingWidget(QWidget):
    grid = QGridLayout()
    setting = Settings()
    apptab = None
    def __init__(self,apptab) -> None:
        super().__init__()
        self.apptab = apptab
        self.grid.addWidget(QGameSettingWidget(self))
        # self.grid.addWidget(QUpdateWidget())
        self.setLayout(self.grid)

class Updater(QObject):

    start = pyqtSignal(bool)
    source = {
        "GITHUB": {
            "resource_url": "https://github.com/freeAhao/jhwd/commits/source/resource",
            "resource_xpath": "//clipboard-copy/@value",
            "resource_download_url": "https://github.com/freeAhao/jhwd/archive/refs/heads/source.zip",
            "app_url": "https://github.com/freeAhao/jhwd/releases",
            "app_xpath": "//h1[@class='d-inline mr-3']/a/@href",
            "app_download_url": "https://github.com/freeAhao/jhwd/releases/download/{}/release.zip",
        }
    }

    setting = Settings()
    csource = None

    def download(self,zipname, url):
        try:
            if not os.path.exists(zipname):
                with requests.get(url,stream=True) as r:
                    with open(zipname,"wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                return True
        except:
            raise Exception("????????????")
                    
    def extract(self,zipname,updatetype,commit=""):

        if updatetype == 0:
            parentFolder = "jhwd-source/"
        elif updatetype == 1:
            parentFolder = ""

        if zipfile.is_zipfile(zipname):
            f = zipfile.ZipFile(zipname)
            listOfFileNames = f.namelist()
            if updatetype==0:
                # ????????????
                if os.path.exists("./resource-??????/"):
                    shutil.rmtree("./resource-??????")
                shutil.move("./resource/","./resource-??????/")
            for fileName in listOfFileNames:
                try:
                    if updatetype==0 and fileName.startswith(parentFolder+"resource/"):
                        # ????????????
                        f.extract(fileName,".")
                        shutil.move(fileName,fileName.replace(parentFolder,"./"))
                        shutil.rmtree(parentFolder)
                    elif updatetype==1 and fileName.startswith("app.exe"):
                        f.extract(fileName,"./app-update/")
                        shutil.move("./app-update/app.exe","./app-{}.exe".format(commit))
                        shutil.rmtree("./app-update/")
                except:
                    traceback.print_exc()
        if updatetype==0:
            Settings().app_config["commit1"] = commit
        elif updatetype==1:
            Settings().app_config["commit2"] = commit
        Settings().save_app_config_to_json()

    def check_update(self,updatetype):
        try:
            if updatetype==0:
                res = requests.get(self.source[self.csource]["resource_url"],timeout=5,headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                })
                page = etree.HTML(res.content)
                commits = page.xpath(self.source[self.csource]["resource_xpath"])
                if commits:
                    commits = str(commits[0])
            elif updatetype==1:
                res = requests.get(self.source[self.csource]["app_url"],timeout=5)
                page = etree.HTML(res.content)
                commits = page.xpath(self.source[self.csource]["app_xpath"])
                if commits:
                    commits = str(commits[0]).split("/")[-1]

            if res.status_code != 200 or not commits or len(commits)==0:
                raise Exception("??????????????????")

            if updatetype == 0:
                return not ("commit1" in self.setting.app_config and commits == self.setting.app_config["commit1"]), commits
            elif updatetype == 1:
                return not ("commit2" in self.setting.app_config and commits == self.setting.app_config["commit2"]), commits
        except Exception as e:
            QMessageBox.critical(None,"??????","????????????:"+str(e))
            return False,None

    def check(self):
        resource_update, commitres = self.check_update(0)
        app_update, commitapp = self.check_update(1)
        if resource_update:
            resres = QMessageBox.question(None,"??????","??????????????????????????????????????????")
        if app_update:
            resapp = QMessageBox.question(None,"??????","??????app?????????????????????")
        result = ""
        if resource_update and "Yes" in str(resres):
            try:
                zipname = "resource-{}.zip".format(commitres[:6])
                self.download(zipname, self.resource_downloadurl)
                self.extract(zipname, 0,commitres)
                result += "???????????????????????????\n"
            except Exception as e:
                print(e.with_traceback())
                result += "??????????????????????????????"+str(e)+"\n"

        if app_update and "Yes" in str(resapp):
            try:
                zipname = "app-{}.zip".format(commitapp[:6])
                self.download(zipname, self.app_downloadurl)
                self.extract(zipname,1,commitapp)
                result += "app????????????\n"
            except Exception as e:
                print(e.with_traceback())
                result += "app???????????????"+str(e)+"\n"
        if (resource_update and "Yes" in str(resres)) or (app_update and "Yes" in str(resapp)):
            QMessageBox.information(None,"??????","????????????????????????:\n"+str(result))
            sys.exit()
    
    def choose_source(self, csource):
        if not csource in self.source:
            return False
        self.csource = csource
        self.setting.config["app"]["update"] = csource
        self.setting.save_config_to_json()

    def __init__(self) -> None:
        super().__init__()
        self.start.connect(self.check)
        try:
            self.csource = self.setting.app_config["update"]
        except:
            self.csource = "GITHUB"

class QUpdateWidget(QWidget):

    grid = QGridLayout()
    setting = Settings()
    u = Updater()

    def __init__(self) -> None:
        super().__init__()
        self.ui()
        self.setLayout(self.grid)
        self.load_datas()

    def ui(self):

        self.sourceBTNS = []
        btnbox = QGroupBox("?????????")
        btngrid = QGridLayout()
        for btn in ["GITHUB"]:
            radiobtn = QRadioButton(btn)
            radiobtn.clicked.connect(self.choose_source)
            radiobtn.setObjectName(btn)

            self.sourceBTNS.append(radiobtn)
            btngrid.addWidget(radiobtn)
        btnbox.setLayout(btngrid)

        try:
            source = self.setting.app_config["update"]
            for btn in self.sourceBTNS:
                btn.setChecked(str(source).upper()==btn.objectName())
        except:
            default = 'GITHUB'
            btn = [btn if btn.objectName() == default else None for btn in self.sourceBTNS][0]
            btn.setChecked(True)
            self.u.choose_source(default)

        self.label = QLabel("")
        self.labelupdate = QLabel("")
        self.labelnotiece = QLabel()
        self.labelnotiece.setOpenExternalLinks(True)

        self.checkbtn = QPushButton("????????????")
        self.checkbtn.clicked.connect(self.check)
        self.downbtn = QPushButton("??????")
        self.downbtn.setEnabled(False)
        self.downbtn.clicked.connect(self.down)

        self.grid.setSpacing(10)
        self.grid.addWidget(btnbox)
        self.grid.addWidget(self.label)
        self.grid.addWidget(self.labelupdate)
        self.grid.addWidget(self.labelnotiece)
        self.grid.addWidget(self.checkbtn)
        self.grid.addWidget(self.downbtn)
        self.setLayout(self.grid)
    
    def choose_source(self):
        for btn in self.sourceBTNS:
            if btn.isChecked():
                self.u.choose_source(btn.objectName())
                break
        
    def down(self):
        result = ""
        if self.resource_update and self.commitres:
            try:
                zipname = "resource-{}.zip".format(self.commitres[:6])
                self.u.download(zipname, self.u.source[self.u.csource]["resource_download_url"])
                self.u.extract(zipname, 0,self.commitres)
                result += "???????????????????????????\n"
            except Exception as e:
                traceback.print_exc()
                result += "??????????????????????????????"+str(e)+"\n"

        if self.app_update and self.commitapp:
            try:
                zipname = "app-{}.zip".format(self.commitapp[:6])
                self.u.download(zipname, self.u.source[self.u.csource]["app_download_url"].format(self.commitapp))
                self.u.extract(zipname,1,self.commitapp)
                result += "app????????????\n"
            except Exception as e:
                traceback.print_exc()
                result += "app???????????????"+str(e)+"\n"
        self.labelupdate.setText(result)
        QMessageBox.information(None,"??????","????????????????????????:\n"+str(result))
        sys.exit()

    def check(self):
        resource_update, commitres = self.u.check_update(0)
        app_update, commitapp = self.u.check_update(1)
        self.resource_update = resource_update
        self.commitres = commitres
        self.app_update = app_update
        self.commitapp = commitapp

        result = ""

        if resource_update and commitres:
            result += "????????????????????????{}\n".format(commitres)
        if app_update and commitapp:
            result += "app????????????{}\n".format(commitapp)

        if not (resource_update or app_update):
            self.resource_update = None
            self.commitres = None
            self.app_update = None
            self.commitapp = None
            self.labelupdate.setText("??????????????????")
            self.downbtn.setEnabled(False)
        else:
            self.downbtn.setEnabled(True)
            self.labelupdate.setText(result)
            
    def load_datas(self):
        result = ""
        result += "?????????????????????{}\n".format(self.setting.app_config["commit1"] if "commit1" in self.setting.app_config else "??????")
        result += "??????app?????????{}\n".format(self.setting.app_config["commit2"] if "commit2" in self.setting.app_config else "??????")

        self.label.setText(result)

class QGameSettingWidget(QWidget):
    grid = QGridLayout()
    setting = Settings()
    appsettingWidget:QSettingWidget = None

    gameBTNS = []
    monitorBTNS = []


    def __init__(self,settingWidget:QSettingWidget) -> None:
        super().__init__()
        self.settingWidget = settingWidget
        gameBtnGroup = QGroupBox("??????")
        gameBtnGroupLayout = QGridLayout()
        gameBtnGroup.setLayout(gameBtnGroupLayout)

        for game in ["APEX","PUBG"]:
            gameBTN = QRadioButton(game)
            gameBTN.setObjectName(game)
            gameBtnGroupLayout.addWidget(gameBTN)
            gameBTN.clicked.connect(self.select_game)
            self.gameBTNS.append(gameBTN)
            gameBTN.setChecked(game == Settings().app_config["game"])


        screenBTNGroup = QGroupBox("???????????????")
        screenBTNGroupLayout = QGridLayout()
        screenBTNGroup.setLayout(screenBTNGroupLayout)
        monitors = get_screen_nums()[1:]
        for index,screen in enumerate(monitors):
            screenBTN = QRadioButton("?????????{}:{}x{}".format(index+1,screen["width"],screen["height"]))
            screenBTN.setObjectName(str(index+1))
            screenBTNGroupLayout.addWidget(screenBTN)
            screenBTN.clicked.connect(self.select_monitor)
            self.monitorBTNS.append(screenBTN)
            screenBTN.setChecked(int(Settings().app_config["monitor"])==index+1)
        
        updateWidget = QUpdateWidget()

        self.grid.addWidget(gameBtnGroup)
        self.grid.addWidget(screenBTNGroup)
        # self.grid.addWidget(updateWidget)
        self.setLayout(self.grid)

        self.init_models()

    def select_game(self):

        for btn in self.gameBTNS:
            if not btn.isChecked():
                continue
            game = btn.objectName()
            break

        if game == Settings().app_config["game"]:
            return

        Settings().change_game(game)
        Settings().save_app_config_to_json()
        self.clean_config()
        apprestart()

    def clean_config(self):
        tempdir = tempfile.gettempdir()
        for i in ["config.lua","weapon.lua","x.lua"]:
            f = tempdir+"\\"+i
            try:
                os.unlink(f.replace("\\","/"))
            except Exception as e:
                traceback.print_exc()
                continue

    def init_models(self,game=None):
        if not self.settingWidget and self.settingWidget.apptab:
            return

        tab = self.settingWidget.apptab

        if game == None:
            game = Settings().app_config["game"]
        if game == "PUBG":
            try:
                recognizer = PubgAutoRecognizer()
                bloodfix = QBloodFix()
                ai = QAiFix()
                antishake = QAntiShakeFix()
                macro = PubgMacroConfigController().view
                weapon = PubgWeaponConfigController().view
                recoil = ImageRecoilAnalyze()

                tab.addTab(recognizer,"????????????")
                tab.addTab(bloodfix,"??????")
                tab.addTab(ai,"AI")
                tab.addTab(antishake,"??????")
                tab.addTab(macro,"?????????")
                tab.addTab(weapon,"????????????")
                tab.addTab(recoil,"??????????????????")
            except Exception as e:
                traceback.print_exc()
                message_critical("??????",str(e))

        elif game == "APEX":
            try:
                recognizer = ApexAutoRecognizer()
                bloodfix = QBloodFix()
                ai = QAiFix()
                antishake = QAntiShakeFix()
                macro = ApexMacroConfigController().view
                weapon = ApexWeaponConfigController().view
                recoil = ImageRecoilAnalyze()
                tab.addTab(recognizer,"????????????")
                tab.addTab(bloodfix,"??????")
                tab.addTab(ai,"AI")
                tab.addTab(antishake,"??????")
                tab.addTab(macro,"?????????")
                tab.addTab(weapon,"????????????")
                tab.addTab(recoil,"??????????????????")
            except Exception as e:
                traceback.print_exc()
                message_critical("??????",str(e))

    def select_monitor(self):
        for btn in self.monitorBTNS:
            if not btn.isChecked():
                continue
            monitor = btn.objectName()
            break
        Settings().app_config["monitor"] = monitor
        Settings().save_app_config_to_json()
        apprestart()