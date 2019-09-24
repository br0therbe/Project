# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-23 17:05
# @Version     : Python 3.6.8
# @Description :
import copy
import json
import random
import re
from _sha256 import sha256
from base64 import b64encode
from time import time

import requests

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
              "like Gecko) Chrome/75.0.3770.80 Safari/537.36")

HB_DICT = {
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


# def __hash_alg(a, b, c):
#     """
#     12306哈希算法(2019-09-23版)
#     """
#     hb = HB_DICT
#     # a = sorted(a, key=lambda x: list(x.keys())[0])
#     for key, value in a.items():
#         e = key.replace('%', '')
#         if isinstance(value, str):
#             f = value.replace('%', '')
#         elif isinstance(value, (int, float)):
#             f = str(value)
#         elif isinstance(value, list):
#             f = ','.join(value)
#         else:
#             f = value
#         if f != '':
#             c += e + f
#             if e in hb:
#                 b += '\x26' + hb[e] + '\x3d' + f
#             else:
#                 b += '\x26' + e + '\x3d' + f
#     a = c
#     c = a.__len__()
#     if a.__len__() % 2 is 0:
#         d = a[c // 2: c] + a[0: c // 2]
#     else:
#         d = a[c // 2 + 1: c] + a[c // 2] + a[0: c // 2]
#     a = b64encode(sha256(d.encode()).digest(), b'-_').decode().replace('=', '')
#     c = a[::-1]
#     c = b64encode(sha256(c.encode()).digest(), b'-_').decode().replace('=', '')
#     return b, c

def __hash_alg(a, b, c):
    """
    12306哈希算法(2019-09-24版)
    """
    hb = HB_DICT
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
            if e in hb:
                b += '\x26' + hb[e] + '\x3d' + f
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


def __fake_md5():
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))


def get_device_api():
    k = {
        "adblock": "0",
        "browserLanguage": "zh-CN",
        "cookieEnabled": "1",
        "custID": "133",
        "doNotTrack": "unknown",
        "flashVersion": 0,
        "javaEnabled": "0",
        "jsFonts": __fake_md5(),
        "mimeTypes": __fake_md5(),
        "os": "Win32",
        "platform": "WEB",
        "plugins": __fake_md5(),
        "scrAvailSize": "1040x1920",
        "srcScreenSize": "24xx1080x1920",
        "storeDb": "i1l1o1s1",
        "timeZone": -8,
        "touchSupport": __fake_md5(),
        "userAgent": USER_AGENT,
        "webSmartID": __fake_md5()
    }
    a, e = __hash_alg(k, "", "")
    a += f'\x26timestamp\x3d{int(time() * 1000)}'
    js_api = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
    js_text = requests.request(method='get', url=js_api, headers={'user-agent': USER_AGENT}).text
    part_url = re.search(r'(\?algID.*?hashCode\\x3d)', js_text).group(1).replace('\\x26', '&').replace('\\x3d', '=')
    device_api = "https://kyfw.12306.cn/otn/HttpZF/logdevice" + part_url + e + a
    return device_api


if __name__ == '__main__':
    r = __fake_md5()
    print(r)
