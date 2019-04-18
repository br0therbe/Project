# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : dianping.py
# @Time    : 2019/4/18 17:57
# @Version : Python 3.6.8
import time
import math
import requests
import zlib
import json
import logging
PLATFORM = 'dian_ping'
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('all.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


class DianPing(object):
    def __init__(self, city_id):
        self.__city_id = city_id
        self._url = 'https://servicewechat.com/wx734c1ad7b3562129/115/page-frame.html'
        self.city_url = f'https://itrip.meituan.com/volga/api/v1/applet/trip/poi/info'
        self.__address_url = 'https://itrip.meituan.com/volga/api/v2/applet/trip/poi/basic/info?source=weChat_dp&client=weapp&feclient=lvyou_web&poiId={}'
        self.replaced_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        self.__session = requests.session()
        self.__ticket_info = dict()
        self.__scenic_id = None

    def __decrypt_js(self):
        sign_params = {
            "areaId": "-1",
            "buyCanUse": "-1",
            "cateId": "1",
            # remind
            "cityId": self.__city_id,
            "lat": '22.516506',
            # remind
            "limit": 20,
            "lng": "113.910372",
            "offset": "0",
            "selectedCityId": self.__city_id,
            "sort": "smart",
            "source": "weChat_dp"
        }
        token_params = {
            "rId": 100,
            "ts": self.first_time,
            'cts': None,
            "brVD": [400, 587],
            "brR": [[1080, 1585], [1080, 1585], 24, 24],
            "bI": ["packages/trip/pages/poilist/poilist",
                   "pages/index/index"],
            "mT": [],
            "kT": [],
            "aT": [],
            "tT": [],
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

    def __set_first_time(self):
        self.first_time = int(time.time() * 1000)

    def __set_headers(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Host': 'itrip.meituan.com',
            'Referer': self._url,
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }

    def __set_params(self, num=20, offset=0):
        self.params = {
            "areaId": "-1",
            'client': 'weapp',
            'feclient': 'feclient',
            "buyCanUse": "-1",
            "cateId": "1",
            # remind
            "cityId": self.__city_id,
            "lat": '22.516506',
            # remind
            "limit": num,
            "lng": "113.910372",
            "offset": offset,
            "selectedCityId": self.__city_id,
            "sort": "smart",
            "source": "weChat_dp",
            '_token': self.__decrypt_js()
        }

    def __parse(self, count):
        for index in range(1, math.ceil(count / 500) + 1):
            logger.debug(index)
            self.__set_params(500, 500 * (index - 1))
            resp = self.__session.request('get', self.city_url, headers=self.headers, params=self.params)#, proxies=self.proxies)
            url = resp.url
            resp_dict = resp.json()
            if resp_dict['code'] != 0:
                logger.error(f'{url}, error')
            elif 'data' not in resp_dict.keys():
                logger.error(f'{url}, exist data, but null')
            else:
                logger.debug(url)
                logger.debug(json.dumps(resp_dict, ensure_ascii=False))
                for scenic in resp_dict['data']['poiResults']:
                    resp_dict = scenic
                    self.__scenic_id = resp_dict['poiIdStr']
                    scenic_url = self.__address_url.format(self.__scenic_id)
                    logger.info(scenic_url)
                    addr_resp_dict = self.__session.request('get', scenic_url, headers=self.headers).json()['data']
                    self.__ticket_info['name'] = resp_dict['name']
                    self.__ticket_info['desc'] = resp_dict['cateName']
                    self.__ticket_info['phone'] = ''
                    self.__ticket_info['address'] = addr_resp_dict['address']
                    self.__ticket_info['region_id'] = ''
                    self.__ticket_info['lat'] = float(resp_dict['lat'])
                    self.__ticket_info['lng'] = float(resp_dict['lng'])
                    self.__ticket_info['status'] = resp_dict['type']
                    self.__ticket_info['open_info'] = ''
                    self.__ticket_info['images'] = []
                    self.__ticket_info['score'] = float(resp_dict['score'])
                    self.__ticket_info['sale_total'] = int(addr_resp_dict['reviewCount'])
                    self.__ticket_info['labels'] = [i['title'] for i in resp_dict['newPoiTags']]
                    self.__ticket_info['_from'] = 'dian_ping'
                    self.__ticket_info['source_spot_id'] = self.__scenic_id
                    self.__ticket_info['price'] = int(resp_dict.get('lowestPrice')) if resp_dict.get('lowestPrice') else None
                    self.__ticket_info['detai'] = ''
                    logger.info(json.dumps(self.__ticket_info, ensure_ascii=False))

    def run(self):
        self.__set_first_time()
        self.__set_headers()
        self.__set_params()
        resp = self.__session.request('get', self.city_url, headers=self.headers, params=self.params)#, proxies=self.proxies)
        url = resp.url
        resp_dict = resp.json()
        logger.debug(url)
        logger.debug(json.dumps(resp_dict, ensure_ascii=False))
        if resp_dict['code'] != 0:
            logger.error(f'{url}, error')
        elif 'data' not in resp_dict.keys():
            logger.error(f'{url}, exist data, but null')
        else:
            self.__parse(resp_dict['data']['count'])


if __name__ == '__main__':
    dp = DianPing('1')
    dp.run()
