# 房屋id、标题、补充、展示图、VR看房、基本信息、房源特色、带看、户型分间、房源照片、看房记录、小区简介、周边配套
from gevent import monkey; monkey.patch_all()
from fake_useragent import UserAgent
from gevent.queue import Queue
from lxml import html
from time import time
import gevent
import logging
import json
import random
import re
import requests


class ErShouFangDetail(object):
    def __init__(self, urls):
        self.urls = urls
        self.detail_url = 'https://sz.lianjia.com/ershoufang/{id}.html'
        self.daikan_url = 'https://sz.lianjia.com/ershoufang/showcomment?id={id}'
        self.see_record_url = 'https://sz.lianjia.com/ershoufang/houseseerecord?id={id}'
        self.region_url = 'https://sz.lianjia.com/ershoufang/housestat?hid={id}&rid={rid}'
        self.queue = self.list_to_queue()
        self.value = list()
        self.retry = list()
        self.error = 0
        self.html_error = list()
        self.parse_error = list()
        # delete blank elements and remove white space at the head and tail of the remaining elements
        self.cut_blank = lambda z: map(lambda y: y.strip(), filter(lambda x: x.strip(), z))

    def list_to_queue(self):
        queue = Queue()
        for i in self.urls:
            queue.put_nowait(i)
        return queue

    def get_headers(self):
        ua = UserAgent().random
        headers_detail = {
            'Host': 'sz.lianjia.com',
            'Connection': 'keep-alive',
            'Referer': 'https://sz.lianjia.com/ershoufang/pg{num}/'.format(num=random.randint(1, 100)),
            'User-Agent': ua
        }
        headers_interface = {
            'Host': 'sz.lianjia.com',
            'Connection': 'keep-alive',
            'Referer': self.detail_url,
            'User-Agent': ua
        }
        return {
            'headers_detail': headers_detail,
            'headers_interface': headers_interface
        }

    def parse(self, queue):
        while not queue.empty():
            if self.error >= 3:
                break
            house_id = queue.get_nowait()
            url = self.detail_url.format(id=house_id)
            headers = self.get_headers()
            headers_detail = headers['headers_detail']
            headers_interface = headers['headers_interface']
            daikan_url = self.daikan_url.format(id=house_id)
            see_record_url = self.see_record_url.format(id=house_id)
            try:
                content = requests.get(url=url, headers=headers_detail, timeout=10).text
            except:
                self.retry.append(url)
                logging.warning(url, '连接超时')
                continue

            rid = re.findall(r'resblockId:\'(\d+)\'\,', content)[0]
            region_url = self.region_url.format(id=house_id, rid=rid)
            root = html.fromstring(content)

            try:
                title = root.xpath('.//div[@class="title"]/h1[@class="main"]/text()')[0]
                supplement = root.xpath('.//div[@class="title"]/div[@class="sub"]/text()')[0]
                imgs = root.xpath('.//ul[@class="smallpic"]/li/img/@src')
                vr_house = root.xpath('.//div[@class="vrHouse"]/div[@class="icon"]/text()')[0]
                vr_url = root.xpath('.//div[@class="vrHouse"]/a[@class="appLink"]/@href')[0]
                ke = root.xpath('.//h2/div[@class="title"]/text()')[0]
                va = dict()
                for each in root.xpath('.//div[@class="introContent"]/div')[:-1]:
                    k = each.xpath('./div[@class="name"]/text()')[0]
                    v = [': '.join(self.cut_blank(i.xpath('.//text()'))) for i in each.xpath('.//ul/li')]
                    va[k] = v
                base_inform = {ke: va}
                ke = root.xpath('.//div[@class="newwrap baseinform"][last()]/h2/div[@class="title"]/text()')[0]
                va = dict()
                for each in root.xpath('.//div[@class="newwrap baseinform"][last()]//div[contains(@class, "clear")]'):
                    try:
                        k = each.xpath('./div[@class="name"]/text()')[0]
                    except:
                        k = 'ERROR'
                    v = ' '.join(self.cut_blank(each.xpath('./div[@class="content"]//text()')))
                    va[k] = v
                house_feature = {ke: va}
                try:
                    layout_img = root.xpath('.//div[@class="imgdiv"]/img/@src')[0]
                    layout_des = [' '.join(each.xpath('./div/text()')) for each in root.xpath('.//div[@id="infoList"]/div[@class="row"]')]
                    layout = {
                        'layout_img': layout_img,
                        'layout_des': layout_des
                    }
                except:
                    layout = {}
                house_imgs = dict()
                for each in root.xpath('.//div[@class="list"]/div[@data-index]'):
                    k = each.xpath('./span/text()')[0]
                    v = each.xpath('./img/@src')[0]
                    house_imgs[k] = v
                try:
                    daikan_req = requests.get(url=daikan_url, headers=headers_interface).json()
                    daikan = list()
                    for each in daikan_req['data']['agentList']:
                        name = each['name']
                        comment = each['comment']
                        last_date = each['lastestSeeRecordDate']
                        total_num = each['agentSeeRecordNum']
                        daikan.append({
                            'name': name,
                            'comment': comment,
                            'last_date': last_date,
                            'total_num': total_num
                        })
                except:
                    daikan = list()
                try:
                    see_record_req = requests.get(url=see_record_url, headers=headers_interface).json()
                    see_record = list()
                    for each in see_record_req['data']['seeRecord']:
                        see_time = each['seeTime']
                        agent_id = str(each['agentId'])
                        see_num = str(each['seeCnt'])
                        agent_name = see_record_req['data']['agentInfo'][agent_id]['agentName']
                        see_record.append({
                            'see_time': see_time,
                            'agent_id': agent_id,
                            'see_num': see_num,
                            'agent_name': agent_name
                        })
                except:
                    see_record = list()

                region_req = requests.get(url=region_url, headers=headers_interface).json()
                each = region_req['data']['resblockCard']
                region = list()
                region.append({
                    'name': each['name'],
                    'year': each['buildYear'],
                    'floor': each['buildNum'],
                    'style': each['buildType'],
                    'price': each['unitPrice']
                })

                value = {
                    "house_id": house_id,
                    "title": title,
                    'supplement': supplement,
                    'imgs': imgs,
                    'vr_house': vr_house,
                    'vr_url': vr_url,
                    'base_inform': base_inform,
                    'house_feature': house_feature,
                    'layout': layout,
                    'house_imgs': house_imgs,
                    'daikan': daikan,
                    'see_record': see_record,
                    'region': region
                }
                self.value.append(value)
            except:
                self.parse_error.append({
                    "url": url,
                    "content": content
                })
                self.error += 1
                logging.error(''.join([url, '解析失败！']))
                continue

    def run(self, num=5):
        num = num if num < 100 else 100
        gevent.joinall([gevent.spawn(self.parse, self.queue) for i in range(num)])


