from configparser import ConfigParser

def get_config():
    """ """
    config_path = 'config.ini'
    CONF = ConfigParser()
    CONF.read(config_path)
    return CONF['DEFAULT']