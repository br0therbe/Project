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
    _dict = dict()
    _list = list(map(lambda x: x.strip(), filter(lambda x: x, _str.split(split))))
    for item in _list:
        key, value = item.split(':', 1)
        _dict[key.strip()] = value
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


# def tesseract_recognize(path):
#     # tesseract = 'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
#     for file in os.listdir(path):
#         text = pytesseract.image_to_string(
#             Image.open(os.path.join(path, file)))
#         print('{} is {}'.format(file, text))
#         # return file, text

if __name__ == '__main__':
    pass
