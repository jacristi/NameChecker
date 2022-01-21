import logging
from functools import wraps
from datetime import datetime
from configparser import ConfigParser


def get_config():
    """ """
    config_path = 'config.ini'
    CONF = ConfigParser()
    CONF.read(config_path)
    return CONF['DEFAULT']

def error_handler(func):
    """ """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """ """
        logger = kwargs.get('logger')
        with Timer(logger, func.__name__):
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                raise e

        return ret

    return wrapper


def read_config():
    """ """
    pass


class Logger(logging.Logger):
    """ """

    custom_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file_path = 'output.log'
    def setup(self, config, log_level=logging.INFO):
        """ """
        self.config = config
        self.log_level = log_level if log_level is not None else logging.INFO
        self.log_file_path = config.get('LOG_FILE_PATH', self.log_file_path)
        self._set_console_handler()
        self._set_file_handler()

    def _set_console_handler(self):
        """ """
        ch = logging.StreamHandler()
        ch.setLevel(self.log_level)
        ch.setFormatter(self.custom_formatter)
        return True

    def _set_file_handler(self):
        """ """
        return True


class Timer:
    """ """
    start = None
    end = None
    interval = None

    def __init__(self, logger, message):
        """ """
        self.logger = logger
        self.message = message

    def __enter__(self):
        """ """
        self.start = datetime.now()
        if self.logger is not None:
            self.logger.info(f"Started | {self.message} | at {self.start}")
        else:
            print(f"Started | {self.message} | at {self.start}")


    def __exit__(self, err_class, err_obj, traceback):
        """ """
        self.end = datetime.now()
        self.interval = (self.end - self.start).total_seconds()
        if self.logger is not None:
            self.logger.info(f"Finished | {self.message} | after {self.interval} at {self.end}")
        else:
            print(f"Finished | {self.message} | after {self.interval} at {self.end}")