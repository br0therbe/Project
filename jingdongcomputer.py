# -*- encoding: utf-8 -*-
"""
@File    : jingdongcomputer.py
@Time    : 2019/3/12 14:49
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


class JingDongComputer(Spiders):
    def __init__(self, urls, level=logging.INFO):
        super().__init__(urls=urls, level=level, filename=os.path.basename(__file__))

    @log_func
    def set_headers(self, url):
        ua = UserAgent().random
        headers_list = {
            'authority': 'list.jd.com',
            'method': 'GET',
            'path': url.replace('https://list.jd.com', ''),
            'scheme': 'https',
            'referer': 'https://diannao.jd.com/',
            'user-agent': ua
        }
        headers_interface = {
            'Referer': url,
            'User-Agent': ua
        }
        return {
            'headers_list': headers_list,
            'headers_interface': headers_interface
        }

    def response(self):
        while not self.queue.empty():
            url = self.set_url()
            headers = self.set_headers(url)
            headers_list = headers['headers_list']
            headers_interface = headers['headers_interface']

            @log_func
            def response_list():
                response = requests.get(url, headers_list).text
                attr_list = ''.join(re.findall(r'attrList = (.*?) };', response, re.S))
                ids = re.findall(r'(\d+):{', attr_list, re.S)
                result = self.parse_other(response)

                @log_response(binding=self.parse_description)
                def response_description():
                    link = 'https://ad.3.cn/ads/mgets?&my=list_adWords&source=JDList&skuids={ids}'
                    return requests.get(link.format(ids='AD_'+'%2CAD_'.join(ids)), headers_interface).json()

                @log_response(binding=self.parse_comment)
                def response_comment():
                    link = 'https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds={ids}'
                    return requests.get(link.format(ids=','.join(ids)), headers=headers_interface).json()

                @log_response(binding=self.parse_shop)
                def response_shop():
                    link = 'https://chat1.jd.com/api/checkChat?my=list&pidList={ids}'
                    return requests.get(link.format(ids=','.join(ids)), headers=headers_interface).text

                @log_response(binding=self.parse_price)
                def response_price():
                    link = 'https://p.3.cn/prices/mgets?skuIds={ids}'
                    return requests.get(link.format(ids='J_' + '%2CJ_'.join(ids)), headers=headers_interface).json()

                description = response_description()
                comment = response_comment()
                shop = response_shop()
                price = response_price()
                for index, each in enumerate(result):
                    each['origin'] = url
                    each['description'] = description[index]
                    each['comment'] = comment[index]
                    each['shop'] = shop[index]
                    each['price'] = price[index]
                    self.value.append(each)
            return response_list()

    def parse_description(self, response):
        return [i.get('ad', '未找到描述') for i in response]

    def parse_comment(self, response):
        return [i['CommentCountStr'] for i in response['CommentsCount']]

    def parse_shop(self, response):
        dict_shop = json.loads(response.replace('null(', '').replace(');', ''))
        return [i.get('seller', '未找到店铺') for i in dict_shop]

    def parse_price(self, response):
        return [i.get('p', '未找到价格') for i in response]

    # parse fields url, brand, img_url
    def parse_other(self, response):
        result = []
        root = html.fromstring(response.replace('data-lazy-img', 'src'))
        for index, each in enumerate(root.xpath('//ul[@class="gl-warp clearfix"]/li')):
            url = 'https:' + each.xpath('.//a[@title=""]/@href')[0].strip()
            brand = each.xpath('.//a[@title=""]/em/text()')[0].strip()
            img_url = 'https:' + each.xpath('.//a/img/@src')[0].strip()
            result.append({
                'url': url,
                'brand': brand,
                'img_url': img_url
            })
        return result

    @log_parse
    def parse(self, num=5):
        num = num if num < 100 else 100
        gevent.joinall([gevent.spawn(self.response) for i in range(num)])
        result = json.dumps(self.value, ensure_ascii=False)
        with open('jingdongcomputer', 'w', encoding='utf-8') as fp:
            fp.write(result)


if __name__ == '__main__':
    # 672：笔记本；
    # 673：台式机；
    # 674：服务器；
    # 2694：平板电脑；
    # 1105：游戏本；
    # 12798：一体机；
    url = ['https://list.jd.com/list.html?cat=670,671,1105&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
           'https://list.jd.com/list.html?cat=670,671,672&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
           'https://list.jd.com/list.html?cat=670,671,674&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
           'https://list.jd.com/list.html?cat=670,671,2694&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
           'https://list.jd.com/list.html?cat=670,671,673&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0',
           'https://list.jd.com/list.html?cat=670,671,12798&page={page}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0'
           ]
    urls = [i.format(page=3) for i in url[1:]]
    # urls = [url.format(page=i) for i in range(11, 18)]
    jdc = JingDongComputer(urls)
    jdc.parse(len(urls))
    pass
