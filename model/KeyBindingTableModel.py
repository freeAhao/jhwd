
from PyQt6.QtCore import QAbstractTableModel, QVariant, Qt

from model.KeyBinding import KeyBinding
 
 
class KeyBindingTableModel(QAbstractTableModel):

    def __init__(self, parent, data:list[KeyBinding], header: list[str]) -> None:
        super().__init__(parent)

        self.data = data
        self.header = header
 
    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data)+1
 
    def columnCount(self, parent=None, *args, **kwargs):
        return 3
 
    def get_data(self,row):
        if row + 1 >= self.rowCount():
            return None
        return self.data[row]
    
    def set_datas(self,data):
        self.data = data
        self.layoutChanged.emit()

    def set_data(self,row, data):
        if row +1 >= self.rowCount():
            self.data.append(data)
        else:
            self.data[row] = data
        self.layoutChanged.emit()

    def append_data(self,x):
        self.data.append(x)
        self.layoutChanged.emit()
 
    def remove_row(self,row):
        if row+1 >= self.rowCount():
            return
        self.data.pop(row)
        self.layoutChanged.emit()
    
    def sort_data(self):
        self.data = sorted(self.data, key=lambda keybingding:len(keybingding.modifiers),reverse=True)
        self.layoutChanged.emit()

    # 返回一个项的任意角色的值，这个项被指定为QModelIndex
    def data(self, QModelIndex, role=None):

        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        # if role == Qt.TextAlignmentRole:
        #     return int(Qt.AlignRight | Qt.AlignVCenter)
        # elif role == Qt.DisplayRole:
        #     row = QModelIndex.row()
        #     column = QModelIndex.column()
        #     return self.currencyMap.get('data')[row][column]
        # # print("查数据")
        # row = QModelIndex.row()
        # # print('role:',role)
        # if role is None:
        #     return self.currencyMap.get('data')[row]
        elif role != Qt.ItemDataRole.DisplayRole:
            return QVariant()

        if QModelIndex.row()+1 >= self.rowCount():
            return QVariant()

        if self.data[QModelIndex.row()] == None:
            return QVariant()

        if QModelIndex.column() == 0:
            return QVariant(",".join(self.data[QModelIndex.row()].modifiers))
        if QModelIndex.column() == 1:
            return QVariant(self.data[QModelIndex.row()].mouseBtn)
        if QModelIndex.column() == 2:
            return QVariant(self.data[QModelIndex.row()].func.description)

 
 
    def headerData(self, section, Qt_Orientation, role=None):
        if Qt_Orientation == Qt.Orientation.Horizontal and role==Qt.ItemDataRole.DisplayRole:
            return QVariant(self.header[section])
        return QVariant()