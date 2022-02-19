from functools import partial

import pandas as pd
import numpy as np
from src.utils.common_utils import error_handler

import src.utils.constants as c


def setup_base_results_df(names_list, checked_avoid_categories):
    """ Set up the base results Dataframe which will be built upon by further processes. """

    results_df = pd.DataFrame.from_dict({c.NAME_FIELD:[]})

    for cat in checked_avoid_categories:
        results_df[cat] = ''

    return results_df


@error_handler
def check_names_for_avoids(names_list, ignore_list, avoids_df, checked_avoids):
    """ Primary check_names controller function. """

    ### Get all categories which have been 'checked'
    checked_avoid_categories = [i for i in checked_avoids if checked_avoids[i] is True]

    ### Set up base df and keep only checked categories
    results_df = setup_base_results_df(names_list, checked_avoid_categories)
    filtered_avoids_df = avoids_df[avoids_df[c.CATEGORY_FIELD].isin(checked_avoid_categories)]

    ### Run check for each name
    for name in names_list:
        results_df = check_name_against_avoids(name, filtered_avoids_df, ignore_list, results_df)

    ### Get list of all category columns in the resutls dataframe, removeing 'Name'
    cat_cols = list(results_df.columns)
    cat_cols.remove(c.NAME_FIELD)

    ### Replace empty strings with NaN and drop columns where all values are null
    # Then replace nulls back with empty string
    results_df = results_df.replace('', np.NaN).dropna(subset=cat_cols, how='all')
    results_df = results_df.dropna(axis=1, how='all')
    results_df = results_df.replace(np.NaN, '')

    return results_df


def check_prefix(name, avoid):
    """ True if name starts with avoid. """
    return name.lower().startswith(avoid.lower())


def check_infix(name, avoid):
    """ True if avoid exists within the name (excluding first/last letter) """
    return avoid in name[1:-1]


def check_suffix(name, avoid):
    """ True if name ends with avoid. """
    return name.lower().endswith(avoid.lower())


def check_anywhere(name, avoid):
    """ True if the avoid is anywhere in the name. """
    return avoid.lower() in name.lower()


def check_string_compare(name, avoid):
    """ True if the name matches or is contained within the avoid. """
    return name.lower() in avoid.lower()


def check_string_compare_combo(name, avoid):
    """ True if the first letter and last 3 letters matches the avoid. """
    return (name.lower()[0] == avoid.lower()[0]) and (name.lower()[-3:] == avoid.lower()[-3:])


def check_string_compare_n_letters(name, avoid, n):
    """ Returns First n-letter substring shared between the name and avoid. """
    for i in range(len(name)-(n-1)):
        if name.lower()[i:i+n] in avoid.lower():
            return name.lower()[i:i+n]
    else:
        return None

### Functions mapped to a type
TYPE_CHECK_FUNCS = {
    c.PREFIX:               check_prefix,
    c.INFIX:                check_infix,
    c.SUFFIX:               check_suffix,
    c.ANYWHERE:             check_anywhere,
    c.NAME_MATCH:           check_string_compare,
}

def check_name_against_avoids(name, avoids_df, ignore_list, results_df):
    """ Check a single name against a full avoids dataframe. Append the results to results_df """

    ### Filter out all avoids contained within any ignore string
    ignore_mask = [not any(a in i for i in ignore_list) for a in avoids_df[c.VALUE_FIELD]]
    avoids_df = avoids_df[ignore_mask].drop_duplicates()

    ### Split dataframe on string_compare and non-string_compare avoid types
    sc_avoids_df = avoids_df[avoids_df[c.TYPE_FIELD] == c.STRING_COMPARE]
    avoids_df = avoids_df[avoids_df[c.TYPE_FIELD] != c.STRING_COMPARE]

    ### Filter non-string_compare df on where there are hits
    avoids_df['hit'] = [TYPE_CHECK_FUNCS[t](name, v) for v, t in zip(avoids_df[c.VALUE_FIELD], avoids_df[c.TYPE_FIELD])]
    res_df = avoids_df[avoids_df['hit'] == True]
    res_df[c.NAME_FIELD] = name

    ### Pivot hits table, starting building final result in new dictionary
    piv = pd.pivot_table(res_df, values=[c.VALUE_FIELD, c.TYPE_FIELD], columns=c.CATEGORY_FIELD, aggfunc=lambda x: ','.join(x))

    df_dict = {
        c.NAME_FIELD: [name]
    }

    for cat in list(piv.columns):
        typs = piv[cat].values[0].split(',')
        vals = piv[cat].values[1].split(',')
        z = list(zip(vals, [f'({t})' for t in typs]))
        df_dict[cat] = ['\n'.join([' '.join(i) for i in z])]

    ### Check for string_compare hits
    if not sc_avoids_df.empty:
        for ind, row in sc_avoids_df[[c.VALUE_FIELD, c.CATEGORY_FIELD]].iterrows():
            val = row[c.VALUE_FIELD]
            cat = row[c.CATEGORY_FIELD]
            val_str = None

            ### For simple compare, does the name match or is it contained in the avoid
            if check_string_compare(name, val):
                val_str = f'{val} (string match)'
            ### Do the name and avoid share the same 1st and final 3 letters
            elif check_string_compare_combo(name, val):
                val_str = f'{val} ({name[0]}--{name[-3:]})'
            else:
                ### Do the name and avoid share any substring of n letters
                # n decreases from len(name) to STRING_COMPARE_MINIMUM defined in config
                for l in range(len(name), c.STRING_COMPARE_MINIMUM-1, -1):
                    ret = check_string_compare_n_letters(name, val, l)
                    if ret is not None:
                        val_str = f'{val} (*{ret}*)'
                        break

            ### format the val_str if exists
            if val_str is not None:
                try:
                    new_val = f'{df_dict[cat]}\n{val_str}'
                    df_dict[cat] = new_val
                except KeyError:
                    df_dict[cat] = val_str

    ### Create the result from df_dict and return concatted results
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