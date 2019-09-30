# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-30 11:47
# @Version     : Python 3.6.8
# @Description :
import random
import re
from _sha256 import sha256
from base64 import b64encode


class CreatePythonFile(object):
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
        # self._k = {
        #     "adblock": "0",
        #     "browserLanguage": "zh-CN",
        #     "cookieCode": "FGEM96UpBlDToSH204Y8pe0II5hdVVLB",
        #     "cookieEnabled": "1",
        #     "custID": "133",
        #     "doNotTrack": "unknown",
        #     "flashVersion": 0,
        #     "javaEnabled": "0",
        #     "jsFonts": "8f58b1186770646318a429cb33977d8c",
        #     "mimeTypes": "52d67b2a5aa5e031084733d5006cc664",
        #     "os": "Win32",
        #     "platform": "WEB",
        #     "plugins": "d22ca0b81584fbea62237b14bd04c866",
        #     "scrAvailSize": "1040x1920",
        #     "srcScreenSize": "24xx1080x1920",
        #     "storeDb": "i1l1o1s1",
        #     "timeZone": -8,
        #     "touchSupport": "99115dfb07133750ba677d055874de87",
        #     "userAgent": USER_AGENT,
        #     "webSmartID": "17b91be3308dea9c9dcb97c3c8f8fdbf"
        # }
        """
        """
        # self._k = {
        #     "adblock": "0",
        #     "browserLanguage": "zh-CN",
        #     "cookieEnabled": "1",
        #     "custID": "133",
        #     "doNotTrack": "unknown",
        #     "flashVersion": 0,
        #     "javaEnabled": "0",
        #     "jsFonts": self.__fake_md5(),
        #     "mimeTypes": self.__fake_md5(),
        #     "os": "Win32",
        #     "platform": "WEB",
        #     "plugins": self.__fake_md5(),
        #     "scrAvailSize": "1040x1920",
        #     "srcScreenSize": "24xx1080x1920",
        #     "storeDb": "i1l1o1s1",
        #     "timeZone": -8,
        #     "touchSupport": self.__fake_md5(),
        #     "userAgent": USER_AGENT,
        #     "webSmartID": self.__fake_md5()
        # }

        self._k = {
            "adblock": "0",
            "browserLanguage": "zh-CN",
            "cookieCode": "JGEoFKejTmpFKIFuZN64_k2Qj323lciP",
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
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "webSmartID": "292d6441a7b642d1f5ddeb32ec718e4d"
        }

    @staticmethod
    def __fake_md5() -> str:
        return ''.join(random.choice('0123456789abcdef') for _ in range(32))

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
    def find_params(statement):
        field, function = statement.split('=', 1)
        if 'SHA256' in statement:
            return field, re.search(r'SHA256\(.*?\)', statement).group(1)
        else:
            return field, re.search(r'\((.*)\)', function).group(1).split(',')

    def process_statement(self, statement, filter_list, function_dict):
        for _filter in filter_list:
            if _filter in statement:
                if _filter == 'SHA256':
                    field, params = self.find_params(statement)
                    f'{field}=self.sha256_alg(params)'
                else:
                    field, params = self.find_params(statement)
                    exec(f'{field}={function_dict[_filter].call(_filter, *params)}')

    def sha256_alg(self, a):
        return b64encode(sha256(a.encode()).digest(), b'-_').decode().replace('=', '')

    def run(self):
        return self.__join_params(self._k, "", "")