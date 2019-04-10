# -*- coding: utf-8 -*-
# @Author  : ljq
# @File    : wv.py
# @Time    : 2019/4/10 15:06
# @Version : Python 3.6.8
import requests
import json


class WV(object):
    def __init__(self, vid, platform='4810701'):
        """
        从网页微视获取短视频，链接https://xw.qq.com/m/shortvideo
        :param vid: 短视频id
        :param platform: 平台id， 默认4810701，不知道平台id的话不要改
        """
        self.vid = vid
        # self.wv_url = 'https://xw.qq.com/m/shortvideo'
        self.home_url = f'https://xw.qq.com/a/video/{vid}'
        self.info_url = 'https://h5vv.video.qq.com/getinfo'
        self.url_list = list()
        self.params = {
            'otype': 'json',
            'platform': platform,
            'host': 'xw.qq.com',
            'ehost': f'https://xw.qq.com/a/video/{vid}',
            'refer': 'xw.qq.com',
            'vid': vid,
            'show1080p': 'false'
        }
        self.headers = {
            'Referer': f'https://xw.qq.com/a/video/{vid}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Mobile Safari/537.36'
        }

    def parse_url(self):
        resp_str = requests.get(self.info_url, params=self.params, headers=self.headers).text.replace('QZOutputJson=', '').replace('}};', '}}')
        resp_dict = json.loads(resp_str)
        video_dict = resp_dict['vl']['vi'][0]

        url_list = [url['url'] for url in video_dict['ul']['ui']]
        filename = video_dict['fn']
        vkey = video_dict['fvkey']

        self.url_list = [f'{url}{filename}?vkey={vkey}' for url in url_list]

    def write_video(self):
        headers = {
            'Range': 'bytes=0-',
            'Referer': f'https://xw.qq.com/a/shortvideo/{self.vid}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Mobile Safari/537.36'
        }
        # 寻找可用的短视频链接，并下载短视频
        for url in self.url_list:
            try:
                resp_bytes = requests.get(url, headers=headers).content
            except:
                continue
            finally:
                with open(f'{self.vid}.mp4', 'wb') as f:
                    f.write(resp_bytes)
                break


class ListPageWV(object):
    def __init__(self):
        self.url = 'https://pacaio.match.qq.com/irs/index'
        self.headers = {
            'Referer': 'https://xw.qq.com/m/shortvideo',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        self.vid_list = list()

    def parse(self, page):
        params = {'idx1': 'irs:minivideo:index:hot', 'idx2': 'cat.all', 'flag': 'video', 'page': page, 'num': '30'}
        resp_dict = requests.get(self.url, params=params, headers=self.headers).json()
        if resp_dict['code']:
            raise ValueError('DATA ERROR')
        self.vid_list.extend([data['id'] for data in resp_dict['data']])


if __name__ == '__main__':
    lpwv = ListPageWV()
    for i in [0, 1, 2]:
        lpwv.parse(i)

    for vid in lpwv.vid_list:
        wv = WV(vid, '4810701')
        wv.parse_url()
        wv.write_video()
