import logging
import sys
from enum import Enum

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%H:%M:%S")
handler.setFormatter(formatter)
root_logger.addHandler(handler)


class LogLevel(Enum):
    INFO = 1
    DEBUG = 2
    TRACE = 3


class Logger:

    verbosity_level = 0

    @staticmethod
    def log(message: str, level: LogLevel):
        if level.value <= Logger.verbosity_level:
            root_logger.log(logging.INFO, message)

    @staticmethod
    def info(message: str):
        Logger.log(message, LogLevel.INFO)

    @staticmethod
    def debug(message: str):
        Logger.log(message, LogLevel.DEBUG)

    @staticmethod
    def trace(message: str):
        Logger.log(message, LogLevel.TRACE)
