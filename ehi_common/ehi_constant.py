# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/27 14:43
# @Version     : Python 3.6.8
# @Description : 一嗨租车常量

# 汽车基础信息(实时价格)
m_car_id = 'm_car_id'
s_car_id = 'source_car_id'
m_car_name = 'm_car_name'
s_car_name = 's_car_name'
m_car_brand = 'm_car_brand'
s_car_brand = 's_car_brand'
m_car_level = 'm_car_level'
s_car_level = 's_car_level'
s_car_pic = 's_car_pic'
s_car_desc = 's_car_desc'
s_car_price = 's_car_price'

# 门店基础信息数据结构
from_ = 'from'
m_city_name = 'm_city_name'
m_city_id = 'm_city_id'
s_city_name = 's_city_name'
s_city_id = 's_city_id'
m_district = 'm_district'
m_shop_id = 'm_shop_id'
s_shop_id = 's_shop_id'
m_shop_name = 'm_shop_name'
s_shop_name = 's_shop_name'
m_shop_addr = 'm_shop_addr'
s_shop_addr = 's_shop_addr'
s_shop_phone = 's_shop_phone'
s_shop_lat = 's_shop_lat'
s_shop_lon = 's_shop_lon'
s_shop_optime = 's_shop_optime'

# 取还车限制天数
LIMIT_DAY = 90
# 取还车限制小时数
LIMIT_HOUR_LIST = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
# 取还车限制分钟数
LIMIT_MINUTE_LIST = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'AppIdentity': 'fxe81PZaeO$m8NB56lZS/$QDO/uzTaJgzkr$7PIt7YFQNu3eg1n$MV/vt5cHDJvzz4ZYHRZSghWTD48NScbfopH6sd0z/wAcCWfRFNZ$l/U*',
    'AppPlatform': 'Mobile',
    'Authorization': 'Bearer',
    'Connection': 'keep-alive',
    'Content-Type': 'text/plain;charset=UTF-8',
    # 'Cookie': 'ASP.NET_SessionId=ibjp5kuo2ae1nbetkg2r2x4y; _smt_uid=5d11eac7.313e2340; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216b8dfd1b8f439-05567d092b6046-2d604637-304500-16b8dfd1b909a4%22%2C%22%24device_id%22%3A%2216b8dfd1b8f439-05567d092b6046-2d604637-304500-16b8dfd1b909a4%22%2C%22props%22%3A%7B%7D%7D; alertCookie=Y; __xsptplusUT_604=1; 1010906md=UlCdyOpHdbex$MAEo2dU5lgqt5mtWG2YmVAVsKKcWhMhM4tWKCNRoJjp$J6jsGVs5dUI6UyoY4o8nKpRN2wfSAPnVj687xUfdwGOAROYoH82HZ53h8HL5y2kszQg0L3pdwFTtV81p554OG02VJQqtQ5l47HzF5W$gBJABUCuJ$b3ho5mBiS/hB44q5gaDxDMJNgWYrkWfy7NJ89KM2fHAQ**; __xsptplus604=604.3.1561540381.1561541416.10%232%7Cwww.baidu.com%7C%7C%7C%7C%23%23jwgPVDXZQp1Rep0qS1FUWOC8-SoMapVk%23',
    'ehiContent-MD5': 'd35a946c0b97abc3934c564685eab4fa',
    'Host': 'm.1hai.cn',
    'Origin': 'https://m.1hai.cn',
    'Referer': 'https://m.1hai.cn/Booking',
    'Remark': 'Unchecked',
    'Token': 'h5noAuth',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
}
EHI_IV = '-o@g*m,%0!si^fo1'
EHI_KEY = 'th!s!s@p@ssw0rd;setoae$12138!@$@'

# fxe81PZaeO$m8NB56kFY/EZdf1H9G0we3wcK0OOf8XU$keyPMfVCVrTS5v6$C9Bp
EHI_CITY_QUERY = 'Version=5220&DeviceId=&Source=Mobile&Extend='
EHI_CITY_URL = 'https://m.1hai.cn/Api/AddressInfo/CityList?query='

# Shu63tZRK$Ci5IEguHxz61MRACl2/dMkFGRPnJeSclI*
EHI_STORE_QUERY = 'cityId={city_id}&cityName='
EHI_STORE_URL = 'https://m.1hai.cn/Api/Store/List?query='

EHI_CAR_URL = 'https://m.1hai.cn/Api/Car/StoreStock/List'
EHI_CAR_DATA = {
    "OrderId": "",
    "ChannelId": "",
    "StockType": 2,
    "IsEnterpriseUse": False,
    "IsPickupService": True,
    "IsDropoffService": False,
    "PickupInfo": {
        "CityId": 77,
        "CityName": "上海",
        "Address": "",
        "StoreId": 886,
        "Time": "2019-06-27 20:00",
        "Longitude": 0,
        "Latitude": 0
    },
    "DropoffInfo": {
        "CityId": 5,
        "CityName": "北京",
        "Address": "",
        "StoreId": 881,
        "Time": "2019-06-29 20:00",
        "Longitude": 0,
        "Latitude": 0
    }
}

CAR_TYPE = {
    '全部': 0,
    '经济型': 1,
    '舒适型': 2,
    '5-15座商务': 3,
    '精英型': 4,
    '电动型': 5,
    'SUV': 6,
    '高端车': 17,
}
MATAFY_CAR_TYPE = {
    '其他': 0,
    '经济型': 1,
    '舒适型': 2,
    'SUV': 3,
    '商务型': 4,
    '豪华型': 5
}
CAR_MAP = {
    1: 1,
    2: 2,
    3: 4,
    4: 0,
    5: 0,
    6: 3,
    17: 5
}

EHI_CITY_COL_NAME = 'ehi_city'
EHI_STORE_COL_NAME = 'm_ehi_shop'
EHI_STORE_RAW_COL_NAME = 'ehi_shop_raw'
SUCCESS = 'SUCCESS'
SUCCESS_CODE = 200
FAILURE = 'FAILURE'
FAILURE_CODE = '505'
