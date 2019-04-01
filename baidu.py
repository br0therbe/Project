# -*- encoding: utf-8 -*-
"""
@File    : baidu.py
@Time    : 2019/3/11 18:20
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
from spiders import *
import requests
import logging


class BaiDu(Spiders):
    def __init__(self, urls, level=logging.DEBUG):
        super().__init__(urls=urls, level=level, filename=os.path.basename(__file__))
        self.url = self.set_url()
        self.headers = self.set_headers()

    @log_func
    @log_url
    def set_url(self):
        return self.queue.get_nowait()

    @log_func
    @log_response(content_type='text')
    def response(self):
        response = requests.get(self.url, self.headers, timeout=1)
        return response

    @log_func
    @log_parse
    def parse(self):
        response = self.response()
        return response


if __name__ == '__main__':
    urls = ['https://www.baidu.com']
    bd = BaiDu(urls)
    bd.parse()
pass
