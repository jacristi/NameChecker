from functools import partial

import pandas as pd
import numpy as np
from src.utils.common_utils import error_handler

import src.utils.constants as c



def setup_base_results_df(names_list, checked_avoid_categories):
    results_df = pd.DataFrame.from_dict({'Name':[]})
    # results_df['Name'] = names_list

    for cat in checked_avoid_categories:
        results_df[cat] = ''

    return results_df

@error_handler
def check_names_for_avoids(names_list, ignore_list, avoids_df, checked_avoids):
    """ """
    checked_avoid_categories = [i for i in checked_avoids if checked_avoids[i] is True]

    results_df = setup_base_results_df(names_list, checked_avoid_categories)

    filtered_avoids_df = avoids_df[avoids_df['category'].isin(checked_avoid_categories)]

    for name in names_list:
        results_df = check_name_against_avoids(name, filtered_avoids_df, ignore_list, results_df)

    cat_cols = list(results_df.columns)
    cat_cols.remove('Name')

    results_df = results_df.replace('', np.NaN).dropna(subset=cat_cols, how='all')
    results_df = results_df.dropna(axis=1, how='all')
    results_df = results_df.replace(np.NaN, '')

    return results_df


def check_prefix(name, avoid):
    """ """
    return name.lower().startswith(avoid.lower())


def check_infix(name, avoid):
    """ """
    return avoid in name[1:-1]


def check_suffix(name, avoid):
    """ """
    return name.lower().endswith(avoid.lower())


def check_anywhere(name, avoid):
    """ """
    return avoid.lower() in name.lower()


def check_string_compare(name, avoid):
    return name.lower() in avoid.lower()


def check_string_compare_combo(name, avoid):
    """ """
    return (name.lower()[0] == avoid.lower()[0]) and (name.lower()[-3:] == avoid.lower()[-3:])


def check_string_compare_n_letters(name, avoid, n):
    """ """
    return any(name.lower()[i:i+n] in avoid.lower() for i in range(len(name)-n))


TYPE_CHECK_FUNCS = {
    c.PREFIX:               check_prefix,
    c.INFIX:                check_infix,
    c.SUFFIX:               check_suffix,
    c.ANYWHERE:             check_anywhere,
    c.STRING_COMPARE:       partial(check_string_compare_n_letters, n=4),
    c.STRING_COMPARE_COMBO: check_string_compare_combo,
}

def check_name_against_avoidsx(name, avoids_df, ignore_list, results_df):
    """ """

    avoid_types = set(avoids_df['type'])

    for t in avoid_types:
        ### Filter avoids by type
        t_df = avoids_df[avoids_df['type'] == t]

        ### Get the type function(s) to check (e.g. check_prefix for type == 'prefix')
        check_func = TYPE_CHECK_FUNCS[t]

        ### iter over rows
        for ind, row in t_df[['value', 'category']].drop_duplicates().iterrows():
            val = row['value']
            cat = row['category']
            val_str = None

            if any([val in ignore for ignore in ignore_list]):
                continue

            if t == c.STRING_COMPARE:
                if check_string_compare_combo(name, val):
                    val_str = f'{val} (combo)'
                else:
                    for l in range(len(name), 3, -1):
                        if check_string_compare_n_letters(name, val, l):
                            val_str = f'{val} ({l} letter string)'
                            break

            elif check_func(name, val):
                ### Get category and value (type)
                val_str = f'{val} ({t})'

            # Add new or append value to appropriate name + category cell
            if val_str is not None:
                results_df[row['category']] = np.where(
                    results_df['Name'] == name,
                    np.where(
                        results_df[cat] == '',
                        val_str,
                        results_df[cat] + '\n' + val_str),
                    results_df[cat]
                )

    return results_df


def check_name_against_avoids(name, avoids_df, ignore_list, results_df):
    """ """
    avoids_df = avoids_df[~avoids_df['value'].isin(ignore_list)].drop_duplicates()

    sc_avoids_df = avoids_df[avoids_df['type'] == c.STRING_COMPARE]
    avoids_df = avoids_df[avoids_df['type'] != c.STRING_COMPARE]

    avoids_df['hit'] = [TYPE_CHECK_FUNCS[t](name, v) for v, t in zip(avoids_df['value'], avoids_df['type'])]

    res_df = avoids_df[avoids_df['hit'] == True]
    res_df['Name'] = name
    piv = pd.pivot_table(res_df, values=['value', 'type'], columns='category', aggfunc=lambda x: ','.join(x))

    df_dict = {
        'Name': [name]
    }

    for cat in list(piv.columns):
        typs = piv[cat].values[0].split(',')
        vals = piv[cat].values[1].split(',')
        z = list(zip(vals, [f'({t})' for t in typs]))
        df_dict[cat] = ['\n'.join([' '.join(i) for i in z])]

    if not sc_avoids_df.empty:
        for ind, row in sc_avoids_df[['value', 'category']].iterrows():
            val = row['value']
            cat = row['category']
            val_str = None

            ### String comparison checks are not as simple :/
            if check_string_compare(name, val):
                val_str = f'{val} (string match)'
            elif check_string_compare_combo(name, val):
                val_str = f'{val} (combo)'
            else:
                for l in range(len(name), c.STRING_COMPARE_MINIMUM-1, -1):
                    if check_string_compare_n_letters(name, val, l):
                        val_str = f'{val} ({l} letter similar)'
                        break
            if val_str is not None:
                try:
                    new_val = f'{df_dict[cat]}\n{val_str}'
                    df_dict[cat] = new_val
                except KeyError:
                    df_dict[cat] = val_str

    df = pd.DataFrame.from_dict(df_dict)

    return pd.concat([results_df, df])


"""
vimzovir
enbrox
holvira
daxorel
daxovax
humiva
edorel
account
boy
laughable
wipe
squirrel
marble
calculate
vengeful
marvelous
tearful
zippy
birthday
record
vast
salty
icky
obsolete
flowery
pine
second-hand
soup
sin
worried
boat
rabbit
leg
boy
waste
butter
prefer
savory
literate
rely
army
communicate
scrape
bite
efficient
snail
right
ordinary
beds
pat
frightening
tickle
quiver
eminent
approve
graceful
modern
hour
laugh
park
home
spare
hammer
drunk
teeth
respect
reach
glass
songs
neat
promise
sparkle
object
trot
secretary
quaint
view
advice
natural
supreme
phobic
fork
label
soap
symptomatic
"""