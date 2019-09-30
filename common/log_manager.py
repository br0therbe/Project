# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-27 11:45
# @Version     : Python 3.6.8
# @Description : 
import logging
import os
from pathlib import Path
from threading import RLock

import requests
from concurrent_log_handler import ConcurrentRotatingFileHandler

ENVIRONMENT = 'Test'
OS_NAME = os.name
BLUE = 94 if OS_NAME == 'nt' else 36
GREEN = 32
YELLOW = 93 if OS_NAME == 'nt' else 33
PURPLISH_RED = 35
RED = 31
STREAM_FORMATTER = logging.Formatter(
    fmt='%(name)s - %(asctime)s - File "%(filename)s", line %(lineno)d - %(funcName)s - %(levelname)s >>> %(message)s',
    datefmt="%H:%M:%S"
)
FILE_FORMATTER = logging.Formatter(
    fmt='%(name)s - %(asctime)s - %(pathname)s:%(lineno)d %(funcName)s - %(levelname)s >>> %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)


class StreamHandler(logging.StreamHandler):
    """
    带颜色的控制台输出日志
    """

    def __init__(self, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        super().__init__(stream)
        self._display_method = 7 if OS_NAME == 'posix' else 0

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

            if record.levelno == 10:
                msg_color = f'\033[{self._display_method};{BLUE}m{msg}\033[0m'
            elif record.levelno == 20:
                msg_color = f'\033[{self._display_method};{GREEN}m{msg}\033[0m'
            elif record.levelno == 30:
                msg_color = f'\033[{self._display_method};{YELLOW}m{msg}\033[0m'
            elif record.levelno == 40:
                msg_color = f'\033[{self._display_method};{PURPLISH_RED}m{msg}\033[0m'  # 紫红色
            elif record.levelno == 50:
                msg_color = f'\033[{self._display_method};{RED}m{msg}\033[0m'
            else:
                msg_color = msg

            stream.write(msg_color)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


class DingTalkHandler(logging.Handler):
    """
    钉钉日志， 1分钟20条消息
    """
    terminator = '\n'

    def __init__(self, access_token: str, level=logging.ERROR):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        super().__init__(level)
        self._ding_talk_api = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
        self._lock = RLock()
        self._title = ENVIRONMENT

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

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
            with self._lock:
                record = self.format(record)
                self._ding_talk(record)
        except Exception:
            self.handleError(record)

    def _ding_talk(self, message: str):
        message = message.strip().replace('\n', '\n> ##### ')
        markdown_data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "Error",
                "text": f"## {self._title} \n> ##### {message}\n"
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False
            }
        }
        headers = {"Content-Type": "application/json; charset=utf-8"}
        requests.request(method='post', url=self._ding_talk_api, json=markdown_data, headers=headers)


class LogManager(object):
    def __init__(self, log_name: str = 'temp', level: int = 10):
        self._log_name = log_name
        self._level = level
        self.logger = logging.getLogger(self._log_name)
        self.logger.setLevel(self._level)

    def add_stream_handler(self, level: int = 20):
        handler = StreamHandler()
        return self.__add_a_handler(handler, level=level, formatter=STREAM_FORMATTER)

    def add_file_handler(self, level: int = 10, folder_path: str = None, filename: str = 'temp.log',
                         file_size: int = 500, backup_count: int = 10):
        if folder_path is None:
            folder_path = str(Path(Path(__file__).absolute().root) / Path('pythonlogs'))
        elif not os.path.exists(folder_path):
            os.makedirs(folder_path)
        log_file = os.path.join(folder_path, filename)
        handler = ConcurrentRotatingFileHandler(log_file, maxBytes=file_size * 1024 * 1024,
                                                backupCount=backup_count, encoding="utf-8")
        return self.__add_a_handler(handler, level=level, formatter=FILE_FORMATTER)

    def add_ding_talk_handler(self, access_token: str, title: str = ENVIRONMENT, level: int = logging.ERROR):
        handler = DingTalkHandler(access_token, level)
        handler.title = title
        return self.__add_a_handler(handler, level=level, formatter=FILE_FORMATTER)

    def __add_a_handler(self, handler: logging.Handler, level: int = 10, formatter: logging.Formatter = None):
        handler.setLevel(level)
        handler.setFormatter(formatter)
        # remind: 官方包已经对 handler 是否存在作出判断
        self.logger.addHandler(handler)
        return self.logger


logger = LogManager().add_stream_handler()

if __name__ == '__main__':
    logging.disable(20)
    # logger.disabled = True
    logger.debug({1: ['test debug!']})
    logger.info('test info!')
    logger.warning('test warning!')
    logger.error('test error!')
    logger.fatal('test fatal!')
