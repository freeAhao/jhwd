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

        loading = QLineEdit()
        loadinggroup = self.lineedit_with_label("cpu负载",loading)

        sensitivity = QLineEdit("1")
        sensitivitygroup = self.lineedit_with_label("灵敏度系数",sensitivity)

        debug = QCheckBox("debug弹道调试")

        grid.addWidget(weapondataprofilesgroup,0,0,1,2)
        grid.addWidget(loadinggroup,1,0,1,2)
        grid.addWidget(sensitivitygroup,2,0,1,2)
        grid.addWidget(debug,3,0,1,2)
        group.setLayout(grid)
        self.grid.addWidget(group,0,0)

        group = QGroupBox("武器")
        grid = QGridLayout()

        weapons = QComboBox()

        weaponspeedEdit = QLineEdit()
        weaponspeed = self.lineedit_with_label("射速",weaponspeedEdit)

        weaponmaxbulletEdit = QLineEdit()
        weaponmaxbullet = self.lineedit_with_label("最大弹药",weaponmaxbulletEdit)

        weaponrateEdit = QLineEdit()
        weaponrate  = self.lineedit_with_label("武器Y系数", weaponrateEdit)

        weaponbaseEdit = QLineEdit()
        weaponbase  = self.lineedit_with_label("基础下压",  weaponbaseEdit)

        weaponsingleEdit = QCheckBox()
        weaponsingle  = self.lineedit_with_label("连点",  weaponsingleEdit)

        weaponautoshiftEdit = QCheckBox()
        weaponautoshift  = self.lineedit_with_label("自动屏息",  weaponautoshiftEdit)

        weapondata = QTextEdit()
        weapon_data_result = QTextEdit()

        weaponposes = QComboBox()
        weaponposerate = QLineEdit()

        scopes = QComboBox()
        scoperate = QLineEdit()

        attachment2 = QComboBox()
        attachment2rate = QLineEdit()

        attachment3 = QComboBox()
        attachment3rate = QLineEdit()

        apply_rate_to_all_weapon = QPushButton("应用到所有武器")

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
        weaponconfiggrid.addWidget(weaponrate,1,1)
        weaponconfiggrid.addWidget(weaponbase,1,2)
        weaponconfiggrid.addWidget(weaponmaxbullet,1,3)
        weaponconfiggrid.addWidget(weaponsingle,1,4)
        weaponconfiggrid.addWidget(weaponautoshift,1,5)

        weaponconfiggrid.addWidget(weaponposes,2,0)
        weaponconfiggrid.addWidget(weaponposerate,2,1)
        weaponconfiggrid.addWidget(scopes,2,2)
        weaponconfiggrid.addWidget(scoperate,2,3)
        weaponconfiggrid.addWidget(attachment2,3,0)
        weaponconfiggrid.addWidget(attachment2rate,3,1)
        weaponconfiggrid.addWidget(attachment3,3,2)
        weaponconfiggrid.addWidget(attachment3rate,3,3)

        weaponconfiggrid.addWidget(apply_rate_to_all_weapon,2,4,2,1)

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
        self.sensitivityrate = sensitivity
        self.debug = debug
        self.weapons = weapons
        self.speed = weaponspeedEdit
        self.rate = weaponrateEdit
        self.base = weaponbaseEdit
        self.maxbullet = weaponmaxbulletEdit
        self.single = weaponsingleEdit
        self.autoshift = weaponautoshiftEdit
        self.poses = weaponposes
        self.poserate = weaponposerate
        self.scopes = scopes
        self.scoperate = scoperate
        self.a2 = attachment2
        self.a2rate = attachment2rate
        self.a3 = attachment3
        self.a3rate = attachment3rate
        self.weapondata = weapondata
        self.weapon_data_result = weapon_data_result
        self.delButton = delButton
        self.saveButton = saveButton
        self.apply_rate_to_all_weapon = apply_rate_to_all_weapon

#====================================================================