# -*- coding: utf-8 -*-
# @Author  : LJQ
# @Time    : 2019/5/13 9:46
# @Version : Python 3.6.8
# @Comment : 获取猫眼基础数据
import base64
import datetime
import json
import math
import os
import re
import requests
import time
from app.utils_ydf import LogManager
from concurrent.futures import ThreadPoolExecutor
# from crawlers.common.CheckData import CheckData
from crawlers.common.PlatNames import MAOYAN
from fontTools.ttLib import TTFont
from hashlib import md5
from pathlib import Path
from pymongo import UpdateOne
from utils import mongo_util
from utils.baiToGoogle import gcj02_to_bd09

# 图片尺寸
# https://p0.meituan.net/128.180/moviemachine/f7d2ad70eb79d6d9b8a197713db9b8c41711752.jpg
# https://p0.meituan.net/168.249/moviemachine/f7d2ad70eb79d6d9b8a197713db9b8c41711752.jpg
# https://p0.meituan.net/1920.1080/moviemachine/f7d2ad70eb79d6d9b8a197713db9b8c41711752.jpg
# http://p0.meituan.net/w.h/moviemachine/f7d2ad70eb79d6d9b8a197713db9b8c41711752.jpg

# 全局变量
date_str = datetime.datetime.now().strftime('%Y-%m-%d')
time_after_minutes = lambda s_time, minute_after: (datetime.datetime.strptime(f'2008-08-08 {s_time}', '%Y-%m-%d %H:%M') + datetime.timedelta(minutes=int(minute_after))).strftime("%H:%M")
price_parse = re.compile(r'([\d.]+)')
image_parse = lambda x: json.loads(re.sub(r'w\.h', '128.180', json.dumps(x, ensure_ascii=False)))
mao_yan_file_path = str(Path(__file__).parent / Path("maoyan_font.ttf"))

# 字体解码
mao_yan_decode_font = TTFont(mao_yan_file_path)
# compare with uni_font_list
# compare_uni_font_list = mao_yan_decode_font.getGlyphNames()[1:-1]
# get decode_font_dict
decode_uni_font_list = mao_yan_decode_font.getGlyphOrder()[2:]
decode_font_dict = {
    'uniE8B9': '9', 'uniEBCF': '4', 'uniF8F5': '1', 'uniF48B': '5', 'uniF509': '3',
    'uniF76D': '0', 'uniF5E5': '6', 'uniE944': '2', 'uniF732': '8', 'uniE674': '7'
}


class KeepSession(object):
    def __init__(self, show_logger, file_logger, allow_redirects=True, verify=None):
        self.__allow_redirects = allow_redirects
        self.__verify = verify
        self.session = requests.session()
        self.show_logger = show_logger
        self.file_logger = file_logger

    def request(self, method: str, url: str, headers: dict, data: dict = None, params: dict = None, timeout: int = 3, retry: int = 3, proxies=None):
        connect_num = 1
        resp = None
        while connect_num <= retry:
            try:
                resp = self.session.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=self.__allow_redirects, verify=self.__verify)
                break
            except requests.exceptions.ConnectTimeout:
                __message = f'{url}, 连接超时, 第{connect_num}次连接'
                self.file_logger.fatal(__message)
                connect_num += 1
            except requests.exceptions.ProxyError:
                __message = f'{url}, 代理获取失败, 第{connect_num}次连接'
                self.file_logger.fatal(__message)
                connect_num += 1
            except requests.RequestException as ex:
                __message = f'{url}, 第{connect_num}次连接, 失败原因: {ex}'
                self.file_logger.fatal(__message)
                connect_num += 1
        self.show_logger.debug(f'resp: {resp}')

        if not resp:
            __message = f'url: {url}, 请求失败, 原因：服务器拒绝返回数据'
            self.file_logger.fatal(__message)
            return

        status_code = resp.status_code
        if status_code != 200:
            __message = f'url: {url}, 请求失败，原因：status_code={status_code}'
            self.file_logger.fatal(__message)
            return

        return resp


def get_md5(_str: str) -> str:
    md = md5()
    md.update(_str.encode('utf8'))
    return md.hexdigest()


