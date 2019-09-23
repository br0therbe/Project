# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/8/15 17:46
# @Version     : Python 3.6.8
# @Description :
import json
import re
from time import time
from base64 import b64decode

import cv2
import numpy as np
import requests

from fake_decrypt_12306 import get_device_api

LOCATION_MAP = {
    '1': '37,41',
    '2': '116,50',
    '3': '186,48',
    '4': '260,50',
    '5': '46,122',
    '6': '111,120',
    '7': '183,121',
    '8': '255,123',
}
HEADERS = {
    'Host': 'kyfw.12306.cn',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.80 Safari/537.36'
}
USERNAME = ''
PASSWORD = ''


def current_time() -> int:
    return int(time() * 1000)


def current_time_str() -> str:
    return str(current_time())


class Login(object):
    """
    12306 登录
    """

    def __init__(self):
        # 会话保持
        self.session = requests.session()
        self.session.headers = HEADERS
        self._index()

    def _index(self):
        """
        请求主页,添加会话
        :return:
        """
        login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self._request_index_time = current_time()
        _ = self.session.request('get', login_url)

    def _get_captcha(self, *, image_path: str = None, is_show_image: bool = False) -> str:
        """
        获取验证码图片
        :param image_path: 验证码存储路径
        :param is_show_image: 是否展示验证码
        :return: 验证码的base64加密流
        """
        captcha_api = 'https://kyfw.12306.cn/passport/captcha/captcha-image64'
        captcha_params = {
            'login_site': 'E',
            'module': 'login',
            'rand': 'sjrand',
            current_time_str(): '',
            'callback': 'callback',
            '_': self._request_index_time
        }
        captcha_resp = self.session.request('get', captcha_api, params=captcha_params)
        captcha_resp_dict = json.loads(captcha_resp.text.replace('/**/callback(', '').replace(');', ''))
        img_bytes = b64decode(captcha_resp_dict['image'])
        img_byte_array = bytearray(img_bytes)
        if is_show_image:
            image = np.asarray(img_byte_array, dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            cv2.imshow('image_show', image)
            cv2.waitKey(15000)
        if image_path:
            # 写入验证码 md5({username}{password}).png
            with open(image_path, 'wb') as fw:
                fw.write(img_bytes)
        return img_bytes

    def _check_captcha(self, index_list: list) -> dict:
        """
        验证码校验
        :param index_list: 验证码序号列表
        :return: 验证码校验是否正确的相关信息
        """
        captcha_check_api = 'https://kyfw.12306.cn/passport/captcha/captcha-check'

        # 验证码点击的位置
        answer = ','.join([LOCATION_MAP[str(index)] for index in index_list])
        print(answer)

        captcha_check_params = {
            'callback': 'callback',
            'answer': answer,
            'rand': 'sjrand',
            'login_site': 'E',
            '_': self._request_index_time
        }

        # 查看是否验证成功
        resp_str = self.session.request('get', captcha_check_api, params=captcha_check_params).text
        resp_dict = json.loads(resp_str.replace('/**/callback({', '{').replace('});', '}'))
        print(resp_dict)
        return resp_dict

    def _login(self) -> dict:
        """
        请求登录接口
        :return: 是否登陆成功的相关信息
        """
        login_api = 'https://kyfw.12306.cn/passport/web/login'
        login_data = {
            'username': self._username,
            'password': self._password,
            'appid': 'otn'
        }
        resp_dict = self.session.request('post', login_api, data=login_data).json()
        print(resp_dict)
        return resp_dict

    def _check_login_first(self) -> dict:
        uamtk_api = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        resp_dict = self.session.request('post', uamtk_api, data={'appid': 'otn'}).json()
        print(resp_dict)
        return resp_dict

    def _check_login_second(self, tk: str) -> dict:
        uamauthclient_api = 'https://kyfw.12306.cn/otn/uamauthclient'
        resp_dict = self.session.request('post', uamauthclient_api, data={'tk': tk}).json()
        print(resp_dict)
        return resp_dict

    def __set_device_cookie(self):
        device_api = get_device_api()
        resp_str = self.session.request('get', url=device_api).text
        rail_expiration = re.search('"exp":"(.+?)"', resp_str).group(1)
        rail_deviceid = re.search('"dfp":"(.+?)"', resp_str).group(1)
        self.session.cookies.set("RAIL_EXPIRATION", rail_expiration)
        self.session.cookies.set("RAIL_DEVICEID", rail_deviceid)

    def login(self, username: str, password: str):
        """
        12306 登录
        :param username: 12306 账号
        :param password: 12306 密码
        :return:
        """
        self._username = username
        self._password = password
        self.__set_device_cookie()

        # 获取验证码
        img_path = f'{username}.png'
        self._get_captcha(image_path=img_path)

        # 验证码校验
        index_str = input('请输入验证码位置: ')
        msg = self._check_captcha(index_str.split())
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != '4' or result_message != '验证码校验成功':
            return {
                'code': 503,
                'data': result_message,
                'message': 'Failure'
            }

        # 登录
        _ = self._login()

        # 第一次检查登录状态
        msg = self._check_login_first()
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != 0 or result_message != '验证通过':
            return {
                'code': 503,
                'data': result_message,
                'message': 'Failure'
            }

        # 第二次检查登录状态
        tk = msg.get('newapptk')
        msg = self._check_login_second(tk)
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != 0 or result_message != '验证通过':
            return {
                'code': 503,
                'data': result_message,
                'message': 'Failure'
            }

        print(self.session.cookies)


if __name__ == '__main__':
    # print(json.dumps(login_by_self.session(username, password), ensure_ascii=False))
    Login().login(USERNAME, PASSWORD)
