import pandas as pd
import numpy as np

import src.utils.constants as c



def setup_base_results_df(names_list, checked_avoid_categories):
    results_df = pd.DataFrame.from_dict({'name':[]})
    results_df['name'] = names_list

    for cat in checked_avoid_categories:
        results_df[cat] = ''

    return results_df


def check_names_for_avoids(names_list, ignore_list, avoids_df, checked_avoids):
    """ """
    checked_avoid_categories = [i for i in checked_avoids if checked_avoids[i] is True]

    results_df = setup_base_results_df(names_list, checked_avoid_categories)

    filtered_avoids_df = avoids_df[avoids_df['category'].isin(checked_avoid_categories)]

    for name in names_list:
        check_name_against_avoids(name, filtered_avoids_df, ignore_list, results_df)

    cat_cols = list(results_df.columns)
    cat_cols.remove('name')

    results_df = results_df.replace('', np.NaN).dropna(subset=cat_cols, how='all')
    results_df = results_df.dropna(axis=1, how='all')
    results_df = results_df.replace(np.NaN, '')

    return results_df


def check_prefix(name, avoid):
    """ """

    return name.lower().startswith(avoid.lower())

def check_infix(name, avoid):
    """ """

    return avoid.lower() in name.lower()[1:-1]


def check_suffix(name, avoid):
    """ """

    return name.lower().endswith(avoid.lower())

def check_anywhere(name, avoid):
    """ """

    return avoid.lower() in name.lower()


def string_compare_prefix(name, avoid):
    """ """

    return name.lower()[0:3] == avoid.lower()[0:3]

def string_compare_4_letter(name, avoid):
    """ """

    return any(name.lower()[i:i+4] in avoid.lower() for i in range(len(name)-4))

def string_compare_combo(name, avoid):
    """ """

    return (name.lower()[0] == avoid.lower()[0]) and (name.lower()[-3:] == avoid.lower()[-3:])


def check_string_compare(name, avoid, n):
    """ """

    return False


TYPE_CHECK_FUNCS = {
    c.PREFIX:           [check_prefix],
    c.INFIX:            [check_infix],
    c.SUFFIX:           [check_suffix],
    c.ANYWHERE:         [check_anywhere],
    c.STRING_COMPARE:   [string_compare_prefix, string_compare_4_letter, string_compare_combo],
}

def check_name_against_avoids(name, avoids_df, ignore_list, results_df):
    """ """

    for t in set(avoids_df['type']):

        t_df = avoids_df[avoids_df['type'] == t]

        ### Get the type function(s) to check (e.g. check_prefix for type == 'prefix')
        for check_func in TYPE_CHECK_FUNCS[t]:
            for ind, row in t_df[['value', 'category']].drop_duplicates().iterrows():
                val = row['value']

                if any([val in ignore for ignore in ignore_list]):
                    continue

                if check_func(name, row['value']):
                    ### Get category and value (type)
                    cat = row['category']

                    val_str = f'{val} ({t})'

                    ### Add new or append value to appropriate name + category cell
                    results_df[row['category']] = np.where(
                        results_df['name'] == name,
                        np.where(
                            results_df[cat] == '',
                            val_str,
                            results_df[cat] + '\n' + val_str),
                        results_df[cat]
                    )

    return results_df