# 过滤标签
def label_filter(label_str: str) -> list:
    # all_label = '2D/3D/IMAX 2D/IMAX 3D/中国巨幕/全景声/ScreenX/4DX
    filter_label_list = []
    for label in label_str.split('/'):
        if label in ['3D', 'IMAX 2D', 'IMAX 3D', '中国巨幕']:
            filter_label_list.append(label)
    length = len(filter_label_list)
    filter_label_list = list(reversed(filter_label_list))
    return filter_label_list[:length] if length < 2 else filter_label_list[:2]


# 猫眼字体解码
def decode_font(resp_dict: dict, url: str, folder_name: str) -> dict:
    filename = os.path.join(folder_name, get_md5(f'{url}{time.time()}'))
    resp_str = json.dumps(resp_dict)
    has_value = re.search(r'base64,(.*?)"', resp_str)
    if has_value:
        online_ttf_base64 = has_value.group(1)
        online_base64_info = base64.b64decode(online_ttf_base64)
        with open(filename, 'wb')as f:
            f.write(online_base64_info)
        mao_yan_font = TTFont(filename)

        # compare_mao_yan_uni_font_list = mao_yan_font.getGlyphNames()[1:-1]
        mao_yan_uni_font_list = mao_yan_font.getGlyphOrder()[2:]

        for mao_yan_uni_font in mao_yan_uni_font_list:
            mao_yan_uni = mao_yan_font['glyf'][mao_yan_uni_font]
            for decode_uni_font in decode_uni_font_list:
                decode_uni = mao_yan_decode_font['glyf'][decode_uni_font]
                if decode_uni == mao_yan_uni:
                    mao_yan_uni_str = f'&#x{mao_yan_uni_font[3:].lower()};'
                    resp_str = resp_str.replace(mao_yan_uni_str, decode_font_dict[decode_uni_font])
        resp_dict = json.loads(resp_str)
    return resp_dict


# 获取猫眼所有城市
def get_cities() -> list:
    city_url = 'http://m.maoyan.com/dianying/cities.json'
    city_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://m.maoyan.com/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36'
    }
    resp = requests.request('get', url=city_url, headers=city_headers)
    if not resp:
        return []
    resp_dict = resp.json().get('cts', [])
    print(json.dumps(resp_dict, ensure_ascii=False))
    return resp_dict


