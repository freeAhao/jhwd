import os
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QCheckBox, QGroupBox, QComboBox, QTableWidget,QAbstractItemView,QPushButton, QTableWidgetItem,QFileDialog,QLineEdit,QMessageBox,QTableView,QDialog,QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, pyqtSignal
from time import time

from model.MacroFunction import MacroFunction

class QMacroConfigWidget(QWidget):

    grid = QGridLayout()

    def __init__(self) -> None:
        super().__init__()

        self.setLayout(self.grid)
        self.aimModeUI()
        # self.otherUI()
        self.keybindUI()

#====================================================================
    def toggle_aimMode_display(self, show: bool):
        if show:
            self.aim.show()
            self.adslabel.show()
        else:
            self.aim.hide()
            self.adslabel.hide()
    
    def save_file_dialog(self) -> str:
        path = os.path.expanduser("~/Desktop/")
        fname = QFileDialog.getSaveFileName(self,caption='保存文件',directory=path,filter="*.lua ; *.txt")
        if not (fname and fname[0]):
            return None
        save_path = fname[0]
        return save_path

    def aimModeUI(self):
        group = QGroupBox("模式")
        grid = QGridLayout()

        driver_soft_label = QLabel("驱动软件")
        driversoft = QComboBox()
        driver_script_download_btn = QPushButton("下载脚本")

        modeslabel = QLabel("开镜模式")
        modes = QComboBox()


        adslabel = QLabel("瞄准/肩射键")
        aim = QComboBox()


        grid.addWidget(driver_soft_label,0,0)
        grid.addWidget(driversoft,0,1)
        grid.addWidget(driver_script_download_btn,0,2)
        grid.addWidget(modeslabel,1,0)
        grid.addWidget(modes,1,1,1,2)
        grid.addWidget(adslabel,2,0)
        grid.addWidget(aim,2,1,1,2)

        group.setLayout(grid)
        self.grid.addWidget(group,0,0)

        self.driver_script_download_btn = driver_script_download_btn
        self.driversoft = driversoft
        self.modes = modes
        self.aim = aim
        self.adslabel = adslabel

#====================================================================

    def otherUI(self):
        group = QGroupBox("其它设置")
        grid = QGridLayout()

        loading = QComboBox()
        for i in ["10","20","30","40","50"]:
            loading.addItem(i)



        group.setLayout(grid)
        self.grid.addWidget(group,1,0)

        self.loading = loading
        
#====================================================================

    def add_modifier_key(self, modifier:str,index):
            checkbox = QCheckBox(modifier)
            self.modifiergrid.addWidget(checkbox,0,index)
            self.modifier_checkboxs.append(checkbox)

    def keybindUI(self):
        group = QGroupBox("按键绑定")
        grid = QGridLayout()

        selectBtn = QComboBox()
        selectFunc = QComboBox()

        addBtn = QPushButton("+")
        minusBtn = QPushButton("-")
        editBtn = QPushButton("脚本编辑")

        table = QTableView(self)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        modifierGroup = QGroupBox("修饰键")
        modifiergrid = QGridLayout()
        modifier_checkboxs = []


        modifierGroup.setLayout(modifiergrid)


        grid.addWidget(modifierGroup,0,0)
        grid.addWidget(selectBtn,0,1)
        grid.addWidget(selectFunc,0,2)
        grid.addWidget(table,1,0,1,3)
        grid.addWidget(minusBtn,2,0,)
        grid.addWidget(addBtn,2,1,)
        grid.addWidget(editBtn,2,2)

        group.setLayout(grid)
        self.grid.addWidget(group,2,0)

        self.modifiergrid = modifiergrid
        self.modifier_checkboxs = modifier_checkboxs
        self.selectBtn = selectBtn
        self.selectFunc = selectFunc
        self.addBtn = addBtn
        self.minusBtn = minusBtn
        self.editBtn = editBtn
        self.table = table

#====================================================================

class MacroEditDialog(QDialog):

    save = pyqtSignal(MacroFunction,str,str,QDialog)

    def __init__(self,funcs) -> None:

        super().__init__()

        self.funcs = funcs

        grid = QGridLayout()

        selectFunc = QComboBox()


        editOpen = QTextEdit(self)

        editClose = QTextEdit(self)

        saveBtn = QPushButton("保存")


        grid.addWidget(selectFunc,0,0)
        grid.addWidget(QLabel("按下快捷键"),1,0)
        grid.addWidget(editOpen,2,0,)
        grid.addWidget(QLabel("松开快捷键"),3,0)
        grid.addWidget(editClose,4,0)
        grid.addWidget(saveBtn,5,0)

        self.setWindowTitle("编辑函数")
        self.setLayout(grid)

        self.selectFunc = selectFunc
        self.editOpen = editOpen
        self.editClose = editClose
        self.saveBtn = saveBtn

        saveBtn.clicked.connect(lambda:self.save.emit(self.selectFunc.currentData(), self.editOpen.toPlainText(), self.editClose.toPlainText(), self))
        selectFunc.currentIndexChanged.connect(self.select_func)
        for funcname in funcs:
            selectFunc.addItem(funcname + "-" + funcs[funcname].description, userData=funcs[funcname])

    def select_func(self):
        func = self.selectFunc.currentData()
        self.editOpen.setText(func.openContent)
        self.editClose.setText(func.closeContent)