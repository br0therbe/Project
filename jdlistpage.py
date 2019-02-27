from fake_useragent import UserAgent
from lxml import html
from time import time
import json
import random
import re
import requests


class JDListPage(object):
    def __init__(self, url_list):
        self.url_list = url_list
        self.url_description = 'https://ad.3.cn/ads/mgets?&my=list_adWords&source=JDList&skuids={ids}'
        self.url_price = 'https://p.3.cn/prices/mgets?skuIds={ids}'
        self.url_comment = 'https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds={ids}'
        self.url_shop = 'https://chat1.jd.com/api/checkChat?my=list&pidList={ids}'

    # build the random request headers
    def get_headers(self):
        ua = UserAgent().random
        # the request headers of list page
        headers_list = {
            'authority': 'list.jd.com',
            'method': 'GET',
            'path': self.url_list.replace('https://list.jd.com', ''),
            'scheme': 'https',
            'referer': 'https://list.jd.com/list.html?cat=670,671,1105&sort=sort_totalsales15_desc&trans=1&page={page}&JL=6_0_0'.format(page=random.randint(1, 226)),
            'user-agent': ua
        }
        # the request headers of interface
        headers_interface = {
            'Referer': self.url_list,
            'User-Agent': ua
        }
        return {
            'headers_list': headers_list,
            'headers_interface': headers_interface
        }

    # parse fields
    def parse(self):
        # build the request headers that will be used when request
        headers = self.get_headers()
        headers_list = headers['headers_list']
        headers_interface = headers['headers_interface']

        # get product id
        req_list = requests.get(url=self.url_list, headers=headers_list).text
        attr_list = ''.join(re.findall(r'attrList = (.*?) };', req_list, re.S))
        ids = re.findall(r'(\d+):{', attr_list, re.S)

        # parse field description
        url_description = self.url_description.format(ids='AD_'+',AD_'.join(ids))
        req_desc = requests.get(url=url_description, headers=headers_interface).json()
        # dict_desc = json.loads(req_desc)
        list_desc = [i['ad'] for i in req_desc]

        # parse field comment
        url_comment = self.url_comment.format(ids=','.join(ids))
        req_com = requests.get(url=url_comment, headers=headers_interface).json()
        # dict_com = json.loads(req_com)
        list_com = [i['CommentCountStr'] for i in req_com['CommentsCount']]

        # parse field shop
        url_shop = self.url_shop.format(ids=','.join(ids))
        req_shop = requests.get(url=url_shop, headers=headers_interface).text.replace('null(', '').replace(');', '')
        dict_shop = json.loads(req_shop)
        list_shop = [i['seller'] for i in dict_shop]

        # parse field price
        url_price = self.url_price.format(ids='J_'+',J_'.join(ids))
        req_price = requests.get(url=url_price, headers=headers_interface).json()
        # dict_price = json.loads(req_price)
        list_price = [i['p'] for i in req_price]

        # parse fields url, brand, img_url and package all fields
        root = html.fromstring(req_list.replace('data-lazy-img', 'src'))
        for index, each in enumerate(root.xpath('//ul[@class="gl-warp clearfix"]/li')):
            url = 'https:' + each.xpath('.//a[@title=""]/@href')[0].strip()
            brand = each.xpath('.//a[@title=""]/em/text()')[0].strip()
            img_url = 'https:' + each.xpath('.//a/img/@src')[0].strip()
            yield {
                "url": url,
                "price": list_price[index],
                "brand": brand,
                "description": list_desc[index],
                "comment": list_com[index],
                "shop": list_shop[index],
                "img_url": img_url
            }


if __name__ == '__main__':
    start_time = time()
    url = 'https://list.jd.com/list.html?cat=670,671,1105&page=1&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main'
    jdlp = JDListPage(url_list=url)
    print(json.dumps(list(jdlp.parse()), ensure_ascii=False))
    end_time = time()
    print("spend time:  {}s".format(end_time-start_time))
    pass
