# coding: utf-8
import requests
import json
class Mao_Yan(object):

    def __init__(self):
        self.pingtai = 'mao_yan'
        # self.logger.setLevel(20)

    def __connect_retry(self, method: str, url: str, headers: dict, data: dict = None, params: dict = None, allow_redirects=True, timeout=7, retry=5, proxies=False):
        connect_num = 1
        resp = None
        if proxies is None:
            proxies = None
            # todo
            # proxies = my_proxy.get_auto_proxy()
        while connect_num <= retry:
            try:
                resp = requests.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=allow_redirects)
                break
            except requests.exceptions.ConnectTimeout:
                __message = f'{url}, 连接超时, 第{connect_num}次重试'
                # self.logger.fatal(__message)
                connect_num += 1
            except requests.exceptions.ProxyError:
                __message = f'{url}, 代理获取失败, 第{connect_num}次重试'
                # self.logger.fatal(__message)
                connect_num += 1
        # self.logger.debug(f'resp: {resp}')
        if not resp:
            __message = f'url: {url}, 请求失败, 原因：服务器拒绝返回数据'
            # self.logger.fatal(__message)
            raise requests.ConnectionError(__message)

        status_code = resp.status_code
        if status_code != 200:
            __message = f'url: {url}, 请求失败，原因：status_code={status_code}'
            # self.logger.fatal(__message)
            raise requests.HTTPError(__message)

        return resp

    @staticmethod
    def format_headers(_str, split='\n'):
        _str = _str.replace("''", '').replace('""', '')
        _dict = dict()
        _list = list(map(lambda x: x.strip(), filter(lambda x: x, _str.split(split))))
        for item in _list:
            if item:
                key, value = item.strip(',').split(':', 1)

                _dict[key.strip()] = str(value).strip()
        return _dict

    def _get_cities(self):
        city_url = 'http://m.maoyan.com/dianying/cities.json'
        city_headers = {
            'Accept'    : 'application/json, text/javascript, */*; q=0.01',
            'Referer'   : 'http://m.maoyan.com/',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }
        resp_dict = self.__connect_retry('get', url=city_url, headers=city_headers).json()
        return resp_dict['cts']

    def get_movies(self):
        movie_url = 'http://m.maoyan.com/ajax/movieOnInfoList?token='
        movie_headers = {
            'Accept'    : 'application/json, text/javascript, */*; q=0.01',
            'Referer'   : 'http://m.maoyan.com/',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }
        resp_dict = self.__connect_retry('get', url=movie_url, headers=movie_headers).json()
        return resp_dict
if __name__ == '__main__':
    my = Mao_Yan()
    print(json.dumps(my.get_movies()))
    print(json.dumps(my._get_cities()))