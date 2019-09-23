# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-23 11:46
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
DEVICE_PARAMS = {
    "adblock": "0",
    "browserLanguage": "zh-CN",
    "cookieEnabled": "1",
    "custID": "133",
    "doNotTrack": "unknown",
    "flashVersion": 0,
    "javaEnabled": "0",
    "jsFonts": "8f58b1186770646318a429cb33977d8c",
    "mimeTypes": "52d67b2a5aa5e031084733d5006cc664",
    "os": "Win32",
    "platform": "WEB",
    "plugins": "d22ca0b81584fbea62237b14bd04c866",
    "scrAvailSize": "1040x1920",
    "srcScreenSize": "24xx1080x1920",
    "storeDb": "i1l1o1s1",
    "timeZone": -8,
    "touchSupport": "99115dfb07133750ba677d055874de87",
    "userAgent": USER_AGENT,
    "webSmartID": "17b91be3308dea9c9dcb97c3c8f8fdbf"
}
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


def __hash_alg(a, b, c):
    """
    12306哈希算法
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


def get_device_api():
    k = copy.copy(DEVICE_PARAMS)
    a, e = __hash_alg(k, "", "")
    a += f'\x26timestamp\x3d{int(time() * 1000)}'
    js_api = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
    js_text = requests.request(method='get', url=js_api, headers={'user-agent': USER_AGENT}).text
    part_url = re.search(r'(\?algID.*?hashCode\\x3d)', js_text).group(1).replace('\\x26', '&').replace('\\x3d', '=')
    device_api = "https://kyfw.12306.cn/otn/HttpZF/logdevice" + part_url + e + a
    return device_api


if __name__ == '__main__':
    r = get_device_api()
    print(r)