if __name__ == '__main__':
    # 使用协程，详情页902页902条数据，483.756032705307s左右
    # 使用协程，详情页1371页1371条数据，889.4946854114532s左右
    # 使用协程，详情页1625页1625条数据，95.85135197639465s左右
    # 使用协程，详情页2996页2996条数据，383s左右
    with open('ershoufang.txt', 'r', encoding='utf8') as fp:
        txt = json.loads(fp.read())
    link = set([i['house_id'] for i in txt])
    start_time = time()
    esf = ErShouFangDetail(link)
    esf.run(100)

    end_time = time()
    print('total time: {}s'.format(end_time-start_time))
    with open('ershoufangdetail.txt', 'a', encoding='utf8') as fp:
        fp.write(json.dumps(esf.value, ensure_ascii=False))
    print('retry:', esf.retry)
    print('html_error:', esf.html_error)
    print('parse_error:', esf.parse_error)
    pass

    # # 解决爬取重复问题
    # from collections import Counter
    # with open('ershoufangdetail.txt', 'r', encoding='utf8') as fp:
    #     s = fp.read()
    # import json
    #
    # a = json.loads(s)
    # b = [i['house_id'] for i in a]
    #
    # # # 查看哪些数据是重复的
    # # print(len(set(b)))
    # # print(Counter(b))
    #
    # # 把重复数据放在列表中
    # l = [105101988829, 105101415451, 105101488954,105100878390,105101268037,105101421770,105101485072]
    # # 找出重复数据对应的列表页，相同则是爬虫问题，不同则是网站排版问题
    # for i in a:
    #     for j in l:
    #         if str(j) in i['house_id']:
    #             print(i)
    # # 结论：网站排版问题