# 获取猫眼基础数据
def mao_yan(city_id, city_name):
    g_city_id = city_id
    g_city_name = city_name
    g_request_client = KeepSession(logger, logger_error)

    # get all movies in city
    def __get_movies_by_city_id():

        def get_ten_movies(id_list):
            # movie_url = 'http://m.maoyan.com/ajax/moreComingList?'
            movie_url = f'http://api.maoyan.com/mmdb/movie/v2/list/info.json?ci={g_city_id}&headline=0'
            params = {
                'token': '',
                'movieIds': ', '.join(map(lambda x: str(x), id_list))
            }
            inner_resp = g_request_client.request('get', url=movie_url, headers=movie_headers, params=params)
            if inner_resp:
                inner_resp_dict = inner_resp.json().get('data', {})
                # logger.debug(inner_resp_dict)
                g_movie_list.extend(inner_resp_dict.get('movies', []))

        def movie_clean(movie_info_raw: dict) -> dict:
            current_time = int(time.time())
            return {
                'movie_id': str(movie_info_raw.get('id', '')),
                'source_movie_id': str(movie_info_raw.get('id', '')),
                'source_city_name': g_city_name,
                'source_city_id': str(g_city_id),
                'from': g_ping_tai,
                'movie_name': str(movie_info_raw.get('nm', '')),
                'dir': str(movie_info_raw.get('dir', '')),
                'star': str(movie_info_raw.get('star', '')),
                'score': movie_info_raw.get('sc') if movie_info_raw.get('sc') else None,
                'wish': int(movie_info_raw.get('wish', 0)),
                'labels': label_filter(movie_info_raw.get('ver', '')),  # 所属标签（非必须）
                'albumImg': str(movie_info_raw.get('img', '')),
                'images': [str(movie_info_raw.get('img', ''))],
                # 'cinema_ids': .__get_cinemas_by_movie_id(str(movie_info_raw.get('id', ''))),
                'createTime': current_time,
                'updateTime': current_time,
                'release_date': str(movie_info_raw.get('rt', '')),
                'status': {'3': 1, '4': 2}.get(str(movie_info_raw.get('showst', '')), 1)  # 状态：0:已下线 1:已上线在售 2:已上线预售  6:已删除 (必须)默认已上线
            }

        movie_headers = {
            'Host': 'api.maoyan.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36'
        }
        # first_movie_url = 'http://m.maoyan.com/ajax/movieOnInfoList?token='
        first_movie_url = f'http://api.maoyan.com/mmdb/movie/v5/list/hot.json?ci={g_city_id}&limit=12&token='
        resp = g_request_client.request('get', url=first_movie_url, headers=movie_headers)
        if not resp:
            return
        resp_dict = resp.json().get('data', {})
        # logger.debug(json.dumps(resp_dict, ensure_ascii=False))
        total_movie_num = int(resp_dict.get('total', 0))
        logger.warning(f'城市：{g_city_name} 城市ID：{g_city_id} 影片数量：{total_movie_num}')
        movie_id_list = resp_dict.get('movieIds', [])
        g_movie_list = resp_dict.get('hot', [])
        if total_movie_num > 12:
            the_rest_list = movie_id_list[12:]
            the_rest_num = total_movie_num - 12
            movie_map = []
            count = 0
            while count < the_rest_num:
                movie_map.append(the_rest_list[count: count + 12])
                count += 12
            thread_num = math.ceil(the_rest_num / 12)
            with ThreadPoolExecutor(max_workers=thread_num) as executor:
                executor.map(get_ten_movies, movie_map)

        g_movie_list = image_parse(g_movie_list)
        # logger.debug(json.dumps(g_movie_list, ensure_ascii=False))

        clean_movie_list = list(map(movie_clean, g_movie_list))
        # logger.info(json.dumps(clean_movie_list, ensure_ascii=False))

        # write to movie_collection
        data_list = []
        for movie_detail_info in clean_movie_list:
            data_list.append(UpdateOne({'movie_id': str(movie_detail_info['movie_id']), 'source_city_name': g_city_name}, {'$set': movie_detail_info}, upsert=True))
        maoyan_movie_collection.bulk_write(data_list, ordered=False)
        try:
            # 暂时只取前10的电影 来获取电影院
            thread_num = 10  # len(movie_id_list)
            with ThreadPoolExecutor(max_workers=thread_num) as executor:
                executor.map(__get_cinemas_by_movie_id, [str(i) for i in movie_id_list[:thread_num]])
        except:
            # Don't care which type of exception is raised
            pass

    # def __get_presell_movies():
    #     # coming_url = 'http://api.maoyan.com/mmdb/movie/v2/list/rt/order/coming.json?ci=1&limit=12&token='
    #     g_presell_movie_list = list(filter(lambda x: x.get('showst') == 4, g_movie_list))
    #     logger.info(json.dumps(g_presell_movie_list, ensure_ascii=False))

    # get all cinemas that show movie in city
    def __get_cinemas_by_movie_id(movie_id):
        # start nearly 10 threads
        # 城市电影院数量: https://m.maoyan.com/ajax/cinemaList?day=2019-09-21&offset=0&limit=2000&cityId=1

        def get_response(date: str = None, offset: str = '0') -> dict:
            current_time = int(1000 * time.time())
            cinema_url = f'http://m.maoyan.com/ajax/movie?forceUpdate={current_time}'
            cinema_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'http://m.maoyan.com',
                'Cookie': f'ci={g_city_id}; selectci=true;',
                'Referer': f'http://m.maoyan.com/cinema/movie/{movie_id}?$from=canary',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36'
            }
            data = {
                'movieId': str(movie_id),
                'day': date if date else date_str,
                'offset': offset,
                'limit': '20',
                'districtId': '-1',
                'lineId': '-1',
                'hallType': '-1',
                'brandId': '-1',
                'serviceId': '-1',
                'areaId': '-1',
                'stationId': '-1',
                'item': '',
                'updateShowDay': 'true' if date is None else 'false',
                'reqId': str(current_time),
                'cityId': str(g_city_id)
            }
            resp = g_request_client.request('post', url=cinema_url, headers=cinema_headers, data=data)
            if not resp:
                return {}
            resp_dict = resp.json()
            # logger.debug(json.dumps(resp_dict, ensure_ascii=False))

            return resp_dict

        def parse_response(date: str):
            resp_dict = get_response(date=date)
            cinema_id_list.extend(list(map(lambda x: str(x.get('id', '')), resp_dict.get('cinemas', []))))
            paging = resp_dict.get('paging')
            if paging:
                total_cinema_num = paging.get('total', 0)
                logger.warning(f'城市：{g_city_name} 城市ID：{g_city_id} 影片：{movie_id} 影院数量：{total_cinema_num}')
                thread_num = math.ceil(total_cinema_num / 20) - 1
                if thread_num > 0:
                    with ThreadPoolExecutor(max_workers=thread_num) as executor:
                        for result in executor.map(get_response, [date] * thread_num, list(range(20, total_cinema_num))[::20]):
                            # logger.debug(json.dumps(result, ensure_ascii=False))
                            cinema_id_list.extend(list(map(lambda x: str(x.get('id', '')), result.get('cinemas', []))))

        date_list = list(filter(lambda x: x, [i.get('date') for i in get_response().get('showDays', {}).get('dates', [])]))

        if date_list:
            with ThreadPoolExecutor(max_workers=len(date_list)) as executor:
                executor.map(parse_response, date_list)

    # 废弃，影片详情
    # def __get_movie_detail_info(movie_id):
    #     detail_info_url = f'http://m.maoyan.com/ajax/detailmovie?movieId={movie_id}'
    #     detail_info_headers = {
    #         'Accept': 'application/json, text/javascript, */*; q=0.01',
    #         'Host': 'm.maoyan.com',
    #         'Cookie': f'ci={g_city_id}; selectci=true;',
    #         'Referer': f'http://m.maoyan.com/cinema/movie/{movie_id}?$from=canary',
    #         'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36'
    #     }
    #     resp_dict = g_request_client.request('get', url=detail_info_url, headers=detail_info_headers).json()
    #     logger.info(json.dumps(resp_dict, ensure_ascii=False))
    # get all schedules(about 7 days and 10 movies) in one cinema
    def __get_movie_schedule_in_cinema(cinema_id):

        def schedule_clean(schedule_info_raw: dict) -> dict:
            if schedule_info_raw.get('enterShowSeat'):
                jump_url = f'http://m.maoyan.com/shows/{cinema_id}?movieId={movie_id}'
                playtime = str(schedule_info_raw.get('tm', ''))
                overtime = str(time_after_minutes(playtime, int(dur)))
                movie_price = price_parse.search(str(schedule_info_raw.get('sellPr', '')))
                price = float(movie_price.group(1)) if movie_price else None
                return {
                    'movie_id': str(movie_id),
                    'cinema_id': str(cinema_id),
                    'day': str(schedule_info_raw.get('dt', '')),
                    'time': playtime,
                    'jump_url': jump_url,
                    'playtype': str(schedule_info_raw.get('tp', '')),
                    'playhouse': str(schedule_info_raw.get('th', '')),
                    'overtime': overtime,
                    'from': g_ping_tai,
                    'source_city_name': str(g_city_name),
                    'source_city_id': str(g_city_id),
                    'cinema_name': cinema_name,
                    'cinema_address': cinema_address,
                    'cinema_lat': lat,
                    'cinema_lng': lng,
                    'price': price,
                    'createTime': int(time.time()),
                    'status': 1
                }

        # 判断cinema_id是否存在
        is_existed_cinema_id = maoyan_cinema_collection.find_one({'cinema_id': cinema_id})
        if is_existed_cinema_id:
            source_city_id_list = is_existed_cinema_id.get('source_city_id', [])
            source_city_id_list.append(g_city_id)
            source_city_name_list = is_existed_cinema_id.get('source_city_name', [])
            source_city_name_list.append(g_city_name)
            maoyan_cinema_collection.update({'cinema_id': cinema_id}, {'$set': {'source_city_id': source_city_id_list, 'source_city_name': source_city_name_list}})
            return
        schedule_url = f'http://m.maoyan.com/ajax/cinemaDetail?cinemaId={cinema_id}'
        schedule_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Host': 'm.maoyan.com',
            'Cookie': f'ci={g_city_id}; selectci=true;',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36'
        }
        resp = g_request_client.request('get', url=schedule_url, headers=schedule_headers)
        if not resp:
            return
        resp_dict = resp.json()
        # logger.debug(json.dumps(resp_dict, ensure_ascii=False))

        # parse price
        resp_dict = decode_font(resp_dict, schedule_url, folder_path)

        cinema_info_raw = resp_dict.get('cinemaData', {})
        lng, lat = gcj02_to_bd09(float(cinema_info_raw.get('lng', 0)), float(cinema_info_raw.get('lat', 0)))
        cinema_address = str(cinema_info_raw.get('addr', ''))
        cinema_name = str(cinema_info_raw.get('nm', ''))
        cinema_detail = {
            'cinema_id': str(cinema_id),
            'from': g_ping_tai,
            'source_city_name': [str(g_city_name)],
            'source_city_id': [str(g_city_id)],
            'cinema_name': cinema_name,
            'cinema_address': cinema_address,
            'cinema_lat': float(lat),
            'cinema_lng': float(lng),
        }
        logger.info(json.dumps(cinema_detail, ensure_ascii=False))

        # write to cinema_collection
        # maoyan_cinema_collection.update({'cinema_id': str(cinema_id)}, {'$set': cinema_detail}, upsert=True)
        maoyan_cinema_collection.insert(cinema_detail)

        schedule_clean_list = []
        # parse all movies in a cinema
        if 'showData' in resp_dict.keys():
            for movie in resp_dict['showData'].get('movies', []):
                dur = movie.get('dur', 0)
                movie_id = movie.get('id', '')
                show_num = movie.get('showCount')
                # logger.warning(f'城市：{g_city_name} 城市ID：{g_city_id}  影片：{movie_id} 影院：{cinema_id} 所有场次：{show_num}')
                if show_num:
                    for every_day in movie.get('shows', []):
                        schedule_clean_list.extend(list(map(schedule_clean, list(filter(lambda x: x, every_day.get('plist', []))))))

        # logger.info(json.dumps(schedule_clean_list, ensure_ascii=False))
        schedule_clean_list = list(filter(lambda x: x, schedule_clean_list))
        # write to cinema_schedule_collection
        maoyan_schedule_collection.insert_many(schedule_clean_list)

    cinema_id_list = []
    __get_movies_by_city_id()
    # __get_cinemas_by_movie_id('1254277')
    # __get_movie_detail_info(248172)
    # _get_cities()
    # __get_movie_schedule_in_cinema(8668)

    logger.info(json.dumps(cinema_id_list))
    # 电影院ID列表在此处生成
    clean_cinema_id_list = list(set(cinema_id_list))
    logger.info(json.dumps(clean_cinema_id_list))

    if clean_cinema_id_list:
        with ThreadPoolExecutor(max_workers=30) as executor:
            try:
                executor.map(__get_movie_schedule_in_cinema, clean_cinema_id_list)
            except:
                # Don't care which type of exception is raised
                pass


