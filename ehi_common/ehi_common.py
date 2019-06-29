# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/27 14:43
# @Version     : Python 3.6.8
# @Description : 一嗨租车通用方法
import base64
import copy
import json
from _md5 import md5

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from platforms.ehi.ehi_common.ehi_constant import *
from app.utils_ydf import RequestClient


def aes256_encode(plaintext: str) -> str:
    iv = EHI_IV.encode('utf-8')
    key = EHI_KEY.encode('utf-8')
    aes = AES.new(key=key, mode=AES.MODE_CFB, iv=iv, segment_size=128)
    pad_pkcs7 = pad(plaintext.encode('utf-8'), AES.block_size, style='pkcs7')
    cipher_byte = aes.encrypt(pad_pkcs7)
    cipher_text = base64.b64encode(cipher_byte).decode('utf-8')
    return cipher_text


def aes256_decode(cipher_text: str) -> str:
    iv = EHI_IV.encode('utf-8')
    key = EHI_KEY.encode('utf-8')
    cipher_byte = base64.b64decode(cipher_text)
    aes = AES.new(key=key, mode=AES.MODE_CFB, iv=iv, segment_size=128)
    pad_pkcs7 = aes.decrypt(cipher_byte)
    plaintext = unpad(pad_pkcs7, AES.block_size, style='pkcs7').decode('utf-8')
    return plaintext


def generate_md5(plaintext: str) -> str:
    return md5(plaintext.encode('utf-8')).hexdigest()


def get_ehi_md5(*, params: str, data: str) -> str:
    if params and data:
        plaintext = f'{EHI_IV}{params}{data}'
    elif params:
        plaintext = f'{EHI_IV}{params}'
    elif data:
        plaintext = f'{EHI_IV}{data}'
    else:
        plaintext = EHI_IV

    return generate_md5(plaintext)


def get_ehi_city() -> list:
    HEADERS['ehiContent-MD5'] = get_ehi_md5(params=EHI_CITY_QUERY, data='')
    query = aes256_encode(EHI_CITY_QUERY).replace('+', '$').replace('=', '*')
    resp_dict = RequestClient().request('get', url=f'{EHI_CITY_URL}{query}', headers=HEADERS).json()
    return resp_dict.get('Result') or []


def get_ehi_store(city_id: int) -> list:
    params = EHI_STORE_QUERY.format(city_id=city_id)
    HEADERS['ehiContent-MD5'] = get_ehi_md5(params=params, data='')
    query = aes256_encode(params).replace('+', '$').replace('=', '*')
    resp_dict = RequestClient().request('get', url=f'{EHI_STORE_URL}{query}', headers=HEADERS).json()
    return resp_dict.get('Result') or []


def get_ehi_car(s_city_id, s_shop_id, start_time, end_time, other_infos) -> list:
    """
    data 参数格式如下：
    {
        "OrderId":"",
        "ChannelId":"",
        "StockType":2,
        "IsEnterpriseUse":false,
        "IsPickupService":true,
        "IsDropoffService":false,
        "PickupInfo":{
            "CityId":77,
            "CityName":"上海",
            "Address":"",
            "StoreId":886,
            "Time":"2019-06-27 20:00",
            "Longitude":0,
            "Latitude":0
        },
        "DropoffInfo":{
            "CityId":5,
            "CityName":"北京",
            "Address":"",
            "StoreId":881,
            "Time":"2019-06-29 20:00",
            "Longitude":0,
            "Latitude":0
        }
    }
    """
    data = copy.deepcopy(EHI_CAR_DATA)
    data['StockType'] = 1
    data['PickupInfo']['CityId'] = s_city_id
    data['PickupInfo']['CityName'] = other_infos['city_name']
    data['PickupInfo']['StoreId'] = s_shop_id
    data['PickupInfo']['Time'] = start_time

    data['DropoffInfo']['CityId'] = s_city_id
    data['DropoffInfo']['CityName'] = other_infos['city_name']
    data['DropoffInfo']['StoreId'] = s_shop_id
    data['DropoffInfo']['Time'] = end_time
    serialize_data = json.dumps(data, separators=(',', ':'))
    HEADERS['ehiContent-MD5'] = get_ehi_md5(params='', data=serialize_data)
    try:
        query = aes256_encode(serialize_data).replace('+', '$').replace('=', '*')
    except:
        return FAILURE

    resp_dict = RequestClient().request('post', url=EHI_CAR_URL, headers=HEADERS, data=query).json()
    return resp_dict.get('Result', {}).get('StockPriceList') or []


def web_aes256_encrypt(plain_text: str) -> str:
    web_url = 'https://tool.lami.fun/jiami/crypt128inter'
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://tool.lami.fun',
        'referer': 'https://tool.lami.fun/jiami/aes',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    data = {
        'mode': 'CFB',
        'padding': 'pkcs7',
        'block': '256',
        'password': EHI_KEY,
        'iv': EHI_IV,
        'encode': 'base64',
        'way': '1',
        'text': plain_text,
        'method': 'aes'
    }
    resp_str = RequestClient(request_retry_times=2).request(
        'post', url=web_url, headers=headers, data=data).json().get('d', {}).get('r', '')
    return resp_str

