import sys
import traceback

import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QErrorMessage

import src.utils.constants as c
from src.UI import ui_namechecker
from src.utils.data_models import QTPandasModel, UserError
from src.utils.check_names import check_names_for_avoids
from src.utils.common_utils import Logger, error_handler
from src.utils.get_avoids_data import get_avoids_from_file, parse_project_competitor_avoids, save_project_competitor_to_file, read_project_competitor_from_file


class UIMain(QMainWindow):
    """ """
    _names_list = []
    ignore_list = []
    avoids_df = None
    results_df = None
    checked_categories = {}

    def __init__(self):
        super(UIMain, self).__init__()
        self.ui = ui_namechecker.Ui_NameEvaluator()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('app.ico'))

        self.config = c.get_config()
        self.logger = Logger('App Logger')
        self.logger.setup(self.config)

        self.err_dialogue = QErrorMessage(self)
        self.err_dialogue.setWindowModality(QtCore.Qt.WindowModal)

        self.ui.btn_check_names.clicked.connect(self.check_names)
        self.ui.btn_upper_case.clicked.connect(self.set_names_uppercase)
        self.ui.btn_title_case.clicked.connect(self.set_names_titlecase)
        self.ui.btn_lower_case.clicked.connect(self.set_names_lowercase)
        self.ui.btn_save_avoids.clicked.connect(self.save_project_competitor_avoids)
        self.ui.btn_reload_avoids.clicked.connect(self.reload_avoids)
        self.ui.btn_exit.clicked.connect(self.close_app)

        self.ui.checkbox_all.stateChanged.connect(self.check_uncheck_all)

        self.set_avoids_table_data()

        self.set_project_competitor_avoids_from_file()

    @error_handler
    def set_avoids_table_data(self, upd_df=None):
        if upd_df is None:
            self.avoids_df = get_avoids_from_file(self.logger, self.config)
        else:
            self.avoids_df = pd.concat([self.avoids_df, upd_df])

        self.avoids_df.drop_duplicates(subset=['value', 'type', 'category'], inplace=True)

        self.ui.qtable_avoids.setModel(QTPandasModel(self.avoids_df))

        header = self.ui.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.ui.qtable_avoids.setSortingEnabled(True)

    @error_handler
    def set_results_table_data(self):
        if self.results_df is None:
            return

        if self.results_df.empty:
            self.results_df = pd.DataFrame.from_dict({'Results': ['No Conflicts!']})

        self.ui.qtable_results.setModel(QTPandasModel(self.results_df))

        rows = self.ui.qtable_results.verticalHeader()
        rows.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header = self.ui.qtable_results.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    @error_handler
    def get_and_strip_names(self):
        """ """
        names_list_text = self.ui.text_names.toPlainText()
        self.names_list = names_list_text.split('\n')


    @error_handler
    def check_names(self, val):
        """ """
        self.get_and_strip_names()
        self.read_stem_ignores()
        self.read_checkboxes()

        if self.names_list == ['']:
            raise UserError("No names entered!")

        self.results_df = check_names_for_avoids(
            self.names_list,
            self.ignore_list,
            self.avoids_df,
            self.checked_categories,
            )
        self.set_results_table_data()


    @error_handler
    def read_stem_ignores(self):
        """ """
        ignore_list_text = self.ui.lineedit_ignore.text()
        self.ignore_list = [i.strip() for i in ignore_list_text.split(',')]


    @error_handler
    def check_uncheck_all(self, val):
        """ """
        self.ui.checkbox_market_research.setChecked(val)
        self.ui.checkbox_inn.setChecked(val)
        self.ui.checkbox_project.setChecked(val)
        self.ui.checkbox_linguistic.setChecked(val)
        self.ui.checkbox_competitor.setChecked(val)


    @error_handler
    def read_checkboxes(self):
        """ """
        self.checked_categories = {
            c.MARKET_RESEARCH:  self.ui.checkbox_market_research.isChecked(),
            c.INN:              self.ui.checkbox_inn.isChecked(),
            c.PROJECT:          self.ui.checkbox_project.isChecked(),
            c.LINGUISTIC:       self.ui.checkbox_linguistic.isChecked(),
            c.COMPETITOR:       self.ui.checkbox_competitor.isChecked(),
        }


    @property
    def names_list(self):
        return self._names_list

    @names_list.setter
    def names_list(self, value):
        self._names_list = value
        self.ui.text_names.setPlainText('\n'.join(self.names_list))

    @error_handler
    def set_names_uppercase(self, val):
        """ """
        self.get_and_strip_names()
        self.names_list = [i.upper() for i in self.names_list]


    @error_handler
    def set_names_titlecase(self, val):
        """ """
        self.get_and_strip_names()
        self.names_list = [i.title() for i in self.names_list]


    @error_handler
    def set_names_lowercase(self, val):
        """ """
        self.get_and_strip_names()
        self.names_list = [i.lower() for i in self.names_list]


    @error_handler
    def reload_avoids(self, val):
        """ """
        self.set_avoids_table_data()


    @error_handler
    def save_project_competitor_avoids(self, val):
        """ """
        project_avoids_text = self.ui.text_project_avoids.toPlainText()
        competitor_avoids_text = self.ui.text_competitor.toPlainText()

        if project_avoids_text == '' and competitor_avoids_text == '':
            raise UserError("No avoids to save!")

        save_project_competitor_to_file(self.config, project_avoids_text, competitor_avoids_text)

        addtl_avoids_df = parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text)

        self.set_avoids_table_data(addtl_avoids_df)

    @error_handler
    def set_project_competitor_avoids_from_file(self):
        """ """
        proj_text, comp_text = read_project_competitor_from_file(self.config)
        self.ui.text_project_avoids.setPlainText(proj_text)
        self.ui.text_competitor.setPlainText(comp_text)

    def raise_error(self, err):
        """ """
        self.err_dialogue.showMessage(str(err))


    def raise_critical_error(self, err):
        """ """
        QMessageBox.critical(self, 'An unexpected error occurred', traceback.format_exc())

    def close_app(self):
        choice = QMessageBox.question(self, "Quit", "Leave?", QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes :
            sys.exit()
        else :
            pass


@error_handler
def run():
    app = QApplication(sys.argv)

    NameChecker = UIMain()
    NameChecker.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


### XXX stub all top level functions
### XXX bind all buttons to dummy functions
### XXX get checked avoid types checkboxes
### XXX read in names, strip and save in mem
### XXX re-output names according to case button click (upper, title, lower)
### XXX save project avoids to in mem avoids df and show in avoids table
### TODO save project/competitor avoids to file to persist across sessions
### TODO check names against each string according to position type (save as csv or txt?)
            # XXX prefix `startswith`
            # XXX infix `in` [1:-1]
            # XXX suffix `endswith`
            # XXX anywhere `in`
            # TODO string comparison - consult original logic
### XXX show hits in results table
### Show results with avoid string highlighted in name?
### XXX avoids table sortable
### XXX avoids table searchable
### TODO incorporate LBB log and style guide
### TODO update all item tooltips
### TODO keyboard short-cuts