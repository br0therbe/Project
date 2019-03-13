# -*- encoding: utf-8 -*-
"""
@File    : spiders.py
@Time    : 2019/3/11 13:41
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
from fake_useragent import UserAgent
from functools import wraps
from queue import Queue
from time import time
import logging
import types
import os


class Spiders(object):
    def __init__(self, urls, level=logging.INFO, filename=os.path.basename(__file__)):
        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.DEBUG)

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter(
            fmt='%(levelname)s:: %(asctime)s; File {filename}; %(message)s '.format(filename=filename),
            datefmt="%m/%d/%Y %H:%M:%S"))

        error = logging.FileHandler('error.log', encoding='utf-8')
        error.setLevel(logging.ERROR)
        error.setFormatter(logging.Formatter(
            fmt='%(levelname)s:: %(asctime)s; File {filename}; %(message)s '.format(filename=filename),
            datefmt="%m/%d/%Y %H:%M:%S"))
        total = logging.FileHandler('all.log', encoding='utf-8')
        total.setLevel(logging.DEBUG)
        total.setFormatter(logging.Formatter(
            fmt='%(levelname)s:: %(asctime)s; File {filename}; %(message)s '.format(filename=filename),
            datefmt="%m/%d/%Y %H:%M:%S"))

        logger.addHandler(console)
        logger.addHandler(error)
        logger.addHandler(total)
        self.queue = self.list_to_queue(urls)
        self.value = []

    def response(self):
        pass

    def parse(self):
        pass

    def set_url(self):
        result = self.queue.get_nowait()
        logger.info('url: {}'.format(result))
        return result

    @staticmethod
    def set_headers(**kwargs):
        headers = {
            'User-Agent': UserAgent().random
        }
        for k, v in kwargs.items():
            headers[k] = v
        logger.info('headers: {}'.format(headers))
        return headers

    @staticmethod
    def list_to_queue(urls):
        queue = Queue()
        for each in urls:
            queue.put_nowait(each)
        logger.info('urls: {}'.format(urls))
        return queue


def log_func(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug('in {} is running'.format(func.__name__))
        result = func(*args, **kwargs)
        if result:
            logger.info('result: {}'.format(result))
        logger.debug('in {} is ending!'.format(func.__name__))
        return result
    return inner


def log_response(binding=None):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = ''
            count = 0
            error_msg = []
            while count < 3:
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    lineno = e.__traceback__.tb_next.tb_lineno
                    message = e
                    error_msg.append('line {}; reason {}'.format(lineno, message))
                    count += 1
                else:
                    if isinstance(binding, types.MethodType):
                        result = binding(result)
                    logger.debug('response: {}'.format(result))
                    break
            else:
                logger.warning('内容获取失败！')
                logger.error(', '.join(error_msg))
            return result
        return inner
    return outer


def log_parse(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        logger.info('total time is {:.3f}s'.format(end_time-start_time))
        return result
    return inner


# def log_url(func):
#     @wraps(func)
#     def inner(*args, **kwargs):
#         result = func(*args, **kwargs)
#         logger.info('url: {}'.format(result))
#         return result
#     return inner


def log_params(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info('params: {}'.format(result))
        return result
    return inner


def log_cookies(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info('cookies: {}'.format(result))
        return result
    return inner
