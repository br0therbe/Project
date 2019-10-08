# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-23 17:05
# @Version     : Python 3.6.8
# @Description :
import copy
import random
import re
from _sha256 import sha256
from base64 import b64encode
import time

import execjs
import requests

from data.constants import USER_AGENT, HEADERS, SHA256JS


class DeviceApi(object):
    def __init__(self):
        self._hb = {
            "plugins": "ks0Q",
            "hasLiedResolution": "3neK",
            "online": "9vyE",
            "systemLanguage": "e6OK",
            "javaEnabled": "yD16",
            "scrWidth": "ssI5",
            "flashVersion": "dzuS",
            "jsFonts": "EOQP",
            "scrAvailHeight": "88tV",
            "browserLanguage": "q4f3",
            "scrHeight": "5Jwy",
            "browserName": "-UVA",
            "userAgent": "0aew",
            "localCode": "lEnu",
            "indexedDb": "3sw-",
            "cookieEnabled": "VPIf",
            "timeZone": "q5aJ",
            "hasLiedBrowser": "2xC5",
            "browserVersion": "d435",
            "touchSupport": "wNLf",
            "hasLiedLanguages": "j5po",
            "scrAvailSize": "TeRS",
            "userLanguage": "hLzX",
            "srcScreenSize": "tOHY",
            "cookieCode": "VySQ",
            "storeDb": "Fvje",
            "openDatabase": "V8vl",
            "appcodeName": "qT7b",
            "localStorage": "XM7l",
            "appMinorVersion": "qBVW",
            "scrAvailWidth": "E-lJ",
            "cpuClass": "Md7A",
            "os": "hAqN",
            "scrColorDepth": "qmyu",
            "mimeTypes": "jp76",
            "adblock": "FMQw",
            "sessionStorage": "HVia",
            "hasLiedOs": "ci5c",
            "historyList": "kU5z",
            "doNotTrack": "VEek",
            "webSmartID": "E3gR",
            "scrDeviceXDPI": "3jCe"
        }
        self._k = {
            "adblock": "0",
            "browserLanguage": "zh-CN",
            "cookieEnabled": "1",
            "custID": "133",
            "doNotTrack": "unknown",
            "flashVersion": 0,
            "javaEnabled": "0",
            "jsFonts": self.__fake_md5(),
            "mimeTypes": self.__fake_md5(),
            "os": "Win32",
            "platform": "WEB",
            "plugins": self.__fake_md5(),
            "scrAvailSize": "1040x1920",
            "srcScreenSize": "24xx1080x1920",
            "storeDb": "i1l1o1s1",
            "timeZone": -8,
            "touchSupport": self.__fake_md5(),
            "userAgent": USER_AGENT,
            "webSmartID": self.__fake_md5()
        }

    def __hash_alg_20190923(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-23版)
        """
        # a = sorted(a, key=lambda x: list(x.keys())[0])
        for key, value in a.items():
            e = key.replace('%', '')
            if isinstance(value, str):
                f = value.replace('%', '')
            elif isinstance(value, (int, float)):
                f = str(value)
            elif isinstance(value, list):
                f = ','.join(value)
            else:
                f = value
            if f != '':
                c += e + f
                if e in self._hb:
                    b += '\x26' + self._hb[e] + '\x3d' + f
                else:
                    b += '\x26' + e + '\x3d' + f
        a = c
        c = a.__len__()
        if a.__len__() % 2 is 0:
            d = a[c // 2: c] + a[0: c // 2]
        else:
            d = a[c // 2 + 1: c] + a[c // 2] + a[0: c // 2]
        a = b64encode(sha256(d.encode()).digest(), b'-_').decode().replace('=', '')
        c = a[::-1]
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    def __hash_alg_20190924(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-24版)
        """
        # a = sorted(a, key=lambda x: list(x.keys())[0])
        for key, value in a.items():
            e = key.replace('%', '')
            if isinstance(value, str):
                f = value.replace('%', '')
            elif isinstance(value, (int, float)):
                f = str(value)
            elif isinstance(value, list):
                f = ','.join(value)
            else:
                f = value
            if f != '':
                c += e + f
                if e in self._hb:
                    b += '\x26' + self._hb[e] + '\x3d' + f
                else:
                    b += '\x26' + e + '\x3d' + f
        d = c
        e = d.__len__()
        if e % 3 is 0:
            f = e // 3
        else:
            f = e // 3 + 1
        if 3 > e:
            a = d
        else:
            a = d[0: f]
            c = d[f: 2 * f]
            d = d[2 * f: e]
            a = c + d + a
        c = a.__len__()
        if a.__len__() % 2 is 0:
            d = a[c // 2: c] + a[0: c // 2]
        else:
            d = a[c // 2 + 1: c] + a[c // 2] + a[0: c // 2]
        a = d
        c = a.__len__()
        if c % 3 is 0:
            d = c // 3
        else:
            d = c // 3 + 1
        if 3 <= c:
            e = a[:d]
            f = a[d:2 * d]
            a = a[2 * d:c] + e + f
        c = a[::-1]
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    def __join_params(self, a, b, c) -> tuple:
        """
        拼接参数
        """
        for key, value in a.items():
            e = key.replace('%', '')
            if isinstance(value, str):
                f = value.replace('%', '')
            elif isinstance(value, (int, float)):
                f = str(value)
            elif isinstance(value, list):
                f = ','.join(value)
            else:
                f = value
            if f != '':
                c += e + f
                if e in self._hb:
                    b += '\x26' + self._hb[e] + '\x3d' + f
                else:
                    b += '\x26' + e + '\x3d' + f
        return b, c

    @staticmethod
    def __two_division_alg(c) -> str:
        """
        字符串分成两部分
        :param c: 字符串
        :return: 重新拼装的字符串
        """
        a = c
        c = a.__len__()
        if c % 2 is 0:
            d = a[c // 2: c] + a[0: c // 2]
        else:
            d = a[c // 2 + 1: c] + a[c // 2] + a[0: c // 2]
        return d

    @staticmethod
    def __three_division_alg(c, mode: int = 312) -> str:
        """
        字符串分成三部分
        :param c: 字符串
        :param mode: 三个部分相加的顺序, 如 312 即 第三部分 + 第一部分 + 第二部分
        :return: 重新拼装的字符串
        """
        a = c
        c = a.__len__()
        if c % 3 is 0:
            d = c // 3
        else:
            d = c // 3 + 1

        lst = []
        if 3 <= c:
            lst.append(a[:d])
            lst.append(a[d:2 * d])
            lst.append(a[2 * d:c])
            high = mode // 100
            middle = (mode - high * 100) // 10
            low = mode - high * 100 - middle * 10
            a = lst[high - 1] + lst[middle - 1] + lst[low - 1]
        return a

    def _hash_alg_20190925(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-25版)
        """
        a = dict(sorted(a.items(), key=lambda x: x[0]))
        b, c = self.__join_params(a, b, c)

        c = self.__two_division_alg(c)
        c = self.__three_division_alg(c, 312)
        c = self.__three_division_alg(c, 231)

        c = c[::-1]
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    def _hash_alg_20190926(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-26版)
        """
        a = dict(sorted(a.items(), key=lambda x: x[0]))
        b, c = self.__join_params(a, b, c)
        a = self.__two_division_alg(c)
        a = self.__two_division_alg(a)
        a = b64encode(sha256(a.encode()).digest(), b'-_').decode().replace('=', '')
        c = a.__len__()
        d = list(a)
        for e in range(c // 2):
            if e % 2 is 0:
                d[e], d[c - 1 - e] = d[c - 1 - e], a[e]
        a = ''.join(d)
        c = self.__two_division_alg(a)
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    @staticmethod
    def __loop_127_alg(c):
        a = c
        c = ''
        d = a.__len__()
        for e in range(d):
            f = ord(a[e])
            c = c + chr(0) if f is 127 else c + chr(f + 1)
        return c

    def _hash_alg_20190927(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-27版)
        """
        a = dict(sorted(a.items(), key=lambda x: x[0]))
        b, c = self.__join_params(a, b, c)

        a = self.__loop_127_alg(c)
        a = self.__three_division_alg(a, mode=231)
        a = b64encode(sha256(a.encode()).digest(), b'-_').decode().replace('=', '')
        a = self.__two_division_alg(a)
        c = self.__three_division_alg(a, mode=231)
        c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    def _hash_alg_20190929(self, a, b, c) -> tuple:
        """
        12306哈希算法(2019-09-29版)
        """
        a = dict(sorted(a.items(), key=lambda x: x[0]))
        b, c = self.__join_params(a, b, c)

        a = c[::-1]
        a = self.__three_division_alg(a, mode=231)
        a = self.__three_division_alg(a, mode=231)
        a = a[::-1]
        a = self.__loop_127_alg(a)
        c = b64encode(sha256(a.encode()).digest(), b'-_').decode().replace('=', '')
        return b, c

    @staticmethod
    def __fake_md5() -> str:
        return ''.join(random.choice('0123456789abcdef') for _ in range(32))

    def _hash_alg(self, js_text) -> tuple:
        """
        哈希算法不修改版
        :param js_text: 整个12306 js代码
        :return:
        """
        # 截取 hashAlg 函数
        _hash_alg_str = re.search(r'hashAlg:function(.*?return new.*?}),', js_text, re.S).group(1)
        # 找出复杂的js部分代码，并替换掉，复杂部分是固定的，使用优雅的python代码运行
        _complex_part = re.search(r'\(.*?\){(.*?\)})', _hash_alg_str, re.S).group(1)
        _replace_hash_alg_str = _hash_alg_str.replace(_complex_part, '').replace('\n', '')
        # 替换返回值为列表 而非12306前端定义的key，value数据结构
        _result_replace = re.findall(r'return (new [a-zA-Z]*\((.*?)\))', _replace_hash_alg_str)[0]
        _replace_hash_alg_str = _replace_hash_alg_str.replace(_result_replace[0], f'[{_result_replace[1]}]')
        # 将零碎的js代码拼装程函数
        hash_alg_text = f'function hashAlg{_replace_hash_alg_str}'

        # 找出sha256加密的代码
        _find_sha256_list = re.findall(r'=([a-zA-Z]*?.SHA256\((.*?)\).*?);', hash_alg_text)
        # 将js中sha256加密部分用本地sha256（此代码为js非本地python）替换
        for _find_sha256 in _find_sha256_list:
            hash_alg_text = hash_alg_text.replace(_find_sha256[0], f'sha256_digest({_find_sha256[1]})')

        # 找出hashAlg函数中调用的其他函数
        function_list = re.findall(r'(=[a-zA-Z]*\(.*?\);)', hash_alg_text)
        function_name_list = []
        # 找出函数名
        for function in function_list:
            function_name = re.search(r'=([a-zA-Z]+)', function).group(1)
            if function_name not in function_name_list:
                function_name_list.append(function_name)

        # 截取函数名所对应的代码，拼接在hashAlg函数后，形成完整的hashAlg函数块
        for function_name in function_name_list:
            function_str = re.search(f'(function {function_name}' + r'.*?return.*?})', js_text, re.S).group(1)
            # 找出函数中的sha256加密的代码
            _find_sha256_list = re.findall(r'return ([a-zA-Z]*?.SHA256\((.*?)\).*?)}', function_str)
            if _find_sha256_list:
                # 将js中sha256加密部分用本地sha256（此代码为js非本地python）替换
                for _find_sha256 in _find_sha256_list:
                    function_str = function_str.replace(_find_sha256[0], f'sha256_digest({_find_sha256[1]})')
            hash_alg_text = f"{hash_alg_text}\n{function_str}"

        # 构建可运行的12306加密js代码
        encrypt_js = f"{copy.copy(SHA256JS)}\n{hash_alg_text}"
        b, c = self.__join_params(self._k, "", "")
        return execjs.compile(encrypt_js).call('hashAlg', '', b, c)

    def get_device_api(self) -> str:
        js_api = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
        js_text = requests.request(method='get', url=js_api, headers=HEADERS).text
        a, e = self._hash_alg(js_text)
        a += f'\x26timestamp\x3d{int(time.time() * 1000)}'
        part_url = re.search(r'(\?algID.*?hashCode\\x3d)', js_text).group(1).replace('\\x26', '&').replace('\\x3d', '=')
        device_api = "https://kyfw.12306.cn/otn/HttpZF/logdevice" + part_url + e + a
        return device_api


if __name__ == '__main__':
    r = DeviceApi().get_device_api()
    print(r)
