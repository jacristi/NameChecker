
from PyQt5.QtCore import Qt, QAbstractTableModel



class QTPandasModel(QAbstractTableModel):
    """ """

    def __init__(self, data, parent=None):
        """ """
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._columns = data.columns

    def rowCount(self, parent=None):
        """ """
        return self._data.shape[0]

    def columnCount(self, parent=None):
        """ """
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """ """
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
        return None

    def headerData(self, col, orientation, role):
        """ """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            cur_val = self._data.iloc[index.row(),index.column()]
            print(f'Changing {cur_val} to {value} at row: {index.row()}, column: {index.column()}')
            self._data.iloc[index.row(),index.column()] = value
            return True

    def insertRow(self, row, parent):
        return super().insertRow(row, parent=parent)

    def sort(self, Ncol, order):
        """ """
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(
            self._columns[Ncol],
            ascending=order==Qt.AscendingOrder
            )
        self.layoutChanged.emit()



class UserError(Exception):
    """ """