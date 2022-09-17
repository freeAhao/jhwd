import os
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QCheckBox, QSlider, QGroupBox, QComboBox, QTableWidget,QAbstractItemView,QPushButton, QTableWidgetItem,QLineEdit,QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
import tempfile
from time import time

class QWeaponConfig(QWidget):

    grid = QGridLayout()

    def __init__(self) -> None:
        super().__init__()

        self.ui()
        # self.load_datas()

        self.setLayout(self.grid)


    def load_resources(self, combobox, resdir):
        for f in os.listdir(resdir):
            if f.find("_")>0:
                continue
            combobox.setIconSize(QSize(40,40))
            if not f.endswith("png"):
                continue
            combobox.addItem(QIcon(resdir+f),f.split("/")[-1].split(".")[0])

    def lineedit_with_label(self,labeltext,edit):
        group = QGroupBox()
        label = QLabel(labeltext)
        grid = QGridLayout()
        grid.addWidget(label,0,0)
        grid.addWidget(edit,0,1)
        group.setLayout(grid)
        return group 
 
    def ui(self):
        group = QGroupBox("全局设置")
        grid = QGridLayout()

        weapondataprofiles = QComboBox()
        weapondataprofilesgroup = self.lineedit_with_label("预设弹道",weapondataprofiles)

        debug = QCheckBox("debug弹道调试")

        loading = QLineEdit()
        loadinggroup = self.lineedit_with_label("cpu负载",loading)
        dq = QCheckBox("抖枪")
        dqrate = QLineEdit("2")
        dqrategroup = self.lineedit_with_label("抖枪强度",dqrate)


        grid.addWidget(weapondataprofilesgroup,0,0,1,2)
        grid.addWidget(loadinggroup,1,0,1,2)
        grid.addWidget(debug,2,0)
        grid.addWidget(dq,3,0)
        grid.addWidget(dqrategroup,3,1)
        group.setLayout(grid)
        self.grid.addWidget(group,0,0)

        group = QGroupBox("武器")
        grid = QGridLayout()

        weapons = QComboBox()

        weaponspeedEdit = QLineEdit()
        weaponspeed = self.lineedit_with_label("射速",weaponspeedEdit)

        weaponmaxbulletEdit = QLineEdit()
        weaponmaxbullet = self.lineedit_with_label("最大弹药",weaponmaxbulletEdit)

        weaponyrateEdit = QLineEdit()
        weaponyrate  = self.lineedit_with_label("武器Y系数", weaponyrateEdit)

        weaponxrateEdit = QLineEdit()
        weaponxrate  = self.lineedit_with_label("武器X系数", weaponxrateEdit)

        weaponbaseEdit = QLineEdit()
        weaponbase  = self.lineedit_with_label("基础下压",  weaponbaseEdit)

        weaponsingleEdit = QCheckBox()
        weaponsingle  = self.lineedit_with_label("连点",  weaponsingleEdit)


        weapondata = QTextEdit()
        weapon_data_result = QTextEdit()



        buttonbox = QGroupBox()
        buttonboxgrid = QGridLayout()
        delButton = QPushButton("删除")
        saveButton = QPushButton("保存")
        buttonboxgrid.addWidget(delButton,0,0)
        buttonboxgrid.addWidget(saveButton,0,1)
        buttonbox.setLayout(buttonboxgrid)


        grid.addWidget(weapons,0,0)


        weaponconfiggroup = QGroupBox()
        weaponconfiggrid = QGridLayout()
        weaponconfiggrid.addWidget(weaponspeed,1,0)
        weaponconfiggrid.addWidget(weaponyrate,1,1)
        weaponconfiggrid.addWidget(weaponxrate,1,2)
        weaponconfiggrid.addWidget(weaponbase,1,3)
        weaponconfiggrid.addWidget(weaponmaxbullet,1,4)
        weaponconfiggrid.addWidget(weaponsingle,1,5)

        weaponconfiggroup.setLayout(weaponconfiggrid)

        datagroup = QGroupBox()
        datagrid = QGridLayout()
        datagrid.addWidget(weapondata,0,0)
        datagrid.addWidget(weapon_data_result,0,1)
        datagroup.setLayout(datagrid)


        grid.addWidget(weaponconfiggroup,1,0)
        grid.addWidget(datagroup,2,0)
        grid.addWidget(buttonbox,3,0)
        group.setLayout(grid)

        self.grid.addWidget(group,1,0)

        self.weapondataprofiles = weapondataprofiles
        self.loading = loading
        self.debug = debug
        self.dq = dq
        self.dqrate = dqrate
        self.weapons = weapons
        self.speed = weaponspeedEdit
        self.yrate = weaponyrateEdit
        self.xrate = weaponxrateEdit
        self.base = weaponbaseEdit
        self.maxbullet = weaponmaxbulletEdit
        self.single = weaponsingleEdit

        self.weapondata = weapondata
        self.weapon_data_result = weapon_data_result
        self.delButton = delButton
        self.saveButton = saveButton

#====================================================================