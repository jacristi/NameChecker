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

def check_string_compare(name, avoid, n):
    """ """

    return False


TYPE_CHECK_FUNCS = {
    c.PREFIX:           check_prefix,
    c.INFIX:            check_infix,
    c.SUFFIX:           check_suffix,
    c.ANYWHERE:         check_anywhere,
    c.STRING_COMPARE:   check_string_compare,
}

def check_name_against_avoids(name, avoids_df, ignore_list, results_df):
    """ """

    for t in set(avoids_df['type']):
        if t == c.STRING_COMPARE:
            pass
        else:
            ### Filter df on
            t_df = avoids_df[avoids_df['type'] == t]

            ### Get the type function to check (e.g. check_prefix for type == 'prefix')
            check_func = TYPE_CHECK_FUNCS[t]

            for ind, row in t_df[['value', 'category']].drop_duplicates().iterrows():
                if check_func(name, row['value']):
                    ### Get category and value (type)
                    cat = row['category']
                    row_val = row['value']
                    val = f'{row_val} ({t})'

                    ### Add new or append value to appropriate name + category cell
                    results_df[row['category']] = np.where(
                        results_df['name'] == name,
                        np.where(
                            results_df[cat] == '',
                            val,
                            results_df[cat] + '\n' + val),
                        results_df[cat]
                    )

    return results_df






### Try to be category agnostic, only use value, type - category used ONLY to show which category hit was in

# def check_market_research_avoids():
#     """ """
#     pass

# def check_inn_avoids():
#     """ """
#     pass

# def check_competitor_avoids():
#     """ """
#     pass

# def check_linguistic_avoids():
#     """ """
#     pass

# def check_project_avoids():
#     """ """
#     pass


# def check_for_avoids(names, ignores, avoids_df, category):
#     AVOIDS_CHECK_FUNCS = {
#     c.MARKET_RESEARCH:  check_market_research_avoids,
#     c.INN:              check_inn_avoids,
#     c.PROJECT:          check_project_avoids,
#     c.LINGUISTIC:       check_linguistic_avoids,
#     c.COMPETITOR:       check_competitor_avoids,
# }