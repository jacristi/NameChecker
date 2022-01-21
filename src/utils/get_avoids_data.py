from configparser import ConfigParser

import pandas as pd

from src.utils.common_utils import error_handler, get_config


@error_handler
def get_avoids_from_file(logger, config):
    """ """
    print("RUNNING FUNC")
    file_path = config.get('PATH_TO_AVOIDS_FILE', 'asdasf.xlsx')

    consol_df = None

    for s_name in ('INN - USAN', 'Pharma', 'Linguistic', 'Competitor'):
        df = pd.read_excel(file_path, sheet_name=s_name)
        df['category'] = s_name

        if consol_df is None:
            consol_df = df
        else:
            consol_df = pd.concat([consol_df, df])

    return consol_df






if __name__ == '__main__':
    from utils.common_utils import Logger

    config = get_config()
    logger = Logger().setup(config)

    get_avoids_from_file(logger, config)