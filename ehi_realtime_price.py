# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/27 14:38
# @Version     : Python 3.6.8
# @Description :
import json

from platforms.ehi.ehi_common.ehi_common import get_ehi_car
from platforms.ehi.ehi_common.ehi_constant import *


def get_ehi_realtime_price_by_city_id(s_city_id, s_shop_id, start_time, end_time, other_infos):
    # 只做清洗
    car_list = []
    car_info_list = get_ehi_car(s_city_id, s_shop_id, start_time, end_time, other_infos)
    if car_info_list == FAILURE:
        return {'code': FAILURE_CODE, 'data': [], 'msg': FAILURE}
    for car in car_info_list:
        car_dict = {}
        # car_dict[m_car_id] = ''
        car_dict[s_car_id] = car.get('GroupItem', {}).get('Id', 0)
        # car_dict[m_car_name] = ''
        car_dict[s_car_name] = car.get('GroupItem', {}).get('Name', '')
        # car_dict[m_car_brand] = ''
        # car_dict[s_car_brand] = car.get('CarTypeItem', {}).get('BrandName', '')
        car_dict[m_car_level] = CAR_MAP.get(car.get('CommonItem', {}).get('LevelId', 0), 0)
        car_dict[s_car_level] = car.get('CommonItem', {}).get('LevelId', 0)
        car_dict[s_car_pic] = car.get('GroupItem', {}).get('ImgPath', '')
        car_dict[s_car_desc] = car.get('GroupItem', {}).get('Description', '')
        car_dict[s_car_price] = car.get('FloorPrice', 0)
        car_list.append(car_dict)

    # print(json.dumps(car_list))
    return {'code': SUCCESS_CODE, 'data': car_list, 'msg': SUCCESS}


if __name__ == '__main__':
    pui = {
        "city_id": 21,
        "city_name": "深圳",
        "Address": "",
        "store_id": 3360,
        "time": "2019-06-27 21:00",
        "Longitude": 0,
        "Latitude": 0
    }
    doi = {
        "city_id": 21,
        "city_name": "深圳",
        "Address": "",
        "store_id": 3360,
        "time": "2019-06-29 21:00",
        "Longitude": 0,
        "Latitude": 0
    }
    print(json.dumps(get_ehi_realtime_price_by_city_id(21, 3360, '2019-06-27 21:00', '2019-06-29 21:00', {'city_name': '深圳'})))
