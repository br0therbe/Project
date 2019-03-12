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

        error = logging.FileHandler('error.log')
        error.setLevel(logging.ERROR)
        error.setFormatter(logging.Formatter(
            fmt='%(levelname)s:: %(asctime)s; File {filename}; %(message)s '.format(filename=filename),
            datefmt="%m/%d/%Y %H:%M:%S"))
        total = logging.FileHandler('all.log')
        total.setLevel(logging.DEBUG)
        total.setFormatter(logging.Formatter(
            fmt='%(levelname)s:: %(asctime)s; File {filename}; %(message)s '.format(filename=filename),
            datefmt="%m/%d/%Y %H:%M:%S"))

        logger.addHandler(console)
        logger.addHandler(error)
        logger.addHandler(total)
        self.queue = self.list_to_queue(urls)

    def response(self):
        pass

    def parse(self):
        pass

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


def log_response(content_type):
    if content_type not in ['content', 'json', 'text']:
        raise ValueError("Invalid content_type! content_type must be 'content' or 'json' or 'text'")
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response = ''
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
                    if content_type == 'content':
                        response = result.content
                    elif content_type == 'json':
                        response = result.json()
                    else:
                        response = result.text
                        logger.info('{}: {}'.format(content_type, response))
                        break
            else:
                logger.warning('{}内容获取失败！'.format(content_type))
                logger.error(', '.join(error_msg))
            return response
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


def log_url(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info('url: {}'.format(result))
        return result
    return inner


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


def log_func(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug('in {} is running'.format(func.__name__))
        result = func(*args, **kwargs)
        logger.debug('in {} is ending!'.format(func.__name__))
        return result
    return inner
