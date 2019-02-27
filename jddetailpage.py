from gevent import monkey; monkey.patch_all()
from fake_useragent import UserAgent
from gevent.queue import Queue
from lxml import html
from time import time
import gevent
import json
import random
import re
import requests


class JDDetailPage(object):
    def __init__(self, urls):
        self.value = []
        self.urls = urls
        self.queue = self.list_to_queue()
        self.url_detail = 'https://item.jd.com/{id}.html'
        self.url_jd_service = 'https://cd.jd.com/mcsFacade?skuId={id}&cat={cat}&brandId={brandid}&area=1_72_4137_0'
        self.url_value_guarantee = 'https://cd.jd.com/yanbao/v3?skuId={id}&cat={cat}&brandId={brandid}&area=1_72_4137_0'
        self.url_comment_num = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={id}'
        self.url_price = 'https://c0.3.cn/stock?skuId={id}&cat={cat}&venderId={venderid}&area=1_72_4137_0'
        self.url_iou = 'https://btshow.jd.com/queryBtPlanInfo.do?callback=queryBtPlanInfo&sku={id}&cId={cat}&num=1&amount={price}&sourceType=PC-XQ&shopId={shopid}'
        self.url_description = 'https://cd.jd.com/promotion/v2?skuId={id}&area=1_72_4137_0&shopId={shopid}&venderId={venderid}&cat={cat}'
        # function filter_blank is to filter the blank elements in the array and leave non-blank elements
        self.filter_blank = lambda y: list(filter(lambda x: x.strip(), y))
        # function cut_blank is to cut the blank in elements of the array
        self.cut_blank = lambda y: list(map(lambda x: x.strip(), y))

    def list_to_queue(self):
        queue = Queue()
        for each in self.urls:
            queue.put_nowait(each)
        return queue

    def get_headers(self):
        """
        referer of headers_detail needs to reassign
        :return:
        """
        ua = UserAgent().random
        # the request headers of list page
        headers_detail = {
            'authority': 'item.jd.com',
            'method': 'GET',
            'path': self.url_detail.replace('https://item.jd.com', ''),
            'scheme': 'https',
            'referer': 'https://list.jd.com/list.html?cat=670,671,1105&sort=sort_totalsales15_desc&trans=1&page={page}&JL=6_0_0'.format(
                page=random.randint(1, 226)),
            'user-agent': ua
        }
        # the request headers of interface
        headers_interface = {
            'Referer': self.url_detail,
            'User-Agent': ua
        }
        return {
            'headers_detail': headers_detail,
            'headers_interface': headers_interface
        }

    def run(self, num=5):
        num = num if num < 100 else 100
        gevent.joinall([gevent.spawn(self.parse, self.queue) for i in range(num)])

    def parse(self, queue):
        while not queue.empty():
            product_id = queue.get_nowait()
            print(product_id, gevent.getcurrent())
            try:
                self.url_detail = self.url_detail.format(id=product_id)
                # build the request headers that will be used when request
                headers = self.get_headers()
                headers_detail = headers['headers_detail']
                headers_interface = headers['headers_interface']
                req_detail = requests.get(url=self.url_detail, headers=headers_detail).text

                # parse parameters from source code to interface urls
                page_config = re.findall(r'var pageConfig = (.+?});', req_detail, re.S)[0]
                add_double_quotes = re.sub(r'(?P<word>[\w ]+):', lambda x: '"{}":'.format(x.group('word')), page_config)
                cut_blank = re.sub(r'\s+', '', add_double_quotes).replace('/**//**/', '')
                replace_word = cut_blank.replace('true', '"true"').replace('false', '"false"').replace("'", '"')
                dict_parameters = json.loads(replace_word)
                cat = ','.join(list(map(lambda x: str(x), dict_parameters['product']['cat'])))
                brand_id = str(dict_parameters['product']['brand'])
                vender_id = str(dict_parameters['product']['venderId'])
                shop_id = str(dict_parameters['product']['shopId'])

                # parse fields shop, shop_id, value_service, price, weight
                url_price = self.url_price.format(id=product_id, cat=cat, venderid=vender_id)
                req_price = requests.get(url=url_price, headers=headers_interface).json()
                shop = req_price['stock']['self_D']['vender']
                # shop_id = req_price['stock']['self_D']['id']
                value_service = [i['showName'] for i in req_price['stock']['support']]
                price = req_price['stock']['jdPrice']['p']
                weight = req_price['stock'].get('weightValue', None)
                url_jd_service = self.url_jd_service.format(id=product_id, cat=cat, brandid=brand_id)
                url_value_guarantee = self.url_value_guarantee.format(id=product_id, cat=cat, brandid=brand_id)
                url_comment_num = self.url_comment_num.format(id=product_id)
                url_iou = self.url_iou.format(id=product_id, cat=cat, price=price, shopid=shop_id)
                url_description = self.url_description.format(id=product_id, cat=cat, venderid=vender_id, shopid=shop_id)

                # parse field jd_service
                req_jd_service = requests.get(url=url_jd_service, headers=headers_interface)
                jd_service = []
                if req_jd_service.text:
                    for each in req_jd_service.json():
                        li = []
                        for i in each['serviceSkuInfoList']:
                            li.append({
                                'service_name': i['serviceSkuName'],
                                'service_price': i['serviceSkuPrice']
                            })
                        jd_service.append(li)

                # parse field value_guarantee
                req_value_guarantee = requests.get(url=url_value_guarantee, headers=headers_interface)
                value_guarantee = []
                if req_value_guarantee.text:
                    for each in req_value_guarantee.json()[product_id]:
                        li = []
                        for i in each['details']:
                            li.append({
                                'guarantee_name': i['bindSkuName'],
                                'guarantee_price': i['price']
                            })
                        value_guarantee.append(li)

                # parse fields comment_num, good_rate
                req_comment_num = requests.get(url=url_comment_num, headers=headers_interface).json()
                comment_num = req_comment_num['CommentsCount'][0]['CommentCountStr']
                good_rate = req_comment_num['CommentsCount'][0]['GoodRate']

                # parse field iou
                req_iou = requests.get(url=url_iou, headers=headers_interface).text
                dict_iou = json.loads(re.findall(r'queryBtPlanInfo\((.+)\)', req_iou, re.S)[0])
                iou = []
                for each in dict_iou['planInfos']:
                    iou.append({
                        'curTotal': each['curTotal'],
                        'plan': each['plan'],
                        'rate': each['rate'],
                        'planFee': each['planFee'],
                        'fee': each['fee']
                    })

                # parse field description
                req_desc = requests.get(url=url_description, headers=headers_interface).json()
                description = req_desc['ads'][0]['ad']

                # parse fields img_urls, brand, color, introduction, specification, after_service
                root = html.fromstring(req_detail)
                img_urls = list(map(lambda x: "https://img11.360buyimg.com/n5/"+x, root.xpath('.//div[@id="spec-list"]//img/@data-url')))
                brand = root.xpath('//div[@class="sku-name"]/text()')[0].strip()
                introduction = self.filter_blank(root.xpath('.//div[@class="p-parameter"]//li[@title]//text()'))

                color = []
                for each in root.xpath('.//div[@id="choose-attr-1"]//div[@data-sku]'):
                    color.append({
                        'product_id': each.xpath('./@data-sku')[0],
                        'title': each.xpath('./@data-value')[0],
                        'img_url': 'https:' + each.xpath('.//img/@src')[0]
                    })

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

                as_key = self.cut_blank(root.xpath('.//div[@class="serve-agree-bd"]/dl/dt/strong/text()'))
                as_value = self.cut_blank([''.join(i.xpath('.//text()')) for i in root.xpath('.//div[@class="serve-agree-bd"]/dl/dd')])
                after_service = dict(zip(as_key, as_value))

                result = {
                    'jd_service': jd_service,
                    'value_guarantee': value_guarantee,
                    'comment_num': comment_num,
                    'good_rate': good_rate,
                    'shop': shop,
                    'shop_id': shop_id,
                    'value_service': value_service,
                    'price': price,
                    'weight': weight,
                    'iou': iou,
                    'description': description,
                    'img_urls': img_urls,
                    'brand': brand,
                    'color': color,
                    'introduction': introduction,
                    'specification': specification,
                    'after_service': after_service
                }
                self.value.append(result)
            except Exception as e:
                print(''.join(['url:', str(product_id), '获取失败']), e)
                continue


if __name__ == '__main__':
    start_time = time()
    pids = ['8674557', '8461498', '100000612187', '100000769432', '100000769466', '100000679465', '8461496', '8461490', '100000667974', '100001234930', '100001234898', '8461500', '100000430140', '8736570', '100001895678']
    # pids = ['8674557']
    jddp = JDDetailPage(pids)
    jddp.run(len(pids))
    end_time = time()
    print("spend time:  {}s".format(end_time - start_time))

    start_time = time()
    txt = json.dumps(jddp.value, ensure_ascii=False)
    with open(r'C:\Users\11021\Desktop\detail.txt', 'w') as fp:
        fp.write(txt)
    end_time = time()
    print("spend time:  {}s".format(end_time - start_time))
