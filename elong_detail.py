# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : elong_detail.py
# @Time    : 2019/4/4 14:33
# @Version : Python 3.6.8
import json
import re
import js2py
import requests
from time import time
from lxml import html


# noinspection PyPep8
class ElongH5In2Querier(object):

    def __init__(self, hotel_id, check_in, check_out, adult_num, child_str):
        self._hotel_id = hotel_id
        self._check_in = check_in
        self._check_out = check_out
        self._adult_num = adult_num
        self._child_str = child_str
        self._platfrom = '艺龙国际抓取'
        self.session = requests.session()
        self._headers = {
            'Connection': 'keep-alive',
            'Host': 'm.elong.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36',
        }
        self._code = None
        self.total_price = None
        self.tax = None

    # noinspection PyAttributeOutsideInit
    def run(self):
        self.get_code()
        if self._child_str:
            price_url = f'http://m.elong.com/ihotel/detail/DetailRoomListNew/?hotelId={self._hotel_id}&inDate={self._check_in}&checkOutDate={self._check_out}&roomPerson=1|{self._adult_num}:{self._child_str}&code={self._code}'
        else:
            price_url = f'http://m.elong.com/ihotel/detail/DetailRoomListNew/?hotelId={self._hotel_id}&inDate={self._check_in}&checkOutDate={self._check_out}&roomPerson=1|{self._adult_num}&code={self._code}'
        resp_dict = self.session.request('get', url=price_url, headers=self._headers).json()
        err_nos = {'-1': "酒店无房"}
        self.session.close()
        err_code = resp_dict['errno']
        if err_code:
            raise ValueError(err_nos[err_code])
        self.total_price = resp_dict['data']['lowestTotalPrice']
        self.tax = float(re.search(r'"otherTaxesAvg":(.*?)[\},]', json.dumps(resp_dict, ensure_ascii=False)).group(1))
        print(self.total_price)
        print(self.tax)

    def get_code(self):
        # 获取艺龙JavaScript加密参数code值，无code值会返回错误数据
        if self._child_str:
            detail_url = f'http://m.elong.com/ihotel/{self._hotel_id}/?inDate={self._check_in}&outDate={self._check_out}&roomPerson=1|{self._adult_num}:{self._child_str}'
        else:
            detail_url = f'http://m.elong.com/ihotel/{self._hotel_id}/?inDate={self._check_in}&outDate={self._check_out}&roomPerson=1|{self._adult_num}'
        print(detail_url)
        resp = self.session.request('get', url=detail_url, headers=self._headers)
        root = html.fromstring(resp.text)
        value = repr(root.xpath('//*[@id="tsdDetail"]/@value')[0])
        elong_js = '''function abcdefgDetail() {\n    try {\n        var a = JS;\n\n        if (null == a || a == \'\' || a == \'${tsdDetail}\') {\n            return -99\n        }\n        ;var b = hijklmn(a);\n        var c = eval(b);\n        return c\n    } catch (e) {\n        return -99\n    }\n}\n;function hijklmn(a) {\n    if (null == a || a == \'\') {\n        return a\n    }\n    ;var b = a.replace(/\\)\\^-1/gm, ")&-1");\n    return b\n};\n  abcdefgDetail();'''
        # noinspection PyAttributeOutsideInit
        self._code = js2py.eval_js(elong_js.replace("JS", value))


if __name__ == '__main__':
    start_time = time()
    args = [282978, '2019-04-11', '2019-04-12', 2]
    # print(detail_task(*args))
    ElongH5In2Querier('303116', '2019-04-15', '2019-04-16', 2, '').run()
    end_time = time()
    print('total time is {:.3f}s'.format(end_time - start_time))
