import os
from turtle import width
import numpy as np
import cv2
import tempfile
import traceback
from model.Settings import Settings
from myutils.QtUtils import message_critical, set_label_img

from view.widgets.ApexWeaponConfigWidget import QWeaponConfig


class WeaponConfigController():

    datas = {
        "loading": 0,
        "dq": ["true"],
        "dqrate": 2,
        "debug": ["false"],
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
        self.view.dq.stateChanged.connect(self.updateRate)
        self.view.dqrate.textChanged.connect(self.updateRate)
        self.view.debug.stateChanged.connect(self.updateRate)

        self.view.speed.textChanged.connect(self.updatedata)
        self.view.xrate.textChanged.connect(self.updatedata)
        self.view.yrate.textChanged.connect(self.updatedata)
        self.view.base.textChanged.connect(self.updatedata)
        self.view.single.stateChanged.connect(self.updatedata)
        self.view.weapondata.textChanged.connect(self.updatedata)

    def load_datas(self):
        selectprofile = Settings().resource_dir+"weapondata/" + self.view.weapondataprofiles.currentText()
        with open(selectprofile,"r",encoding="utf-8") as f:
            texts = f.readlines()
        self.datas = {
            "loading": 0,
            "dq": ["true"],
            "dqrate": 2,
            "debug": ["false"],
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
                elif f.find("xrate")>=0:
                    rate = float(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["xrate"] = rate
                elif f.find("yrate")>=0:
                    rate = float(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["yrate"] = rate
                elif f.find("base")>=0:
                    base = float(f.split("=")[-1].split(",")[0].strip())
                    self.datas["weapons"][weapon_name]["base"] = base 
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
            traceback.print_exc()
            message_critical("错误", selectprofile+"配置异常:"+str(e))
            return
        self.fill_ui_data()
            
    def generate_config(self):
        # if not os.path.exists((tempfile.gettempdir()+"/weapon.lua").replace("\\","/")):
        self.apply()

    def block_ui_event(self,block:bool):
        for widget in [self.view.loading,
                       self.view.dq,
                       self.view.speed,
                       self.view.yrate,
                       self.view.xrate,
                       self.view.base,
                       self.view.single,
                       self.view.weapondata
                       ]:
            widget.blockSignals(block)

    def render_recoil_pattern(self,weapon_name):
        pass
        # height = 200
        # xdata = self.datas["weapons"][weapon_name]["countdatax"][1:-1].split(",")
        # ydata = self.datas["weapons"][weapon_name]["countdatay"][1:-1].split(",")
        # xdata = [round(float(x.replace("'","").strip())) for x in xdata]
        # ydata = [round(float(y.replace("'","").strip())) for y in ydata]
        # maxx = abs(sum(xdata))
        # maxy = abs(sum(ydata))
        # img = np.zeros([maxy*3,maxx*3,3],dtype=np.uint8)
        # point = (round(maxx*3/2),round(maxy))
        # for i,y in enumerate(ydata):
        #     x = xdata[i]
        #     if i != 0:
        #         point = (point[0]+int(x),point[1]+int(y))
        #     cv2.circle(img,point,radius=10,color=(0,255,0),thickness=-1)
        # width=round(height/img.shape[0]*img.shape[1])
        # img = cv2.resize(img,(width,height))
        # set_label_img(self.view.weapon_data_result,img)


    def cal_data_result(self):
        try:
            base = float(self.view.base.text())
            xrate = float(self.view.xrate.text())
            yrate = float(self.view.yrate.text())
            datas = self.view.weapondata.toPlainText().replace("{","").replace("},","").replace("}","").split("\n")
            datas_result = {}
            keys_sorted = []
            for d in datas:
                if d.strip() == "":
                    continue
                dsplit = d.split(",")
                keys_sorted.append(int(dsplit[0]))
                datas_result[int(dsplit[0])] = [float(dsplit[1]), float(dsplit[2])]
            keys_sorted.sort()

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

                movex = (offsetx) * xrate
                movey = (base + offsety) * yrate

                countx = countx + movex
                county = county + movey

                countdatax.append("{:.2f}".format(countx))
                countdatay.append("{:.2f}".format(county))
                # self.view.weapon_data_result.append(f"{{{i},{movey},0}}")

            countdatax = str(countdatax).replace("[","{").replace("]","}")
            countdatay = str(countdatay).replace("[","{").replace("]","}")
            # self.view.weapon_data_result.append(countdatax)
            # self.view.weapon_data_result.append(countdatay)
            weapon_name = self.view.weapons.currentText()
            self.datas["weapons"][weapon_name]["countdatax"] = countdatax
            self.datas["weapons"][weapon_name]["countdatay"] = countdatay
            # self.render_recoil_pattern(weapon_name)

        except:
            traceback.print_exc()
            self.view.weapon_data_result.setText("")
        self.apply()

    def fill_ui_data(self):
        self.block_ui_event(True)
        self.view.loading.setText(self.datas["loading"][0])
        self.view.debug.setChecked(self.datas["debug"][0]=="true")
        self.view.dq.setChecked(self.datas["dq"][0]=="true")
        self.view.dqrate.setText(self.datas["dqrate"][0])

        weapon = self.view.weapons.currentText()

        if not weapon in self.datas["weapons"].keys():
            self.view.speed.setText("")
            self.view.yrate.setText("")
            self.view.xrate.setText("")
            self.view.base.setText("")
            self.view.weapondata.setText("")
            self.block_ui_event(False)
            return
        weapon = self.datas["weapons"][weapon]
        self.view.speed.setText(str(weapon["speed"]))
        self.view.yrate.setText(str(weapon["yrate"]))
        self.view.xrate.setText(str(weapon["xrate"]))
        self.view.base.setText(str(weapon["base"]))

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
            if key in ["dq","debug"]:
                result += "{}={{{}}}\n\n".format(key,str(self.datas[key][0]).lower())
                continue
            if key in ["dqrate"]:
                result += "{}={{{}}}\n\n".format(key,self.datas[key][0])
                continue

            result += "{}={{{}}}\n\n".format(key,",".join(self.datas[key]))

        for key in self.datas["weapons"]:
            weapon = self.datas["weapons"][key]
            result += "table[\"{}\"]={{\n".format(key)
            result += "speed={},\n".format(weapon["speed"])
            result += "yrate={},\n".format(weapon["yrate"])
            result += "xrate={},\n".format(weapon["xrate"])
            result += "base={},\n".format(weapon["base"])
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

        try:
            self.datas["dq"] = [self.view.dq.isChecked()]
        except Exception as e:
            return

        try:
            self.datas["dqrate"] = [str(int(self.view.dqrate.text()))]
        except Exception as e:
            self.view.dqrate.setText("2")
            self.view.dqrate.setFocus()
            return

        try:
            self.datas["debug"] = [self.view.debug.isChecked()]
        except Exception as e:
            return
        self.apply()

    def updatedata(self):
        weapon_name = self.view.weapons.currentText()
        if not(self.view.speed.text() and self.view.xrate.text() and self.view.yrate.text() and self.view.base.text()):
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
            weapon["yrate"] = float(self.view.yrate.text())
        except:
            self.view.yrate.setText("")
            # self.weaponrate.setFocus()
            return

        try:
            weapon["xrate"] = float(self.view.xrate.text())
        except:
            self.view.xrate.setText("")
            # self.weaponrate.setFocus()
            return

        try:
            weapon["base"] = float(self.view.base.text())
        except:
            self.view.base.setText("")
            # self.weaponbase.setFocus()
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
