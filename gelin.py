# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : gelin.py
# @Time    : 2019/4/9 19:20
# @Version : Python 3.6.8
import requests


class GeLin(object):
    def __init__(self, hotel_id, check_in, check_out):
        self._hotel_id = hotel_id
        self._check_in = check_in
        self._check_out = check_out
        self.headers = {
            'Origin': 'https://i.998.com',
            'Referer': 'https://i.998.com/search/homeList',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36'
        }
        self.url = 'https://i.998.com/apis/Hotel/GetRoomTypeList'
        self.data = {
            'hotelCode': self._hotel_id,
            'startDate': self._check_in,
            'endDate': self._check_out
        }
        self.all_price = list()

    def run(self):
        resp_dict = requests.post(self.url, headers=self.headers, data=self.data).json()
        if not resp_dict['Result']:
            raise ValueError('DATA ERROR')
        room_data = resp_dict['Data'][0]
        self.all_price.extend(list(filter(lambda x: x, [each['Price'] for room in room_data for each in room['ActivityList']])))
        price = sorted(self.all_price)[0]
        print(price)
        # print(json.dumps(resp_dict, ensure_ascii=False))


if __name__ == '__main__':
    gl = GeLin('003782', '2019-04-10', '2019-04-11')
    gl.run()
