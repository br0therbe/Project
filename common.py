# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : common.py
# @Time    : 2019/4/10 10:01
# @Version : Python 3.6.8
# coding: utf-8
from hashlib import md5
from functools import wraps
from queue import Queue
from time import time
import base64
import requests

def base64_encode(_byte):
    _byte = bytes(_byte, encoding='utf-8')
    return base64.b64encode(_byte).decode('utf-8')


def base64_decode(_byte):
    _byte = bytes(_byte, encoding='utf-8')
    return base64.b64decode(_byte).decode('utf-8')


def cost(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print('total time is {:.3f}s'.format(end_time - start_time))
        return result

    return inner


def format_headers(_str, split='\n'):
    _str = _str.replace("''", '').replace('""', '')
    _dict = dict()
    _list = list(map(lambda x: x.strip(), filter(lambda x: x, _str.split(split))))
    for item in _list:
        if item:
            key, value = item.strip(',').split(':', 1)

            _dict[key.strip()] = str(value).strip()
    return _dict


def get_md5(_str):
    md = md5()
    md.update(_str.encode('utf8'))
    return md.hexdigest()


def list_to_queue(urls):
    queue = Queue()
    for url in urls:
        queue.put_nowait(url)
    return queue

def __connect_retry(self, method: str, url: str, headers: dict, data: dict = None, params: dict = None, allow_redirects=True, timeout=7, retry=5, proxies=False):
    connect_num = 1
    resp = None
    if proxies == None:
        proxies = my_proxy.get_auto_proxy()
    while connect_num <= retry:
        try:
            resp = requests.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=allow_redirects)
            break
        except requests.exceptions.ConnectTimeout:
            __message = f'{url}, 连接超时, 第{connect_num}次重试'
            self.logger.fatal(__message)
            connect_num += 1
        except requests.exceptions.ProxyError:
            __message = f'{url}, 代理获取失败, 第{connect_num}次重试'
            self.logger.fatal(__message)
            connect_num += 1
    self.logger.debug(f'resp: {resp}')
    if not resp:
        __message = f'url: {url}, 请求失败, 原因：服务器拒绝返回数据'
        self.logger.fatal(__message)
        raise requests.ConnectionError(__message)

    status_code = resp.status_code
    if status_code != 200:
        __message = f'url: {url}, 请求失败，原因：status_code={status_code}'
        self.logger.fatal(__message)
        raise requests.HTTPError(__message)

    return resp
# def tesseract_recognize(path):
#     # tesseract = 'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
#     for file in os.listdir(path):
#         text = pytesseract.image_to_string(
#             Image.open(os.path.join(path, file)))
#         print('{} is {}'.format(file, text))
#         # return file, text

if __name__ == '__main__':
    pass
