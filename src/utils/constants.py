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

SHORTHAND_MAPPING = {
    INN: INN_SHORTHAND,
    LINGUISTIC: LINGUISTIC_SHORTHAND,
    COMPETITOR: COMPETITOR_SHORTHAND,
    PROJECT: PROJECT_SHORTHAND,
    MARKET_RESEARCH: MARKET_RESEARCH_SHORTHAND,
}

PREFIX = 'prefix'
INFIX = 'infix'
SUFFIX = 'suffix'
ANYWHERE = 'anywhere'
STRING_COMPARE = 'string_compare'

FIX_SIGNIFIERS = CONFIG.get('FIX_SIGNIFIERS', '-,~').split(',')
ANYWHERE_SIGNIFIERS = CONFIG.get('ANYWHERE_SIGNIFIERS', '",*').split(',')
