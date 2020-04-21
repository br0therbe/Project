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

def __connect_retry(self, method: str, url: str, headers: dict, data: dict = None, params: dict = None, allow_redirects=True, timeout=7, retry=5, proxies=False, verify=None):
    connect_num = 1
    resp = None
    if proxies is None:
        proxies = my_proxy.get_auto_proxy()
    while connect_num <= retry:
        try:
            resp = requests.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=allow_redirects, verify=verify)
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

class KeepSession(LoggerMixin):
    def __init__(self, allow_redirects=True, verify=None):
        self.__allow_redirects = allow_redirects
        self.__verify = verify
        self.session = requests.session()

    def request(self, method: str, url: str, headers: dict, data: dict = None, params: dict = None, timeout=5, retry=3, proxies=None):
        connect_num = 1
        resp = None
        while connect_num <= retry:
            try:
                resp = self.session.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=self.__allow_redirects, verify=self.__verify)
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

class FunctionResultCache(object):
    cache_dict = {}
    __lock = threading.Lock()

    @classmethod
    def some_time(cls, cache_time: float):

        def _some_time(func):
            @wraps(func)
            def __some_time(*args, **kwargs):
                key = cls._make_key(func, args, kwargs)
                if key in cls.cache_dict and time.time() - cls.cache_dict[key][1] < cache_time:
                    return cls.cache_dict[key][0]
                else:
                    with cls.__lock:
                        if key in cls.cache_dict and time.time() - cls.cache_dict[key][1] < cache_time:
                            return cls.cache_dict[key][0]
                        else:
                            result = func(*args, **kwargs)
                            cls.cache_dict[key] = result, time.time()
                            return result

            return __some_time

        return _some_time

    @staticmethod
    def _make_key(func, args: tuple, kwargs: dict) -> int:
        key = (func,) + args
        defaults = func.__kwdefaults__
        if defaults:
            kwargs = {**defaults, **kwargs}

        for item in sorted(kwargs.items(), key=lambda x: x[0]):
            key += item
        return hash(key)

    
    
    
headers = {"Content-Type": "application/json; charset=utf-8"}
at = ['phone']

def dingtalk(*, title: str, message: str, image_url: str = None):
    """
    钉钉通知重要消息
    :param title: 标题
    :param message: 消息体
    :param image_url: 图片链接
    :return:
    """
    timestamp = int(time.time() * 1000)
    str_to_sign = f'{timestamp}\n{secret}'
    sign = quote(b64encode(hmac.new(secret.encode('utf-8'), str_to_sign.encode('utf-8'), digestmod=sha256).digest()))
    api = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    message = message.strip().replace('\n', '\n> ##### ')
    real_title = f'{title}'
    if image_url is not None:
        message += f'\n> ![screenshot]({image_url})'
    markdown_data = {
        "msgtype": "markdown",
        "markdown": {
            "title": real_title,
            "text": f"## {real_title} @{'@'.join(at)}\n> ##### {message}\n"
        },
        "at": {
            "atMobiles": at,
            "isAtAll": False
        }
    }
    try:
        resp_str = requests.request(method='post', url=api, json=markdown_data, headers=headers).text
        logger.info(f'钉钉发送成功：{resp_str}')
    except Exception as e:
        logger.exception(f'钉钉发送失败，原因：{e}')

if __name__ == '__main__':
    pass
