# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/28 16:34
# @Version     : Python 3.6.8
# @Description :
import json

from pymongo import UpdateOne

from app.utils_ydf.city_info_from_baidu import BaiduCoorLocation
from base.mixins import ZucheMongoMixin
from platforms.ehi.ehi_common.ehi_common import get_ehi_store
from platforms.ehi.ehi_common.ehi_constant import *
from utils.const_var import EHI_NAME


def write_ehi_shore_raw_to_mongo():
    db = ZucheMongoMixin().mongo_16_database_zuche
    ehi_store_col = db.get_collection(EHI_STORE_RAW_COL_NAME)
    ehi_city_col = db.get_collection(EHI_CITY_COL_NAME)
    for city_info in ehi_city_col.find({}, {"_id": 0, "Id": 1}):
        city_id = city_info['Id']
        store_list = get_ehi_store(city_id=city_id)
        record_list = []
        for store_info in store_list:
            record_list.append(
                UpdateOne(filter={'_id': f'ehi_{store_info.get("Id", "")}'}, update={"$set": store_info}, upsert=True)
            )
        else:
            ehi_store_col.bulk_write(record_list)


def clean_ehi_shore():
    db = ZucheMongoMixin().mongo_16_database_zuche
    ehi_store_raw_col = db.get_collection(EHI_STORE_RAW_COL_NAME)
    ehi_store_col = db.get_collection(EHI_STORE_COL_NAME)
    record_list = []
    for store_info in ehi_store_raw_col.find({}, {'_id': 0, 'CityName': 1, 'CityId': 1, 'Latitude': 1, 'Longitude': 1,
                                                  'Id': 1, 'Name': 1, 'Address': 1, 'PhoneNumber': 1, 'OpeningTime': 1,
                                                  'ClosingTime': 1}):
        store_dict = {}
        store_dict[from_] = EHI_NAME
        store_dict[s_city_name] = store_info.get('CityName', '')
        store_dict[s_city_id] = store_info.get('CityId')
        store_dict[m_city_name] = BaiduCoorLocation(store_info.get('Latitude', 0),
                                                    store_info.get('Longitude', 0)).city_name
        store_dict[m_city_id] = BaiduCoorLocation(store_info.get('Latitude', 0),
                                                  store_info.get('Longitude', 0)).city_code
        store_dict[m_district] = BaiduCoorLocation(store_info.get('Latitude', 0),
                                                   store_info.get('Longitude', 0)).district
        store_dict[s_shop_id] = store_info.get('Id')
        store_dict[s_shop_name] = store_info.get('Name', '')
        store_dict[s_shop_addr] = store_info.get('Address', '')
        store_dict[s_shop_phone] = store_info.get('PhoneNumber', '')
        store_dict[s_shop_lat] = store_info.get('Latitude')
        store_dict[s_shop_lon] = store_info.get('Longitude')
        store_dict[s_shop_optime] = f"{store_info.get('OpeningTime', '')}-{store_info.get('ClosingTime', '')}"
        record_list.append(
            UpdateOne(filter={'_id': f'ehi_{store_info.get("Id", "")}'}, update={"$set": store_dict}, upsert=True)
        )
        if record_list.__len__() > 1000:
            ehi_store_col.bulk_write(record_list)
            record_list = []
    else:
        ehi_store_col.bulk_write(record_list)


if __name__ == '__main__':
    clean_ehi_shore()
