# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : meituan.py
# @Time    : 2019/4/13 16:00
# @Version : Python 3.6.8
import time
import requests
import zlib
import json


class MeiTuan(object):
    def __init__(self, hotel_id, check_in, check_out):
        self.__hotel_id = hotel_id
        self.__check_in = self.__date2time(check_in)
        self.__check_out = self.__date2time(check_out)
        self._url = f'https://i.meituan.com/awp/h5/hotel/poi/deal.html?poiId={self.__hotel_id}&startTime={self.__check_in}&endTime={self.__check_out}&type=1&zlFlag=true'
        self._hotel_url = f'https://ihotel.meituan.com/group/v1/yf/list/{self.__hotel_id}'
        self.replaced_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        self.__session = requests.session()
        self.first_time = None

    @staticmethod
    def __date2time(date):
        return int(time.mktime(time.strptime(date, '%Y-%m-%d')) + 8 * 60 * 60) * 1000

    def __decrypt_js(self):
        sign_params = {
            "roomCount": "",
            "start": self.__check_in,
            "end": self.__check_out,
            "type": "1",
            "poi": self.__hotel_id,
            "uuid": "8a0f50abae8c49648e45.1555048840.1.0.0",
            "iuuid": "1FD78FA38FD88B4151AB1243ED30E66F306AD81A1DAB9E73E40FFB67459F7447",
            "userid": ""
        }
        token_params = {
            "rId": 100004,
            "ver": "1.0.6",
            "ts": self.first_time,
            'cts': None,
            "brVD": [1125, 2436],
            "brR": [[375, 812], [375, 812], 24, 24],
            "bI": [f"https://i.meituan.com/awp/h5/hotel/poi/deal.html?poiId={self.__hotel_id}&startTime={self.__check_in}&endTime={self.__check_out}&ct_poi=091843741529760504646511937512793132014_c0_e6301623566429729273_anull_o1_dhotelpoitagb_k1002&type=1&zlFlag=true", "https://i.meituan.com/awp/h5/hotel/poi/deal.html?session_query=1"],
            "mT": [],
            "kT": [],
            "aT": [],
            "tT": [],
            "aM": "",
            'sign': None
        }

        def get_params_str(params_dict):
            _list = list()
            sort_keys = sorted(params_dict.keys())
            for index, key in enumerate(sort_keys):
                if (key != 'token') & (key != '_token'):
                    _list.append(key + '=' + str(params_dict[key]))
            return '&'.join(_list)

        def str2deflate(params):
            _list = list(zlib.compress(bytes(json.dumps(params).replace(' ', ''), encoding='utf-8')))

            def repl(zlib_list):
                __list = list()
                flag = 0
                list_len = len(zlib_list)
                for index, element in enumerate(zlib_list):
                    flag += 1
                    if flag == 3:
                        flag = 0
                    if flag == 0:
                        __list.extend([self.replaced_str[((((zlib_list[index - 1] << 2) if index else 0) | (element >> 6)) & 0x3F)], self.replaced_str[(element & 0x3F)]])
                    elif flag == 1:
                        __list.append(self.replaced_str[(element >> 2) & 0x3F])
                    else:
                        __list.append(self.replaced_str[((((zlib_list[index - 1] << 4) if index else 0) | (element >> 4)) & 0x3F)])
                    if (index == list_len - 1) and flag > 0:
                        __list.append(self.replaced_str[((element << ((3 - flag) << 1)) & 0x3F)])
                if flag:
                    while flag < 3:
                        flag += 1
                        __list.append('=')
                return ''.join(__list)

            return repl(_list)

        token_params['sign'] = str2deflate(get_params_str(sign_params))
        token_params["cts"] = int(time.time() * 1000)
        return str2deflate(token_params)

    def run(self):
        headers = {'__skcy': 'no-signature', 'Content-Type': 'application/json; charset=utf-8',
                   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}

        self.first_time = int(time.time() * 1000)
        # just for keeping session
        _ = self.__session.request('get', self._url, headers=headers)
        params = {
            'utm_medium': 'touch',
            'version_name': '999.9',
            'platformid': '1',
            'start': self.__check_in,
            'end': self.__check_out,
            'type': '1',
            'poi': self.__hotel_id,
            'uuid': '',
            'iuuid': '',
            '_token': self.__decrypt_js()
        }
        resp_dict = self.__session.request('get', self._hotel_url, headers=headers, params=params).json()
        print(self._url)
        print(resp_dict['data']['result'][0]['averagePrice'] / 100)


if __name__ == '__main__':
    mt = MeiTuan('329335', '2019-05-14', '2019-05-17')
    mt.run()
