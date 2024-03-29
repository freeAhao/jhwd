from datetime import datetime
from controller.PubgRecognizer import  PoseRecoginzer,WeaponRecoginzer,AttachmentRecoginzer
from model.Settings import Settings
from model.PubgStatus import Status
from model.Weapon import Weapon
from myutils.QtUtils import set_label_img, start_q_thread
from controller.PubgRecognizer import Recognizer

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

    def toggle_rec(self):
        if self.recoginizer.run:
            self.recoginizer.run=False
            try:
                self.reset_status()
            except:
                pass
        else:
            self.recoginizer.start.emit(True)
    
    def updateSleepTime(self):
        value = self.view.timeSlider.value() / 1000
        self.recoginizer.sleeptime = value
        self.config["sleep"] = self.view.timeSlider.value()
        Settings().save_config_to_json()

    def updateFPS(self,fps):
        fps = int(fps)
        self.view.set_fps(fps)
        
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

    def update(self, d:dict):

        if "weapon1" in d:
            weaponpath = d["weapon1"]["path"]
            # if self.status.weapon1.get_weapon_img_path() != weaponpath:
            if self.status.weapon1.weapon_name != weaponpath.split("/")[-1].split(".")[0].split("_")[0]:
                print("更新武器1",self.status.weapon1.weapon_name,weaponpath.split("/")[-1].split(".")[0].split("_"))
                self.view.set_img1(weaponpath)
                self.status.weapon1.set_weapon_img_path(weaponpath)
                self.status.write_config()
                self.status.updateQueue.put("weapon1")
            self.view.set_similarity(d["weapon1"]["similarity"],1)

            self.view.set_tips("匹配文件：{}\n相似度：{}".format(d["weapon1"]["path"],d["weapon1"]["similarity"]), 1)

        if "weapon2" in d:
            weaponpath = d["weapon2"]["path"]
            # if self.status.weapon2.get_weapon_img_path() != weaponpath:
            if self.status.weapon2.weapon_name != weaponpath.split("/")[-1].split(".")[0].split("_")[0]:
                print("更新武器2",self.status.weapon2.weapon_name,weaponpath.split("/")[-1].split(".")[0].split("_"))
                self.view.set_img2(weaponpath)
                self.status.weapon2.set_weapon_img_path(weaponpath)
                self.status.write_config()
                self.status.updateQueue.put("weapon2")
            self.view.set_similarity(d["weapon2"]["similarity"],2)
            self.view.set_tips("匹配文件：{}\n相似度：{}".format(d["weapon2"]["path"],d["weapon2"]["similarity"]), 2)

        if "currentweapon" in d:
            weaponnum  = d["currentweapon"]
            if self.status.weapon != weaponnum:
                print("切换武器"+str(weaponnum))
                weapon = self.status.change_weapon(weaponnum)
                self.status.write_config("change weapon to {}".format(weapon.weapon_name),True)
                self.status.updateQueue.put("changeweapon")
    def reset_status(self):
        self.status.no_weapon()

class PoseRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        self.load_config("pose")
        super().__init__(view)
        self.start_rec(start)

    def start_rec(self,start:bool=True):
        self.recoginizer = PoseRecoginzer(self.c,self.config["sleep"]/1000,self.config["accuracy"])
        self.thread = start_q_thread(self.view, self.recoginizer)

    def update(self, d:dict):
        if "posepath" in d:
            pose = int(d["posepath"].split("/")[-1].split(".")[0])
            if self.status.pose != pose:
                self.view.set_img(d["posepath"])
                self.status.pose = pose
                self.status.write_config()
                self.status.updateQueue.put("pose")
            self.view.set_similarity(d["similarity"])
            self.view.set_tips("匹配文件：{}\n相似度：{}".format(d["posepath"],d["similarity"]))

    def reset_status(self):
        self.status.no_pose()

class AttachmentRecognizeController(RecognizeController):

    def __init__(self, view,start:bool) -> None:
        self.load_config("attachment")
        super().__init__(view)
        self.start_rec(start)

    def start_rec(self,start:bool=True):
        self.recoginizer = AttachmentRecoginzer(self.c,self.config["sleep"]/1000,self.config["accuracy"])
        self.thread = start_q_thread(self.view, self.recoginizer,start)

    def update(self, d:dict):

        updated = False

        w1attachment = d["weapon1"]
        for index,attachment in enumerate(w1attachment):
            path = attachment[1]
            if self.status.weapon1.set_attachment(index, path):
                updated = True

        w2attachment = d["weapon2"]
        for index,attachment in enumerate(w2attachment):
            path = attachment[1]
            if self.status.weapon2.set_attachment(index, path):
                updated = True
        
        if updated:
            for index,attachment in enumerate(w2attachment):
                print("武器2配件更新")
                path = attachment[1]
                similarity = attachment[2]
                if path == None:
                    path = Settings().resource_dir+"attachments/null.png"  if index == 0 else path
                    path = Settings().resource_dir+"attachments/2/4.png"  if index == 1 else path
                    path = Settings().resource_dir+"attachments/3/7.png"  if index == 2 else path
                    path = Settings().resource_dir+"attachments/4/4.png"  if index == 3 else path
                    path = Settings().resource_dir+"attachments/5/2.png"  if index == 4 else path
                self.view.set_attachment2(index,path,similarity)
                self.view.set_tips(index,"匹配图片：{}\n相似度：{}".format(path,similarity),2)
            for index,attachment in enumerate(w1attachment):
                print("武器1配件更新")
                path = attachment[1]
                similarity = attachment[2]
                if path == None:
                    path = Settings().resource_dir+"attachments/null.png"  if index == 0 else path
                    path = Settings().resource_dir+"attachments/2/4.png"  if index == 1 else path
                    path = Settings().resource_dir+"attachments/3/7.png"  if index == 2 else path
                    path = Settings().resource_dir+"attachments/4/4.png"  if index == 3 else path
                    path = Settings().resource_dir+"attachments/5/2.png"  if index == 4 else path
                self.view.set_attachment1(index,path,similarity)
                self.view.set_tips(index,"匹配图片：{}\n相似度：{}".format(path,similarity),1)
            self.status.updateQueue.put("attachment")
            self.status.write_config("attachment updated", False)