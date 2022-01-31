import configparser
from os import path

import pandas as pd
import numpy as np

import src.utils.constants as c
from src.utils.common_utils import error_handler
from src.utils.data_models import UserError


@error_handler
def get_avoids_from_file(logger, config):
    """ Pulls data from master excel sheet (path defined in the config), formats the df and sends back to be displayed in qtable view"""

    file_path = config.get('PATH_TO_AVOIDS_FILE', 'asdasf.xlsx')

    consol_df = None

    ### For each sheet, get the sheet's data and concat to consolidated dataframe
    for s_name in (c.INN, c.LINGUISTIC, c.MARKET_RESEARCH):
        try:
            df = pd.read_excel(file_path, sheet_name=s_name)
        except FileNotFoundError as e:
            return None

        df[c.CATEGORY_FIELD] = s_name

        if consol_df is None:
            consol_df = df
        else:
            consol_df = pd.concat([consol_df, df])

    ### Filter out anything with no type
    consol_df = consol_df[~consol_df[c.TYPE_FIELD].isnull()]

    ### Fill null descriptiosn with default string
    consol_df[c.DESCRIPTION_FIELD] = consol_df[c.DESCRIPTION_FIELD].fillna('--')

    ### Keep only exepected columns
    consol_df = consol_df[[c.VALUE_FIELD, c.TYPE_FIELD, c.DESCRIPTION_FIELD, c.CATEGORY_FIELD]]

    return consol_df



def parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text):
    """ Parse the text for both project and competitor avoids.
        Competitor are simply split on new line
        Project avoids are split on newline and parsed based on specific characters.
    """

    project_avoids = [i.strip() for i in project_avoids_text.split('\n') if i.strip()]
    competitor_avoids = [i.strip() for i in competitor_avoids_text.split('\n') if i.strip()]

    if project_avoids == [] and competitor_avoids == []:
        raise UserError('No avoids entered')

    ### Start dataframe base
    avoids_df = pd.DataFrame.from_dict({
        c.VALUE_FIELD:        [],
        c.TYPE_FIELD:         [],
        c.DESCRIPTION_FIELD:  [],
        c.CATEGORY_FIELD:     []})

    avoids_df[c.VALUE_FIELD] = project_avoids + competitor_avoids

    ### Get masks for infix, suffix, prefix, and anywhere types
    # where first and last characters are contained in FIX_SIGNIFIERS (e.g. -inf-)
    infix_mask = [(i[0] in c.FIX_SIGNIFIERS and i[-1] in c.FIX_SIGNIFIERS) for i in avoids_df[c.VALUE_FIELD]]

    # Where first character is contained within FIX_SIGNIFIERS (e.g -suff)
    suffix_mask = [i[0] in c.FIX_SIGNIFIERS for i in avoids_df[c.VALUE_FIELD]]

    # Where last character is contained within FIX_SIGNIFIERS (e.g. pre-)
    prefix_mask = [i[-1] in c.FIX_SIGNIFIERS for i in avoids_df[c.VALUE_FIELD]]

    # where first and last characters are contained in ANYWHERE_SIGNIFIERS (e.g. "inf")
    anywhere_mask = [(i[0] in c.ANYWHERE_SIGNIFIERS and i[-1] in c.ANYWHERE_SIGNIFIERS) for i in avoids_df[c.VALUE_FIELD]]

    ### Set up type values based on pre-defiend masks
    avoids_df[c.TYPE_FIELD] = np.where(
        infix_mask,
        c.INFIX,
        np.where(
            prefix_mask,
            c.PREFIX,
            np.where(
                suffix_mask,
                c.SUFFIX,
                np.where(
                    anywhere_mask,
                    c.ANYWHERE,
                    c.STRING_COMPARE
                ),
            )
        )
    )

    ### Set category values
    avoids_df[c.CATEGORY_FIELD] = np.where(
        avoids_df[c.VALUE_FIELD].isin(project_avoids),
        c.PROJECT,
        c.COMPETITOR
    )

    ### Set default description
    avoids_df[c.DESCRIPTION_FIELD] = 'User Defined Avoid'

    ### Remove fix/anywhere characters from all avoids
    for i in c.FIX_SIGNIFIERS + c.ANYWHERE_SIGNIFIERS:
        avoids_df[c.VALUE_FIELD] = avoids_df[c.VALUE_FIELD].str.replace(i, '', regex=False)

    return avoids_df


def save_project_competitor_to_file(config, project_avoids_text, competitor_avoids_text):
    """ Save project and competitor avoids to config file for next session. """

    config_path = 'NameEvaluator_conf.ini'
    CONF = configparser.ConfigParser()
    CONF.read(config_path)

    ### Replace newline with comma
    CONF.set(c.CONFIG_AVOIDS_HEADER, c.PROJECT, project_avoids_text.replace('\n', ','))
    CONF.set(c.CONFIG_AVOIDS_HEADER, c.COMPETITOR, competitor_avoids_text.replace('\n', ','))

    ### Save updated config
    with open(config_path, 'w') as config_file:
        CONF.write(config_file)


def read_project_competitor_from_file(config):
    """ Get project/competitor avoids previously saved to config. """

    config_path = 'NameEvaluator_conf.ini'
    if not path.exists(config_path):
        return '', ''

    ### Read values, replace comma with new line and return the updated text
    conf = configparser.ConfigParser()
    conf.read(config_path)
    try:
        proj_text = conf[c.CONFIG_AVOIDS_HEADER].get(c.PROJECT, '').replace(',', '\n')
        comp_text = conf[c.CONFIG_AVOIDS_HEADER].get(c.COMPETITOR, '').replace(',', '\n')
    except KeyError:
        return '', ''

    return proj_text, comp_text

