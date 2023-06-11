import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Union

from .CustomFormatter import CustomFormatter

# Define the default logging level
DEFAULT_LOGGING_LEVEL = logging.INFO

# Define the default log directory
DEFAULT_LOG_DIR = os.path.dirname(os.path.realpath(__file__))


class LoggerSingleton:
    __instance: 'LoggerSingleton' = None
    __log_level: int = DEFAULT_LOGGING_LEVEL
    __log_dir: str = DEFAULT_LOG_DIR

    @classmethod
    def get_instance(cls) -> 'LoggerSingleton':
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.loggers = {}

    def check_log_level(self, level: Union[str, int]) -> None:
        if isinstance(level, str):
            if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                raise ValueError(f'Invalid log level: {level}')
        elif isinstance(level, int):
            if level not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
                raise ValueError(f'Invalid log level: {level}')
        else:
            raise TypeError(f'Invalid log level type: {type(level)}')

    # New setter method for changing log level
    def set_log_dir(self, dir_path: str) -> None:
        self.__log_dir = os.path.join(dir_path, 'logs')
        if not os.path.exists(self.__log_dir):
            os.makedirs(self.__log_dir)

    def set_level(self, level) -> None:
        self.check_log_level(level)
        if isinstance(level, str):
            self.__log_level = getattr(logging, level)
        else:
            self.__log_level = level

        # Update the level of all loggers that have been created
        for logger in self.loggers.values():
            logger.setLevel(self.__log_level)

    def get_console_handler(self) -> logging.StreamHandler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.get_formatter())
        return console_handler

    def get_file_handler(self) -> TimedRotatingFileHandler:
        file_handler = TimedRotatingFileHandler(os.path.join(self.__log_dir, 'logs.log'), when='midnight')
        file_handler.setFormatter(self.get_file_formatter())
        return file_handler

    def get_formatter(self) -> CustomFormatter:
        return CustomFormatter()

    def get_file_formatter(self) -> logging.Formatter:
        return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def get_logger(self, logger_name: str) -> logging.Logger:
        if logger_name in self.loggers:
            return self.loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(self.__log_level)  # Use the current log level
        logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False

        self.loggers[logger_name] = logger
        return logger


def get_logger(logger_name: str) -> logging.Logger:
    return LoggerSingleton.get_instance().get_logger(logger_name)


# New utility methods
def set_log_level(level) -> None:
    LoggerSingleton.get_instance().set_level(level)


def set_log_dir(dir_path: str) -> None:
    LoggerSingleton.get_instance().set_log_dir(dir_path)
