# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/28 16:16
# @Version     : Python 3.6.8
# @Description :
from pymongo import UpdateOne

from base.mixins import ZucheMongoMixin
from platforms.ehi.ehi_common.ehi_common import get_ehi_city
from platforms.ehi.ehi_common.ehi_constant import EHI_CITY_COL_NAME


def write_ehi_city_to_mongo():
    city_list = get_ehi_city()
    record_list = []
    for city_info in city_list:
        record_list.append(
            UpdateOne(filter={'_id': f'ehi_{city_info.get("Id", "")}'}, update={"$set": city_info}, upsert=True)
        )
    else:
        ZucheMongoMixin().mongo_16_database_zuche.get_collection(EHI_CITY_COL_NAME).bulk_write(record_list)


if __name__ == '__main__':
    write_ehi_city_to_mongo()
