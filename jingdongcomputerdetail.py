# -*- encoding: utf-8 -*-
"""
@File    : jingdongcomputerdetail.py
@Time    : 2019/3/13 14:04
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
from gevent import monkey; monkey.patch_all()
from lxml import html
from spiders import *
import gevent
import json
import logging
import re
import requests


class JingDongComputerDetail(Spiders):
    def __init__(self, urls, origins, level=logging.INFO):
        super().__init__(urls=urls, level=level, filename=os.path.basename(__file__))
        self.queue_origin = self.list_to_queue(origins)
        # function filter_blank is to filter the blank elements in the array and leave non-blank elements
        self.filter_blank = lambda y: list(filter(lambda x: x.strip(), y))
        # function cut_blank is to cut the blank in elements of the array
        self.cut_blank = lambda y: list(map(lambda x: x.strip(), y))

    @log_func
    def set_headers(self, url, origin):
        ua = UserAgent().random
        headers_detail = {
            'authority': 'item.jd.com',
            'method': 'GET',
            'path': url.replace('https://item.jd.com', ''),
            'scheme': 'https',
            'referer': origin,
            'user-agent': ua
        }
        headers_interface = {
            'Referer': url,
            'User-Agent': ua
        }
        return {
            'headers_detail': headers_detail,
            'headers_interface': headers_interface
        }

    def response(self):
        while not self.queue.empty():
            url = self.set_url()
            origin = self.queue_origin.get_nowait()
            headers = self.set_headers(url, origin)
            headers_detail = headers['headers_detail']
            headers_interface = headers['headers_interface']

            @log_func
            def response_list():
                response = requests.get(url, headers_detail).text
                page_config = re.findall(r'var pageConfig = (.+?});', response, re.S)[0]
                if len(page_config) < 100:
                    return url + '页面错误！网站原因！'
                add_double_quotes = re.sub(r'(?P<word>[\w ]+):', lambda x: '"{}":'.format(x.group('word')), page_config)
                cut_blank = re.sub(r'\s+', '', add_double_quotes).replace('/**//**/', '')
                replace_word = cut_blank.replace('true', '"true"').replace('false', '"false"').replace("'", '"')
                dict_parameters = json.loads(replace_word)
                params = {
                    'cat': ','.join(list(map(lambda x: str(x), dict_parameters['product']['cat']))),
                    'vender_id': str(dict_parameters['product']['venderId']),
                    'shop_id': str(dict_parameters['product']['shopId']),
                    'id': str(dict_parameters['product']['skuid'])
                }

                @log_response(binding=self.parse_description)
                def response_description():
                    link = 'https://cd.jd.com/promotion/v2?skuId={id}&area=1_72_4137_0&shopId={shop_id}&venderId={vender_id}&cat={cat}'
                    return requests.get(link.format(**params), headers_interface).json()

                @log_response(binding=self.parse_price)
                def response_price():
                    link = 'https://c0.3.cn/stock?skuId={id}&cat={cat}&venderId={vender_id}&area=1_72_4137_0'
                    return requests.get(link.format(**params), headers=headers_interface).json()
                result = self.parse_other(response)
                description = response_description()
                price = response_price()
                result['description'] = description
                result['price'] = price['price']
                result['weight'] = price['weight']
                result['url'] = url
                result['origin'] = origin
                self.value.append(result)
            return response_list()

    def parse_description(self, response):
        return response['ads'][0].get('ad', '未找到描述')

    def parse_price(self, response):
        price = response['stock']['jdPrice'].get('p', '未找到价钱')
        weight = response['stock'].get('weightValue', '未找到重量')
        return {
            'price': price,
            'weight': weight
        }

    # parse fields url, brand, img_url
    def parse_other(self, response):
        root = html.fromstring(response)
        title = ''.join(self.cut_blank(root.xpath('.//div[@class="sku-name"]/text()')))
        # 最大的图片：https://img11.360buyimg.com/n0/_jfs/t1/15328/31/2977/374661/5c23143eE729ca16f/7a548b712611bc7c.jpg
        img_urls = list(map(lambda x: "https://img11.360buyimg.com/n5/" + x,
                            root.xpath('.//div[@id="spec-list"]//img/@data-url')))
        introduction = self.filter_blank(root.xpath('.//div[@class="p-parameter"]//li[@title]//text()'))
        specification = {}
        for each in root.xpath('.//div[@class="Ptable"]/div'):
            key = each.xpath('./h3/text()')[0]
            value = []
            for i in each.xpath('.//dl[@class="clearfix"]'):
                value.append(': '.join(self.filter_blank(i.xpath('.//text()'))))
            specification[key] = value
        k = root.xpath('.//div[@class="package-list"]/h3/text()')[0]
        v = root.xpath('.//div[@class="package-list"]/p/text()')
        specification[k] = v
        return {
            'title': title,
            'img_urls': img_urls,
            'introduction': introduction,
            'specification': specification
        }

    @log_parse
    def parse(self, num=5):
        num = num if num < 100 else 100
        gevent.joinall([gevent.spawn(self.response) for i in range(num)])
        result = json.dumps(self.value, ensure_ascii=False)
        with open('jingdongcomputerdetail', 'w', encoding='utf-8') as fp:
            fp.write(result)


if __name__ == '__main__':
    # 672：笔记本；
    # 673：台式机；
    # 674：服务器；
    # 2694：平板电脑；
    # 1105：游戏本；
    # 12798：一体机；

    urls = ['https://item.jd.com/41975829749.html', 'https://item.jd.com/7913417.html', 'https://item.jd.com/40894980506.html',
            'https://item.jd.com/100000208951.html', 'https://item.jd.com/38229442009.html', 'https://item.jd.com/29446977968.html',
            'https://item.jd.com/8945221.html', 'https://item.jd.com/100000339301.html', 'https://item.jd.com/8386007.html',
            'https://item.jd.com/37416260269.html', 'https://item.jd.com/8420783.html', 'https://item.jd.com/30150254585.html',
            'https://item.jd.com/7210084.html', 'https://item.jd.com/100003144800.htm', 'https://item.jd.com/8342260.html'
            ]
    origins = [
        'https://list.jd.com/list.html?cat=670,671,12798&page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
        'https://list.jd.com/list.html?cat=670,671,674&page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
        'https://list.jd.com/list.html?cat=670,671,672&page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
        'https://list.jd.com/list.html?cat=670,671,2694&page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
        'https://list.jd.com/list.html?cat=670,671,673&page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0']
    a = []
    for i in origins:
        a.append(i)
        a.append(i)
        a.append(i)
    jdc = JingDongComputerDetail(urls, a)
    jdc.parse(len(urls))
    pass