if __name__ == '__main__':
    # logger
    g_ping_tai = MAOYAN[0]
    logger = LogManager(g_ping_tai).get_logger_and_add_handlers(log_filename=g_ping_tai)
    logger_error = LogManager(f'{g_ping_tai}_request_error_{date_str}').get_logger_and_add_handlers(log_filename=f'{g_ping_tai}_request_error_{date_str}')

    # 数据库
    maoyan_movie_collection = mongo_util.get_clllection('movie', f'maoyan_movie{date_str}')
    maoyan_cinema_collection = mongo_util.get_clllection('movie', f'maoyan_cinema{date_str}')
    maoyan_schedule_collection = mongo_util.get_clllection('movie', f'maoyan_schedule{date_str}')

    maoyan_movie_collection.create_index([('source_city_name', 1), ('movie_id', 1)], unique=True)
    maoyan_cinema_collection.create_index([('cinema_id', 1)], unique=True)
    maoyan_schedule_collection.create_index([('cinema_id', 1), ('movie_id', 1), ('day', 1), ('time', 1)], unique=True)

    # 文件夹路径
    folder_path = str(Path(Path(__file__).absolute().root) / Path('maoyan_font_folder'))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    start_time = time.time()
    # mao_yan('1280', '阿城区')
    city_list = get_cities()
    city_id_list = [str(city_info['id']) for city_info in city_list]
    city_name_list = [str(city_info['nm']) for city_info in city_list]
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(mao_yan, city_id_list, city_name_list)

    # check data
    # check_data = CheckData()
    # check_data.check_movie_data_in_city('maoyan_movie')
    # check_data.check_cinema_data('maoyan_cinema')
    # check_data.check_movie_schedule_data_in_cinema('maoyan_schedule')
    end_time = time.time()
    print(f'total time is {int(end_time - start_time)}s')
 
