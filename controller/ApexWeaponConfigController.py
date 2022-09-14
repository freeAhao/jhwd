import os
import tempfile
import traceback
from model.Settings import Settings
from myutils.QtUtils import message_critical

from view.widgets.ApexWeaponConfigWidget import QWeaponConfig


class WeaponConfigController():

    datas = {
        "loading": 0,
        "weapons":{}
    }

    def __init__(self) -> None:
        super().__init__()
        self.view = QWeaponConfig()
        self.init_ui_data()
        self.init_ui_eventbind()

        self.load_datas()

        self.generate_config()

    def init_ui_data(self):

        for i in os.listdir(Settings().resource_dir+"weapondata/"):
            self.view.weapondataprofiles.addItem(i)

        # self.view.load_resources(self.view.poses,Settings().resource_dir+"pos/")
        # self.view.load_resources(self.view.scopes,Settings().resource_dir+"attachments/1/")
        # self.view.load_resources(self.view.a2,Settings().resource_dir+"attachments/2/")
        # self.view.load_resources(self.view.a3,Settings().resource_dir+"attachments/3/")
        self.view.load_resources(self.view.weapons,Settings().resource_dir+"gun/")

    def init_ui_eventbind(self):
        self.view.weapondataprofiles.currentIndexChanged.connect(lambda:self.load_datas())
        self.view.weapons.currentIndexChanged.connect(self.fill_ui_data)

        self.view.saveButton.clicked.connect(self.apply)
        self.view.delButton.clicked.connect(self.delteweapon)

        self.view.loading.textChanged.connect(self.updateRate)

        self.view.speed.textChanged.connect(self.updatedata)
        self.view.rate.textChanged.connect(self.updatedata)
        self.view.base.textChanged.connect(self.updatedata)
        self.view.maxbullet.textChanged.connect(self.updatedata)
        self.view.single.stateChanged.connect(self.updatedata)
        self.view.weapondata.textChanged.connect(self.updatedata)

    def load_datas(self):
        selectprofile = Settings().resource_dir+"weapondata/" + self.view.weapondataprofiles.currentText()
        with open(selectprofile,"r",encoding="utf-8") as f:
            texts = f.readlines()
        self.datas = {
            "loading": 0,
            "weapons": {}
        }

        weapon_name = None
        try:
            for f in texts:
                is_weapon_data = True
                # global sensitive
                for k in self.datas.keys():
                    if f.find(k)>=0:
                        leftquote = f.split("=")[-1].find("{")
                        rightquote = f.split("=")[-1].find("}")
                        self.datas[k] = f.split("=")[-1][leftquote+1:rightquote].split(",")
                        is_weapon_data = False
                if not is_weapon_data:
                    continue
                # weapon
                if f.find("table[") >= 0:
                    leftquote = f.find("[")
                    rightquote = f.find("]")
                    weapon_name = f[leftquote+2:rightquote-1]
                    self.datas["weapons"][weapon_name] = {}
                    self.datas["weapons"][weapon_name]["ballistic"] = []
                    continue
                elif f.find("speed")>=0:
                    speed = int(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["speed"] = speed
                elif f.find("limit")>=0:
                    limit = float(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["limit"] = limit
                elif f.find("base")>=0:
                    base = float(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["base"] = base 
                elif f.find("max")>=0:
                    max = int(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["max"] = max
                elif f.find("countdatax")>=0:
                    leftquote = f.find("{")
                    rightquote = f.find("}")
                    countdatax = f[leftquote:rightquote+1]
                    self.datas["weapons"][weapon_name]["countdatax"] = countdatax
                elif f.find("countdatay")>=0:
                    leftquote = f.find("{")
                    rightquote = f.find("}")
                    countdatay = f[leftquote:rightquote+1]
                    self.datas["weapons"][weapon_name]["countdatay"] = countdatay
                elif f.count(",") >= 2:
                    leftquote = f.find("{")
                    rightquote = f.find("}")
                    ballistic = f[leftquote+1:rightquote]
                    self.datas["weapons"][weapon_name]["ballistic"].append(ballistic)
                elif f.find("single")>=0: 
                    self.datas["weapons"][weapon_name]["single"] = f.find("true") > 0
        except Exception as e:
            print(traceback.print_exc())
            message_critical("错误", selectprofile+"配置异常:"+str(e))
            return
        self.fill_ui_data()
            
    def generate_config(self):
        # if not os.path.exists((tempfile.gettempdir()+"/weapon.lua").replace("\\","/")):
        self.apply()

    def block_ui_event(self,block:bool):
        for widget in [self.view.loading,
                       self.view.speed,
                       self.view.rate,
                       self.view.maxbullet,
                       self.view.base,
                       self.view.single,
                       self.view.weapondata
                       ]:
            widget.blockSignals(block)
    
    def cal_data_result(self):
        try:
            maxbullet = int(self.view.maxbullet.text())
            base = float(self.view.base.text())
            rate = float(self.view.rate.text())
            datas = self.view.weapondata.toPlainText().replace("{","").replace("},","").replace("}","").split("\n")
            datas_result = {}
            keys_sorted = []
            for d in datas:
                if d.strip() == "":
                    continue
                dsplit = d.split(",")
                keys_sorted.append(int(dsplit[0]))
                datas_result[int(dsplit[0])] = [int(dsplit[1]), int(dsplit[2])]
            keys_sorted.sort()

            self.view.weapon_data_result.setText("这里显示最终结果")
            countx = 0
            county = 0
            countdatax = []
            countdatay = []
            for i in range(1,keys_sorted[-1]+1):
                for index,key in enumerate(keys_sorted):
                    if index+1 == len(keys_sorted):
                        offsety = datas_result[key][0]
                        offsetx = datas_result[key][1]
                        break
                    if i>=key and i< keys_sorted[index+1]:
                        offsety = datas_result[key][0]
                        offsetx = datas_result[key][1]
                        break

                movex = round((offsetx) * rate)
                movey = round((base + offsety) * rate)

                countx = countx + movex
                county = county + movey

                countdatax.append(countx)
                countdatay.append(county)
                self.view.weapon_data_result.append(f"{{{i},{movey},0}}")

            countdatax = str(countdatax).replace("[","{").replace("]","}")
            countdatay = str(countdatay).replace("[","{").replace("]","}")
            self.view.weapon_data_result.append(countdatax)
            self.view.weapon_data_result.append(countdatay)
            weapon_name = self.view.weapons.currentText()
            self.datas["weapons"][weapon_name]["countdatax"] = countdatax
            self.datas["weapons"][weapon_name]["countdatay"] = countdatay

        except:
            self.view.weapon_data_result.setText("")

    def fill_ui_data(self):
        self.block_ui_event(True)
        self.view.loading.setText(self.datas["loading"][0])

        weapon = self.view.weapons.currentText()

        if not weapon in self.datas["weapons"].keys():
            self.view.speed.setText("")
            self.view.rate.setText("")
            self.view.base.setText("")
            self.view.maxbullet.setText("")
            self.view.weapondata.setText("")
            self.block_ui_event(False)
            return

        weapon = self.datas["weapons"][weapon]
        self.view.speed.setText(str(weapon["speed"]))
        self.view.rate.setText(str(weapon["limit"]))
        self.view.base.setText(str(weapon["base"]))
        self.view.maxbullet.setText(str(weapon["max"]))

        if "single" in weapon.keys():
            self.view.single.setChecked(weapon["single"])
        else:
            self.view.single.setChecked(False)

        datas = weapon["ballistic"]
        datatext= ""
        for d in datas:
            datatext += "{" + d + "},\n"
        self.view.weapondata.setText(datatext)

        self.cal_data_result()

        self.block_ui_event(False)


    def delteweapon(self):
        weapon_name = self.view.weapons.currentText()
        del self.datas["weapons"][weapon_name]
        self.fill_ui_data()

    def apply(self):
        result = ""

        for key in self.datas:
            if key == "weapons":
                continue
            result += "{}={{{}}}\n\n".format(key,",".join(self.datas[key]))

        for key in self.datas["weapons"]:
            weapon = self.datas["weapons"][key]
            result += "table[\"{}\"]={{\n".format(key)
            result += "speed={},\n".format(weapon["speed"])
            result += "limit={},\n".format(weapon["limit"])
            result += "base={},\n".format(weapon["base"])
            result += "max={},\n".format(weapon["max"])
            result += "single={},\n".format("true" if "single" in weapon and weapon["single"] else "false")
            result += "countdatax={},\n".format(weapon["countdatax"])
            result += "countdatay={},\n".format(weapon["countdatay"])
            result += "ballistic={\n"
            for d in weapon["ballistic"]:
                result += "{{{}}},\n".format(d)
            result += "}\n"
            result += "}\n"

        with open(Settings().resource_dir+"weapondata/"+self.view.weapondataprofiles.currentText(), "w") as f:
            f.write(result)

        with open(tempfile.tempdir+"/weapon.lua","w") as f:
            f.write(result)
    
    def updateRate(self):

        try:
            int(self.view.loading.text())
            self.datas["loading"] = [str(int(self.view.loading.text()))]
        except Exception as e:
            self.view.loading.setText("")
            self.view.loading.setFocus()
            return


    def updatedata(self):
        weapon_name = self.view.weapons.currentText()
        if not(self.view.speed.text() and self.view.rate.text() and self.view.base.text() and self.view.maxbullet.text()):
            return

        if not weapon_name in self.datas["weapons"].keys():
            weapon = {}
        else:
            weapon = self.datas["weapons"][weapon_name]

        try:
            weapon["speed"] = int(self.view.speed.text())
        except:
            self.view.speed.setText("")
            # self.weaponspeed.setFocus()
            return

        try:
            weapon["limit"] = float(self.view.rate.text())
        except:
            self.view.rate.setText("")
            # self.weaponrate.setFocus()
            return

        try:
            weapon["base"] = float(self.view.base.text())
        except:
            self.view.base.setText("")
            # self.weaponbase.setFocus()
            return

        try:
            weapon["max"] = int(self.view.maxbullet.text())
        except:
            self.view.bullet.setText("")
            # self.weaponmaxbullet.setFocus()
            return

        weapon["single"] = self.view.single.isChecked()

        weapondatatext = self.view.weapondata.toPlainText()
        datas = []
        for f in weapondatatext.split("\n"):
            if f.strip() == "":
                continue
            leftquote = f.find("{")
            rightquote = f.find("}")
            if not f.count(",") >= 2:
                self.view.weapondata.setFocus()
                return
            datas.append(f[leftquote+1:rightquote])

        weapon["ballistic"] = datas

        if weapon_name not in self.datas["weapons"].keys():
            self.datas["weapons"][weapon_name] = weapon
        
        self.cal_data_result()
