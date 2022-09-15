from controller.ApexRecognizer import WeaponRecoginzer
from model.Settings import Settings
from model.ApexStatus import Status
from model.Weapon import Weapon
from myutils.QtUtils import set_label_img, start_q_thread

from PyQt6.QtCore import pyqtSignal, QObject


class RecognizeCommunicate(QObject):
    update = pyqtSignal(dict)
    updateFPS = pyqtSignal(int)

class RecognizeController:

    status = Status()
    recoginizer = None

    def __init__(self,view) -> None:
        self.view = view
        self.c = RecognizeCommunicate()

        if "accuracy" in dir(self.view):
            self.view.accuracy.textChanged.connect(self.change_accuracy)
        self.view.startBtn.stateChanged.connect(self.toggle_rec)
        if "timeSlider" in dir(self.view):
            self.view.timeSlider.valueChanged.connect(self.updateSleepTime)
        if "screenshotBtn" in dir(self.view):
            self.view.screenshotBtn.clicked.connect(self.screenshot)

        self.c.update.connect(self.update)
        self.c.updateFPS.connect(self.updateFPS)

        self.init_ui_with_conf()
    
    def screenshot(self):
        self.recoginizer.screenshot()

    def change_accuracy(self):
        try:
            self.recoginizer.accuracy = float(self.view.accuracy.text())
            self.config["accuracy"] = float(self.view.accuracy.text())
            Settings().save_config_to_json()
        except:
            pass

    def updateSleepTime(self):
        value = self.view.timeSlider.value() / 1000
        self.recoginizer.sleeptime = value
        self.config["sleep"] = self.view.timeSlider.value()
        Settings().save_config_to_json()

    def updateFPS(self,fps):
        fps = int(fps)
        self.view.set_fps(fps)

    def toggle_rec(self):
        if self.recoginizer.run:
            self.recoginizer.run=False
            if hasattr(self,"stop_rec"):
                self.stop_rec()
        else:
            self.recoginizer.start.emit(True)
        
    def load_config(self,name):
        self.config = Settings().get_config(name)
    
    def init_ui_with_conf(self):

        if "config" not in dir(self):
            return

        if "accuracy" not in self.config.keys():
            self.config["accuracy"] = float(self.view.accuracy.text())
        else:
            self.view.accuracy.blockSignals(True)
            self.view.accuracy.setText(str(self.config["accuracy"]))
            self.view.accuracy.blockSignals(False)

        if "sleep" not in self.config.keys():
            self.config["sleep"] = float(self.view.timeSlider.value())
        else:
            self.view.timeSlider.blockSignals(True)
            self.view.timeSlider.setValue(int(self.config["sleep"]))
            self.view.timeSlider.blockSignals(False)

class WeaponRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        self.load_config("weapon")
        super().__init__(view)
        self.start_rec(start)

    def start_rec(self,start:bool=True):
        self.recoginizer = WeaponRecoginzer(self.c,self.config["sleep"]/1000,self.config["accuracy"])
        self.thread = start_q_thread(self.view, self.recoginizer,start)
    
    def stop_rec(self):
        self.status.no_weapon()
        set_label_img(self.view.labelWeapon1, Settings().resource_dir+"weapon_null.png")

        # weaponpath = Settings().resource_dir+"gun/car.png"
        # self.view.set_img1(weaponpath)
        # self.status.weapon.set_weapon_img_path(weaponpath)
        # self.status.write_config()
        # self.status.updateQueue.put("weapon1")

    def update(self, d:dict):
        # if "error" in d:
        #     self.status.no_weapon()
        if "weapon" in d:
            weaponpath = d["weapon"]["weaponpath"]
            if not self.status.weapon:
                self.status.weapon = Weapon()
            if  self.status.weapon.get_weapon_img_path() != weaponpath:
                self.view.set_img1(weaponpath)
                self.status.weapon.set_weapon_img_path(weaponpath)
                self.status.write_config()
                self.status.updateQueue.put("weapon1")
                print("更新武器",self.status.weapon.weapon_name)
        if "currentimg" in d:
            self.view.set_img2(d["currentimg"])
