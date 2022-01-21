import sys

from pandas import read_csv
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QVariant, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow

from src.UI import ui_namechecker
from src.utils.data_models import QTPandasModel
from src.utils.common_utils import get_config, Logger
from src.utils.get_avoids_data import get_avoids_from_file

class UIMain(ui_namechecker.Ui_NameChecker):
    """ """
    names_list = []
    names_list_stripped = []
    avoids_tbl = None
    results_tbl = None


    def __init__(self):
        super(UIMain, self).__init__()
        from src.utils.common_utils import Logger

        self.config = get_config()
        self.logger = Logger('App Logger').setup(self.config)



    def set_table_data(self):
        df = get_avoids_from_file(self.logger, self.config)
        # self.qtable_results.setModel(QTPandasModel(df))
        self.qtable_avoids.setModel(QTPandasModel(df))

        header = self.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def get_avoids_data(self):
        print("get avoids")
        return read_csv('avoids.csv')#self.get_avoids_data()


def run():
    app = QApplication(sys.argv)

    MainWindow = QMainWindow()

    ui = UIMain()
    ui.setupUi(MainWindow)

    ui.set_table_data()

    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


### TODO avoids table sortable, searchable?
### TODO get checked avoid types
### TODO read in names, strip and save in mem
### TODO re-output names according to case button click (upper, title, lower)
### TODO save project avoids to in mem avoids df and show in avoids table
### TODO save project avoids to file rto persist across sessions
### TODO check names against each string according to position type
            # prefix `startswith`
            # infix `in` [1:-1]
            # suffix `endswith`
            # anywhere `in`
            # string comparison - consult original logic
### TODO show hits in results table
