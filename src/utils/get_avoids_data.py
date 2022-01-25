import configparser
import pandas as pd
import numpy as np

import src.utils.constants as c
from src.utils.common_utils import error_handler


@error_handler
def get_avoids_from_file(logger, config):
    """ """
    print("RUNNING FUNC")
    file_path = config.get('PATH_TO_AVOIDS_FILE', 'asdasf.xlsx')

    consol_df = None

    for s_name in (c.INN, c.LINGUISTIC, c.MARKET_RESEARCH):
        df = pd.read_excel(file_path, sheet_name=s_name)
        df['category'] = s_name

        if consol_df is None:
            consol_df = df
        else:
            consol_df = pd.concat([consol_df, df])

    consol_df = consol_df[~consol_df['type'].isnull()]
    consol_df['description'] = consol_df['description'].fillna('')
    return consol_df



def parse_project_competitor_avoids(project_avoids_text, competitor_avoids_text):
    """ """
    project_avoids = [i.strip() for i in project_avoids_text.split('\n') if i.strip()]
    competitor_avoids = [i.strip() for i in competitor_avoids_text.split('\n') if i.strip()]
    avoids_df = pd.DataFrame.from_dict({
        'value':        [],
        'type':         [],
        'description':  [],
        'category':     []})


    avoids_df['value'] = project_avoids + competitor_avoids
    infix_mask = [(i[0] in c.FIX_SIGNIFIERS and i[-1] in c.FIX_SIGNIFIERS) for i in avoids_df['value']]
    suffix_mask = [i[0] in c.FIX_SIGNIFIERS for i in avoids_df['value']]
    prefix_mask = [i[-1] in c.FIX_SIGNIFIERS for i in avoids_df['value']]
    anywhere_mask = [(i[0] in c.ANYWHERE_SIGNIFIERS and i[-1] in c.ANYWHERE_SIGNIFIERS) for i in avoids_df['value']]

    avoids_df['type'] = np.where(
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

    avoids_df['category'] = np.where(
        avoids_df['value'].isin(project_avoids),
        c.PROJECT,
        c.COMPETITOR
    )

    avoids_df['description'] = ''

    for i in c.FIX_SIGNIFIERS + c.ANYWHERE_SIGNIFIERS:
        avoids_df['value'] = avoids_df['value'].str.replace(i, '', regex=False)

    return avoids_df


def save_project_competitor_to_file(config, project_avoids_text, competitor_avoids_text):
    """ """
    avoid_file_path = config.get('PATH_TO_PROJECT_AVOIDS', 'proj_comp_avoids.txt')

    proj_comp_avoids = configparser.ConfigParser()
    proj_comp_avoids['DEFAULT'] = {
        c.PROJECT: project_avoids_text.replace('\n', ','),
        c.COMPETITOR: competitor_avoids_text.replace('\n', ','),
    }

    with open(avoid_file_path, 'w') as config_file:
        proj_comp_avoids.write(config_file)


def read_project_competitor_from_file(config):
    """ """
    avoid_file_path = config.get('PATH_TO_PROJECT_AVOIDS', 'proj_comp_avoids.txt')

    conf = configparser.ConfigParser()
    conf.read(avoid_file_path)

    proj_text = conf['DEFAULT'].get(c.PROJECT, '').replace(',', '\n')
    comp_text = conf['DEFAULT'].get(c.COMPETITOR, '').replace(',', '\n')

    return proj_text, comp_text

