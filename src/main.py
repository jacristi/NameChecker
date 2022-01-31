import sys
import traceback

import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QErrorMessage

import src.utils.constants as c
from src.UI.ui_namechecker import Ui_NameEvaluator
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

    def __init__(self, no_style=True):
        super(UIMain, self).__init__()
        self.ui = Ui_NameEvaluator()
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
        self.ui.btn_filter_avoids.clicked.connect(self.filter_avoids_table)
        self.ui.btn_clear_avoid_filter.clicked.connect(self.clear_avoids_table_filter)

        self.ui.checkbox_all.stateChanged.connect(self.check_uncheck_all)

        self.set_avoids_table_data()

        self.set_project_competitor_avoids_from_file()
        self.save_project_competitor_avoids_start()

        self.clickable(self.ui.group_check_uncheck_all).connect(self.click_group_check_uncheck_all)
        self.clickable(self.ui.group_inn).connect(self.click_group_inn)
        self.clickable(self.ui.group_market_research).connect(self.click_group_market_research)
        self.clickable(self.ui.group_linguistics).connect(self.click_group_linguistics)
        self.clickable(self.ui.group_competitor).connect(self.click_group_competitor)
        self.clickable(self.ui.group_project_avoids).connect(self.click_group_project_avoids)

        self.ui.text_names.setTabChangesFocus(True)
        self.ui.text_project_avoids.setTabChangesFocus(True)
        self.ui.text_competitor.setTabChangesFocus(True)

        if no_style is True:
            self.ui.MainWindow.setStyleSheet("")
            self.ui.MainTab.setStyleSheet("")

    @error_handler
    def set_avoids_table_data(self, upd_df=None):
        if upd_df is None:
            self.avoids_df = get_avoids_from_file(self.logger, self.config)
        else:
            self.avoids_df = pd.concat([self.avoids_df, upd_df])

        if self.avoids_df is None:
            raise UserError("Master avoids file could not be found/read\nPlease check the path defined in NameEvaluator_conf.ini")

        self.avoids_df.drop_duplicates(subset=[c.VALUE_FIELD, c.TYPE_FIELD, c.CATEGORY_FIELD], inplace=True)

        self.ui.qtable_avoids.setModel(QTPandasModel(self.avoids_df))

        header = self.ui.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.ui.qtable_avoids.setSortingEnabled(True)
        self.ui.qtable_avoids.sortByColumn(0, QtCore.Qt.AscendingOrder)


    @error_handler
    def set_filtered_avoids_table_data(self, filtered_df):
        self.ui.qtable_avoids.setModel(QTPandasModel(filtered_df))

        header = self.ui.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.ui.qtable_avoids.setSortingEnabled(True)
        self.ui.qtable_avoids.sortByColumn(0, QtCore.Qt.AscendingOrder)


    @error_handler
    def filter_avoids_table(self, val):
        """ """
        temp_table = self.avoids_df.copy()
        filter_text = self.ui.lineedit_filter_avoids.text()

        if self.config.get('FILTER_AVOIDS_ON_VALUE_ONLY', '0') == '1':
            temp_table = temp_table[temp_table[c.VALUE_FIELD].str.contains(filter_text)]
        else:
            temp_table = temp_table[
                (temp_table[c.VALUE_FIELD].str.contains(filter_text)) |
                (temp_table[c.TYPE_FIELD].str.contains(filter_text)) |
                (temp_table[c.DESCRIPTION_FIELD].str.contains(filter_text)) |
                (temp_table[c.CATEGORY_FIELD].str.contains(filter_text))
                ]

        self.set_filtered_avoids_table_data(temp_table)



    @error_handler
    def clear_avoids_table_filter(self, val):
        """ """
        self.set_avoids_table_data()


    @error_handler
    def set_results_table_data(self):
        if self.results_df is None:
            return

        if self.results_df.empty:
            self.results_df = pd.DataFrame.from_dict({'Results': ['No Conflicts!']})

        self.ui.qtable_results.reset()
        self.ui.qtable_results.setModel(QTPandasModel(self.results_df))

        rows = self.ui.qtable_results.verticalHeader()
        rows.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        header = self.ui.qtable_results.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)



    @error_handler
    def get_and_strip_names(self):
        """ """
        names_list_text = self.ui.text_names.toPlainText()
        self.names_list = sorted(list({i.strip() for i in names_list_text.split('\n') if i.strip()}))


    @error_handler
    def check_names(self, val):
        """ """
        self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        self.get_and_strip_names()
        self.read_stem_ignores()
        self.read_checkboxes()
        self.ui.qtable_results.reset()

        if self.names_list == []:
            raise UserError("No names entered!")

        if all([i is False for i in self.checked_categories.values()]):
            raise UserError("No avoids checked!")

        self.results_df = check_names_for_avoids(
            self.names_list,
            self.ignore_list,
            self.avoids_df,
            self.checked_categories,
            )
        self.set_results_table_data()
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))


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
    def save_project_competitor_avoids_start(self):
        """ """
        project_avoids_text = self.ui.text_project_avoids.toPlainText()
        competitor_avoids_text = self.ui.text_competitor.toPlainText()

        if project_avoids_text == '' and competitor_avoids_text == '':
            return

        save_project_competitor_to_file(self.config, project_avoids_text, competitor_avoids_text)

        addtl_avoids_df = parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text)

        self.set_avoids_table_data(addtl_avoids_df)


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

    def clickable(self, widget):

        class Filter(QtCore.QObject):

            clicked = QtCore.pyqtSignal()

            def eventFilter(self, obj, event):

                if obj == widget:
                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            return True

                return False

        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked

    def click_group_check_uncheck_all(self):
        val = not self.ui.checkbox_all.isChecked()
        self.check_uncheck_all(val)
        self.ui.checkbox_all.setChecked(val)

    def click_group_inn(self):
        self.ui.checkbox_inn.setChecked(not self.ui.checkbox_inn.isChecked())

    def click_group_market_research(self):
        self.ui.checkbox_market_research.setChecked(not self.ui.checkbox_market_research.isChecked())

    def click_group_linguistics(self):
        self.ui.checkbox_linguistic.setChecked(not self.ui.checkbox_linguistic.isChecked())

    def click_group_competitor(self):
        self.ui.checkbox_competitor.setChecked(not self.ui.checkbox_competitor.isChecked())

    def click_group_project_avoids(self):
        self.ui.checkbox_project.setChecked(not self.ui.checkbox_project.isChecked())

    def closeEvent(self, event):
        choice = QMessageBox.question(self, "Quit", "Leave?", QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes :
            QMainWindow.closeEvent(self, event)
        else :
            event.ignore()

    def close_app(self):
        self.close()


@error_handler
def run():
    app = QApplication(sys.argv)

    no_style = False

    NameChecker = UIMain(no_style)
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
### XXX save project/competitor avoids to file to persist across sessions
### XXX check names against each string according to position type (save as csv or txt?)
            # XXX prefix `startswith`
            # XXX infix `in` [1:-1]
            # XXX suffix `endswith`
            # XXX anywhere `in`
            # XXX string comparison - consult original logic
### XXX show hits in results table
### XXX show hit string for combo/string compare {{potentially highlight string in hit}}
### XXX results sortable
### XXX Auto-import pre-saved avoids



### TODO avoids table searchable/filterable
### TODO update all item tooltips
### TODO keyboard short-cuts (ctrl+enter when text_names is focus will check names; tab in project avoids text will move to competitor text)
