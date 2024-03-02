import logging
from enum import Enum


class LogLevel(Enum):
    INFO = 1
    DEBUG = 2
    TRACE = 3


class Logger:

    verbosity_level = 0

    @staticmethod
    def log(message: str, level: LogLevel):
        if level.value >= Logger.verbosity_level:
            logging.log(logging.INFO, message)

    @staticmethod
    def info(message: str):
        Logger.log(message, LogLevel.INFO)

    @staticmethod
    def debug(message: str):
        Logger.log(message, LogLevel.DEBUG)

    @staticmethod
    def trace(message: str):
        Logger.log(message, LogLevel.TRACE)
