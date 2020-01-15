# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2020-01-03 9:48
# @Version     : Python 3.6.8
__all__ = ['LogManager']
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

STREAM_FORMATTER = logging.Formatter(
    fmt='%(asctime)s - %(name)s - "%(filename)s:%(lineno)d" - %(funcName)s - %(levelname)s >>> %(message)s',
    datefmt="%H:%M:%S"
)
FILE_FORMATTER = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(pathname)s:%(lineno)d %(funcName)s - %(levelname)s >>> %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

OS_NAME = os.name
BLUE = 94 if OS_NAME == 'nt' else 36
GREEN = 32
YELLOW = 93 if OS_NAME == 'nt' else 33
RED = 31
PURPLISH_RED = 35
_DISPLAY_METHOD = 7 if OS_NAME == 'posix' else 0

DEBUG_LEVEL = 10
INFO_LEVEL = 20
WARNING_LEVEL = 30
ERROR_LEVEL = 40
CRITICAL_LEVEL = 50
LEVEL_COLOR_MAP = {
    DEBUG_LEVEL: lambda msg: f'\033[{_DISPLAY_METHOD};{BLUE}m{msg}\033[0m',
    INFO_LEVEL: lambda msg: f'\033[{_DISPLAY_METHOD};{GREEN}m{msg}\033[0m',
    WARNING_LEVEL: lambda msg: f'\033[{_DISPLAY_METHOD};{YELLOW}m{msg}\033[0m',
    ERROR_LEVEL: lambda msg: f'\033[{_DISPLAY_METHOD};{RED}m{msg}\033[0m',  # 紫红色
    CRITICAL_LEVEL: lambda msg: f'\033[{_DISPLAY_METHOD};{PURPLISH_RED}m{msg}\033[0m',
}


class _ColorStreamHandler(logging.StreamHandler):
    """
    带颜色的控制台输出日志
    """

    def __init__(self, stream=None):
        """
        Initialize the handler.
        If stream is not specified, sys.stderr is used.
        """
        super().__init__(stream)

    def emit(self, record):
        """
        Emit a record.
        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            msg_color = (LEVEL_COLOR_MAP.get(record.levelno) or LEVEL_COLOR_MAP[DEBUG_LEVEL])(msg)
            stream.write(msg_color)
            stream.write(self.terminator)
            self.flush()
        except (OSError, IOError, Exception):
            self.handleError(record)


class LogManager(object):
    def __init__(self, log_name: str = 'temp', level: int = 10):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
        self._log_name = log_name

    def add_stream_handler(self, level: int = 10):
        handler = _ColorStreamHandler()
        return self.__add_a_handler(handler, level=level, formatter=STREAM_FORMATTER)

    def add_file_handler(self, level: int, filename: str = None, folder_path: str = None, backup_count: int = 30):
        self.add_stream_handler()
        return self._add_file_handler(level, filename, folder_path, backup_count)

    def _add_file_handler(self, level: int, filename: str = None, folder_path: str = None, backup_count: int = 30):
        if folder_path is None:
            folder_path = str(Path(Path(__file__).absolute().root) / Path('pythonlogs'))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if filename is None:
            filename = self._log_name
        log_file = os.path.join(folder_path, filename)
        handler = TimedRotatingFileHandler(log_file, when='D', backupCount=backup_count, encoding="utf-8")
        return self.__add_a_handler(handler, level=level, formatter=FILE_FORMATTER)

    def __add_a_handler(self, handler: logging.Handler, level: int = 10, formatter: logging.Formatter = None):
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return self.logger


if __name__ == '__main__':
    logger = LogManager('test').add_stream_handler(10)
    logger.debug('123')
    logger.info('123')
    logger.warning('123')
    logger.error('123')
    logger.critical('123')
