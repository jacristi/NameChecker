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

    busy_cursor = QtCore.Qt.BusyCursor
    default_cursor = QtCore.Qt.ArrowCursor

    def __init__(self, no_style=True):
        super(UIMain, self).__init__()

        ### Set up UI
        self.ui = Ui_NameEvaluator()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('app.ico'))

        ### Set up config dict + logger
        self.config = c.get_config()
        self.logger = Logger('App Logger')
        self.logger.setup(self.config)

        ### Set up error dialogue widget
        self.err_dialogue = QErrorMessage(self)
        self.err_dialogue.setWindowModality(QtCore.Qt.WindowModal)

        ### Set button onClik actions
        self.ui.btn_check_names.clicked.connect(self.check_names)
        self.ui.btn_upper_case.clicked.connect(self.set_names_uppercase)
        self.ui.btn_title_case.clicked.connect(self.set_names_titlecase)
        self.ui.btn_lower_case.clicked.connect(self.set_names_lowercase)
        self.ui.btn_save_avoids.clicked.connect(self.save_project_competitor_avoids)
        self.ui.btn_clear_avoids.clicked.connect(self.clear_avoids)
        self.ui.btn_reload_avoids.clicked.connect(self.reload_avoids)
        self.ui.btn_exit.clicked.connect(self.close_app)
        self.ui.lineedit_filter_avoids.textChanged.connect(self.filter_avoids_table)

        ### Set check/uncheck all box to do exactly that
        self.ui.checkbox_all.stateChanged.connect(self.check_uncheck_all)

        ### Set initial avoids data, loads from 'master' file
        self.set_avoids_table_data()

        ### Set up avoids entered/saved from last session
        self.set_project_competitor_avoids_from_file()
        self.save_project_competitor_avoids_start()

        ### Assign a clickable component to these objects
        # Allows the user to still check the box even if not directly on the text
        self.clickable(self.ui.group_check_uncheck_all).connect(self.click_group_check_uncheck_all)
        self.clickable(self.ui.group_inn).connect(self.click_group_inn)
        self.clickable(self.ui.group_market_research).connect(self.click_group_market_research)
        self.clickable(self.ui.group_linguistics).connect(self.click_group_linguistics)
        self.clickable(self.ui.group_competitor).connect(self.click_group_competitor)
        self.clickable(self.ui.group_project_avoids).connect(self.click_group_project_avoids)

        ### Text boxes change focus on TAB (rather than adding tab whitespace)
        self.ui.text_names.setTabChangesFocus(True)
        self.ui.text_project_avoids.setTabChangesFocus(True)
        self.ui.text_competitor.setTabChangesFocus(True)

        ### Easily turn off styling
        if no_style is True:
            self.ui.MainWindow.setStyleSheet("")
            self.ui.MainTab.setStyleSheet("")

    @error_handler
    def set_avoids_table_data(self, upd_df=None):
        """ Set qtable_avoids to have the expected data.
            upd_df is expected when user saves project and/or competitor avoids.
        """
        if upd_df is None:
            self.avoids_df = get_avoids_from_file(self.logger, self.config)
        else:
            self.avoids_df = pd.concat([self.avoids_df, upd_df])

        if self.avoids_df is None:
            raise UserError("Master avoids file could not be found/read\nPlease check the path defined in NameEvaluator_conf.ini")

        self.avoids_df.drop_duplicates(subset=[c.VALUE_FIELD, c.TYPE_FIELD, c.CATEGORY_FIELD], inplace=True)

        ### Qtable uses custom pandas model
        self.ui.qtable_avoids.setModel(QTPandasModel(self.avoids_df))

        ### Stretch headers to fit
        header = self.ui.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        ### Sorting enabled
        self.ui.qtable_avoids.setSortingEnabled(True)
        self.ui.qtable_avoids.sortByColumn(0, QtCore.Qt.AscendingOrder)

    @error_handler
    def set_filtered_avoids_table_data(self, filtered_df):
        """ Set qtable_avoids to filtered data. """

        ### Qtable uses custom pandas model
        self.ui.qtable_avoids.setModel(QTPandasModel(filtered_df))

        ### Stretch headers to fit
        header = self.ui.qtable_avoids.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        ### Sorting enabled
        self.ui.qtable_avoids.setSortingEnabled(True)
        self.ui.qtable_avoids.sortByColumn(0, QtCore.Qt.AscendingOrder)

    @error_handler
    def filter_avoids_table(self, val):
        """ Filter current avoids_df using string values in lineedit.
            This is called on lineedit_filter_avoids value change
        """

        filtered_table = self.avoids_df.copy()
        filter_text = self.ui.lineedit_filter_avoids.text().strip()

        ### If no value, set back to full df
        if filter_text == '':
            self.set_avoids_table_data()

        # Can configure whether the filter works only on value or on all fields
        if self.config.get('FILTER_AVOIDS_ON_VALUE_ONLY', '0') == '1':
            filtered_table = filtered_table[filtered_table[c.VALUE_FIELD].str.contains(filter_text)]
        else:
            filtered_table = filtered_table[
                (filtered_table[c.VALUE_FIELD].str.contains(filter_text, case=False)) |
                (filtered_table[c.TYPE_FIELD].str.contains(filter_text, case=False)) |
                (filtered_table[c.DESCRIPTION_FIELD].str.contains(filter_text, case=False)) |
                (filtered_table[c.CATEGORY_FIELD].str.contains(filter_text, case=False))
                ]

        ### Set filtered table
        self.set_filtered_avoids_table_data(filtered_table)

    @error_handler
    def set_results_table_data(self):
        """ Set qtable_results to have the expected data. """

        ### Don't show if not created yet
        if self.results_df is None:
            return

        ### Show no conflicts if no conflicts found
        if self.results_df.empty:
            self.results_df = pd.DataFrame.from_dict({'Results': ['No Conflicts!']})

        ### Qtable uses custom pandas model
        self.ui.qtable_results.setModel(QTPandasModel(self.results_df))

        ### Stretch headers to fit
        header = self.ui.qtable_results.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        ### Set rows to fit to content
        rows = self.ui.qtable_results.verticalHeader()
        rows.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    @error_handler
    def get_and_strip_names(self):
        """ Get names entered in text_names text area, split on new line and strip of whitespace. """

        names_list_text = self.ui.text_names.toPlainText()
        self.names_list = sorted(list({i.strip() for i in names_list_text.split('\n') if i.strip()}))

    @error_handler
    def check_names(self, val):
        """ Take entered names and check against full list of all avoids. """

        ### Show process is busy with cursor change
        self.setCursor(QtGui.QCursor(self.busy_cursor))

        ### Get al names, get any ignore strings entered, get all checked categories
        self.get_and_strip_names()
        self.read_stem_ignores()
        self.read_checkboxes()
        self.ui.qtable_results.reset()

        ### Raise user error if no names or no checked avodis
        if self.names_list == []:
            raise UserError("No names entered!")

        if all([i is False for i in self.checked_categories.values()]):
            raise UserError("No avoids checked!")

        ### Run main avoids check function
        self.results_df = check_names_for_avoids(
            self.names_list,
            self.ignore_list,
            self.avoids_df,
            self.checked_categories,
            )

        ### Set new results data table
        self.set_results_table_data()

        ### Reset cursor when process is complete
        self.setCursor(QtGui.QCursor(self.default_cursor))

    @error_handler
    def read_stem_ignores(self):
        """ Get any/all entered stem ignores. These can be commaseparated"""

        ignore_list_text = self.ui.lineedit_ignore.text()
        self.ignore_list = [i.strip() for i in ignore_list_text.split(',')]

    @error_handler
    def check_uncheck_all(self, val):
        """ Check or uncheck all check boxes. """

        self.ui.checkbox_market_research.setChecked(val)
        self.ui.checkbox_inn.setChecked(val)
        self.ui.checkbox_project.setChecked(val)
        self.ui.checkbox_linguistic.setChecked(val)
        self.ui.checkbox_competitor.setChecked(val)

    @error_handler
    def read_checkboxes(self):
        """ Read checkboxes and store true/false in dictionary by category name. """

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
        """ Set all names to UPPER case. """

        self.get_and_strip_names()
        self.names_list = [i.upper() for i in self.names_list]

    @error_handler
    def set_names_titlecase(self, val):
        """ Set all names to Title case. """

        self.get_and_strip_names()
        self.names_list = [i.title() for i in self.names_list]

    @error_handler
    def set_names_lowercase(self, val):
        """ Set all names to lower case. """
        self.get_and_strip_names()
        self.names_list = [i.lower() for i in self.names_list]

    @error_handler
    def clear_avoids(self, val):
        """ """
        choice = QMessageBox.question(
            self, "Clear and reset all avoids", "Clear and reset all avoids?",
            QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes :
            self.ui.text_project_avoids.clear()
            self.ui.text_competitor.clear()
            save_project_competitor_to_file(self.config, '', '')
            self.reload_avoids(True)


    @error_handler
    def reload_avoids(self, val):
        """ Reset avoids table to only contain avoids from master file. """

        self.set_avoids_table_data()

    @error_handler
    def save_project_competitor_avoids_start(self):
        """ Parse and save user-defined project/competitor avoids from previous session. """

        project_avoids_text = self.ui.text_project_avoids.toPlainText()
        competitor_avoids_text = self.ui.text_competitor.toPlainText()

        ### No action if nothing exists
        if project_avoids_text == '' and competitor_avoids_text == '':
            return

        ### Save avoids in config file
        save_project_competitor_to_file(self.config, project_avoids_text, competitor_avoids_text)

        ### Parse avoids and concat to complete avoids df
        addtl_avoids_df = parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text)
        self.set_avoids_table_data(addtl_avoids_df)

    @error_handler
    def save_project_competitor_avoids(self, val):
        """ Parse and save user-defined project/competitor avoids from current session. """

        project_avoids_text = self.ui.text_project_avoids.toPlainText()
        competitor_avoids_text = self.ui.text_competitor.toPlainText()

        ### Raise UserError if nothing entered by button clicked
        if project_avoids_text == '' and competitor_avoids_text == '':
            raise UserError("No avoids to save!")

        ### Save avoids in config file
        save_project_competitor_to_file(self.config, project_avoids_text, competitor_avoids_text)

        ### Parse avoids and concat to complete avoids df
        addtl_avoids_df = parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text)
        self.set_avoids_table_data(addtl_avoids_df)

    @error_handler
    def set_project_competitor_avoids_from_file(self):
        """ Set text area contents for existing project/competitor avoids. """

        proj_text, comp_text = read_project_competitor_from_file(self.config)
        self.ui.text_project_avoids.setPlainText(proj_text)
        self.ui.text_competitor.setPlainText(comp_text)

    def raise_error(self, err):
        """ Raise error in a dialogue box. """

        self.err_dialogue.showMessage(str(err))

    def raise_critical_error(self, err):
        """ Critical message box for any unexpected errors. """

        QMessageBox.critical(self, 'An unexpected error occurred', traceback.format_exc())

    def clickable(self, widget):
        """ Wrapper to bestow a 'clickable' component to a widget."""

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
        """ Onclick event for group box containing check_uncheck all checkbox. """

        val = not self.ui.checkbox_all.isChecked()
        self.check_uncheck_all(val)
        self.ui.checkbox_all.setChecked(val)

    def click_group_inn(self):
        """ Onclick event for group box containing INN checkbox. """

        self.ui.checkbox_inn.setChecked(not self.ui.checkbox_inn.isChecked())

    def click_group_market_research(self):
        """ Onclick event for group box containing Market Research checkbox. """

        self.ui.checkbox_market_research.setChecked(not self.ui.checkbox_market_research.isChecked())

    def click_group_linguistics(self):
        """ Onclick event for group box containing Linguistics checkbox. """

        self.ui.checkbox_linguistic.setChecked(not self.ui.checkbox_linguistic.isChecked())

    def click_group_competitor(self):
        """ Onclick event for group box containing Competitor checkbox. """

        self.ui.checkbox_competitor.setChecked(not self.ui.checkbox_competitor.isChecked())

    def click_group_project_avoids(self):
        """ Onclick event for group box containing Project Avoids checkbox. """

        self.ui.checkbox_project.setChecked(not self.ui.checkbox_project.isChecked())

    def closeEvent(self, event):
        """ when closing create a pop-up to confirm. Can configure this to have no pop-up. """

        if self.config.get('confirm_exit', '1') == '0':
            choice = QMessageBox.Yes
        else:
            choice = QMessageBox.question(self, "Quit", "Leave?", QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes :
            QMainWindow.closeEvent(self, event)
        else :
            event.ignore()

    def close_app(self):
        """ On click event for Exit button. """

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
