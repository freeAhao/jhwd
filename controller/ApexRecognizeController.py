from controller.ApexRecognizer import AIRecoginzer, BloodRecoginzer, WeaponRecoginzer
from model.Settings import Settings
from model.Status import Status
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
            if self.status.weapon.get_weapon_img_path() != weaponpath:
                print("更新武器")
                self.view.set_img1(weaponpath)
                self.status.weapon.set_weapon_img_path(weaponpath)
                self.status.write_config()
                self.status.updateQueue.put("weapon1")
        if "currentimg" in d:
            self.view.set_img2(d["currentimg"])


class BloodRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        super().__init__(view)
        self.start_rec(start)

        self.view.xRate.valueChanged.connect(self.changeRate)
        self.view.yRate.valueChanged.connect(self.changeRate)

        self.view.h.valueChanged.connect(self.changeColor)
        self.view.s.valueChanged.connect(self.changeColor)
        self.view.v.valueChanged.connect(self.changeColor)

    def start_rec(self,start:bool=True):
        self.recoginizer = BloodRecoginzer(self.c,0.001)
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self, d:dict):
        if "img" in d:
            self.view.set_img(d["img"])
        elif "move" in d:
            movex = d["move"][0]
            movey = d["move"][1]
            self.status.change_fix(movex,movey)
            self.view.set_move(movex,movey)

    def changeRate(self):
        xRate = self.view.xRate.value()/100
        yRate = self.view.yRate.value()/100
        self.recoginizer.xrate = xRate
        self.recoginizer.yrate = yRate

    def changeColor(self):
        h = self.view.h.value()
        s = self.view.s.value()
        v = self.view.v.value()
        self.recoginizer.h = h
        self.recoginizer.s = s
        self.recoginizer.v = v 

class AIRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        super().__init__(view)
        self.start_rec(start)

        self.view.xRate.valueChanged.connect(self.changeRate)
        self.view.yRate.valueChanged.connect(self.changeRate)
        self.view.airegion.valueChanged.connect(self.changeAiRegion)
        self.view.fixregion.valueChanged.connect(self.changeFixRegion)

        for btn in [ self.view.ordmlBTN, self.view.ovinoBTN, self.view.ptorchBTN, self.view.tensortBTN]:
            btn.clicked.connect(self.changeEngine)

    def start_rec(self,start:bool=True):
        self.recoginizer = AIRecoginzer(self.c,0.001)
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self, d:dict):
        if "img" in d:
            self.view.set_img(d["img"])
        elif "move" in d:
            movex = d["move"][0]
            movey = d["move"][1]
            self.status.change_fix(movex,movey)
            self.view.set_move(movex,movey)
    
    def changeEngine(self):
        for btn in [self.view.ordmlBTN, self.view.ovinoBTN, self.view.ptorchBTN, self.view.tensortBTN]:
            if btn.isChecked():
                if btn == self.view.ordmlBTN:
                    self.recoginizer.changeEngine("onnxruntime")
                elif btn == self.view.ovinoBTN:
                    self.recoginizer.changeEngine("openvino")
                elif btn == self.view.ptorchBTN:
                    # self.recoginizer.changeEngine("pytorch")
                    pass
                elif btn == self.view.tensortBTN:
                    # self.recoginizer.changeEngine("tensortrt")
                    pass
                break

    def changeRate(self):
        xRate = self.view.xRate.value()/100
        yRate = self.view.yRate.value()/100
        self.recoginizer.xrate = xRate
        self.recoginizer.yrate = yRate

    def changeAiRegion(self):
        airegion = self.view.airegion.value()
        self.recoginizer.ai.airegion = airegion

    def changeFixRegion(self):
        fixregion = self.view.fixregion.value()
        self.recoginizer.ai.fixregion = fixregion