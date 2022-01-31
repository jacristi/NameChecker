import configparser
from os import path

import pandas as pd
import numpy as np

import src.utils.constants as c
from src.utils.common_utils import error_handler
from src.utils.data_models import UserError


@error_handler
def get_avoids_from_file(logger, config):
    """ """

    file_path = config.get('PATH_TO_AVOIDS_FILE', 'asdasf.xlsx')

    consol_df = None

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

    consol_df = consol_df[~consol_df[c.TYPE_FIELD].isnull()]
    consol_df[c.DESCRIPTION_FIELD] = consol_df[c.DESCRIPTION_FIELD].fillna('')

    consol_df = consol_df[[c.VALUE_FIELD, c.TYPE_FIELD, c.DESCRIPTION_FIELD, c.CATEGORY_FIELD]]

    return consol_df



def parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text):
    """ """
    project_avoids = [i.strip() for i in project_avoids_text.split('\n') if i.strip()]
    competitor_avoids = [i.strip() for i in competitor_avoids_text.split('\n') if i.strip()]

    if project_avoids == [] and competitor_avoids == []:
        raise UserError('No avoids entered')

    avoids_df = pd.DataFrame.from_dict({
        c.VALUE_FIELD:        [],
        c.TYPE_FIELD:         [],
        c.DESCRIPTION_FIELD:  [],
        c.CATEGORY_FIELD:     []})


    avoids_df[c.VALUE_FIELD] = project_avoids + competitor_avoids
    infix_mask = [(i[0] in c.FIX_SIGNIFIERS and i[-1] in c.FIX_SIGNIFIERS) for i in avoids_df[c.VALUE_FIELD]]
    suffix_mask = [i[0] in c.FIX_SIGNIFIERS for i in avoids_df[c.VALUE_FIELD]]
    prefix_mask = [i[-1] in c.FIX_SIGNIFIERS for i in avoids_df[c.VALUE_FIELD]]
    anywhere_mask = [(i[0] in c.ANYWHERE_SIGNIFIERS and i[-1] in c.ANYWHERE_SIGNIFIERS) for i in avoids_df[c.VALUE_FIELD]]

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

    avoids_df[c.CATEGORY_FIELD] = np.where(
        avoids_df[c.VALUE_FIELD].isin(project_avoids),
        c.PROJECT,
        c.COMPETITOR
    )

    avoids_df[c.DESCRIPTION_FIELD] = 'User Defined Avoid'

    for i in c.FIX_SIGNIFIERS + c.ANYWHERE_SIGNIFIERS:
        avoids_df[c.VALUE_FIELD] = avoids_df[c.VALUE_FIELD].str.replace(i, '', regex=False)

    return avoids_df


def save_project_competitor_to_file(config, project_avoids_text, competitor_avoids_text):
    """ """
    config_path = 'NameEvaluator_conf.ini'

    CONF = configparser.ConfigParser()
    CONF.read(config_path)

    CONF.set(c.CONFIG_AVOIDS_HEADER, c.PROJECT, project_avoids_text.replace('\n', ','))
    CONF.set(c.CONFIG_AVOIDS_HEADER, c.COMPETITOR, competitor_avoids_text.replace('\n', ','))

    with open(config_path, 'w') as config_file:
        CONF.write(config_file)


def read_project_competitor_from_file(config):
    """ """
    config_path = 'NameEvaluator_conf.ini'

    if not path.exists(config_path):
        return '', ''

    conf = configparser.ConfigParser()
    conf.read(config_path)
    try:
        proj_text = conf[c.CONFIG_AVOIDS_HEADER].get(c.PROJECT, '').replace(',', '\n')
        comp_text = conf[c.CONFIG_AVOIDS_HEADER].get(c.COMPETITOR, '').replace(',', '\n')
    except KeyError:
        return '', ''

    return proj_text, comp_text

