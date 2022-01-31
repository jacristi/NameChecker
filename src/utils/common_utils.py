import logging
from functools import wraps
from datetime import datetime

from src.utils.data_models import UserError


def error_handler(func):
    """ Wrapper for handling potential errors. """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """ """
        ret = None
        obj = args[0] if args else None

        try:
            print(f'Calling {func.__name__}')
            ret = func(*args, **kwargs)
        except UserError as e:
            if obj is not None:
                obj.raise_error(e)
            else:
                raise e
        except Exception as e:
            print(e)
            if obj is not None:
                obj.raise_critical_error(e)
            else:
                raise e
        return ret

    return wrapper


class Logger(logging.Logger):
    """ """

    custom_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file_path = 'output.log'

    def setup(self, config, log_level=logging.INFO):
        """ Setup the logger. """

        self.config = config
        self.log_level = log_level if log_level is not None else logging.INFO
        self.log_file_path = config.get('LOG_FILE_PATH', self.log_file_path)
        self._set_console_handler()
        self.setLevel(self.log_level)

    def _set_console_handler(self):
        """ Set a basic console handler. """

        ch = logging.StreamHandler()
        ch.setLevel(self.log_level)
        ch.setFormatter(self.custom_formatter)
        return True



class Timer:
    """ Tiemr contextmanager for timing the start/end/interval for a given block of code."""

    start = None
    end = None
    interval = None

    def __init__(self, logger, message):
        self.logger = logger
        self.message = message

    def __enter__(self):
        self.start = datetime.now()
        if self.logger is not None:
            self.logger.info(f"Started | {self.message} | at {self.start}")
        else:
            print(f"Started | {self.message} | at {self.start}")

    def __exit__(self, err_class, err_obj, traceback):
        self.end = datetime.now()
        self.interval = (self.end - self.start).total_seconds()

        if self.logger is not None:
            self.logger.info(f"Finished | {self.message} | after {self.interval} at {self.end}")
        else:
            print(f"Finished | {self.message} | after {self.interval} at {self.end}")