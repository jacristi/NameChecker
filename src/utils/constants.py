from src.env import get_config

CONFIG = get_config()

INN = 'INN - USAN'
INN_SHORTHAND = 'inn'

LINGUISTIC = 'Linguistic'
LINGUISTIC_SHORTHAND = 'linguistic'

COMPETITOR = 'Competitor'
COMPETITOR_SHORTHAND = 'competitor'

PROJECT = 'Project'
PROJECT_SHORTHAND = 'project'

MARKET_RESEARCH = 'Market Research'
MARKET_RESEARCH_SHORTHAND = 'market_research'

INTERNAL = 'Internal'
INTERNAL_SHORTHAND = 'internal'

SHORTHAND_MAPPING = {
    INN: INN_SHORTHAND,
    LINGUISTIC: LINGUISTIC_SHORTHAND,
    COMPETITOR: COMPETITOR_SHORTHAND,
    PROJECT: PROJECT_SHORTHAND,
    MARKET_RESEARCH: MARKET_RESEARCH_SHORTHAND,
}

NAME_FIELD = 'Name'
VALUE_FIELD = 'value'
CATEGORY_FIELD = 'category'
TYPE_FIELD = 'type'
DESCRIPTION_FIELD = 'description'

PREFIX = 'prefix'
INFIX = 'infix'
SUFFIX = 'suffix'
ANYWHERE = 'anywhere'
STRING_COMPARE = 'string_compare'
STRING_COMPARE_COMBO = 'combo'
STRING_MATCH = 'string_match'
NAME_MATCH = 'name_match'

STRING_COMPARE_MINIMUM = int(CONFIG.get("STRING_COMPARE_MINIMUM", 3))
FIX_SIGNIFIERS = CONFIG.get('FIX_SIGNIFIERS', '-,~').split(',')
ANYWHERE_SIGNIFIERS = CONFIG.get('ANYWHERE_SIGNIFIERS', '",*').split(',')

CONFIG_AVOIDS_HEADER = 'PROJ_COMP_AVOIDS'

PROJECT_AVOID_PLACEHOLDER_TEXT = """Enter project-specific avoids, such as prefix, infix or suffix letter strings. One avoid per line.

Prefix avoids should be formatted with a hyphen AFTER the letter string (ex: Dal-).

Suffix avoids should be formatted with a hyphen BEFORE the letter string (ex: -bri).

Infix or anywhere avoids should be formatted with a hyphen or asterisks or single quote BEFORE and AFTER the letter string (ex: *rex* OR -rex- OR ‘rex’)
"""
INTERNAL_NAMES_PLACEHOLDER_TEXT = """Enter internally created names or derivations here. One name per line.

Will be screened for identical matches.
"""
COMPETITORS_PLACEHOLDER_TEXT = """Enter competitor names here. One name per line.

Will be screened for similar letter strings.
"""