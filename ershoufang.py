from gevent import monkey; monkey.patch_all()
from fake_useragent import UserAgent
from gevent.queue import Queue
from lxml import html
from time import time
import gevent
import logging
import json
import re
import requests


class ErShouFang(object):
    def __init__(self, urls):
        self.urls = urls
        self.queue = self.list_to_queue()
        self.value = list()
        self.retry = list()
        self.error = 0
        self.html_error = list()
        self.parse_error = list()

    def list_to_queue(self):
        queue = Queue()
        for i in self.urls:
            queue.put_nowait(i)
        return queue

    def get_headers(self):
        ua = UserAgent().random
        headers = {
            'Host': 'sz.lianjia.com',
            'Connection': 'keep-alive',
            'Referer': 'https://sz.lianjia.com/ershoufang/',
            'User-Agent': ua
        }
        return headers

    def parse(self, queue):
        headers = self.get_headers()
        while not queue.empty():
            if self.error >= 3:
                break
            url = queue.get_nowait()
            try:
                content = requests.get(url=url, headers=headers, timeout=10).text
            except:
                self.retry.append(url)
                logging.warning(url, '连接超时')
                continue
            result = re.findall(r'\</script\>(\<div class=\"listContentLine\"\>.+\</div\>)', content)
            if result:
                root = html.fromstring(result[0])
            else:
                self.html_error.append({
                    'url': url,
                    'content': content
                })
                logging.error(''.join([url, 'html提取失败！']))
                continue
            try:
                for each in root.xpath('//ul[@class="sellListContent"]/li'):
                    house_id = each.xpath('.//a[@data-el="ershoufang"]/@data-housecode')[0]
                    img = each.xpath('.//img[@class="lj-lazy"]/@data-original')[0]
                    title = each.xpath('.//div[@class="title"]/a/text()')[0]
                    house_info = ''.join(each.xpath('.//div[@class="houseInfo"]//text()'))
                    position = ''.join(each.xpath('.//div[@class="positionInfo"]//text()'))
                    follow = each.xpath('.//div[@class="followInfo"]/text()')[0]
                    tag = each.xpath('.//div[@class="tag"]/span/text()')
                    total_price = ''.join(each.xpath('.//div[@class="totalPrice"]//text()'))
                    unit_price = each.xpath('.//div[@class="unitPrice"]/span/text()')[0]
                    value = {
                        "url": url,
                        'house_id': house_id,
                        'img': img,
                        'title': title,
                        'house_info': house_info,
                        'position': position,
                        'follow': follow,
                        'tag': tag,
                        'total_price': total_price,
                        'unit_price': unit_price
                    }
                    self.value.append(value)
            except:
                self.parse_error.append({
                    "url": url,
                    "content": content
                })
                self.error += 1
                logging.error(''.join([url, 'html解析失败！']))
                continue

    def run(self, num=5):
        num = num if num < 100 else 100
        gevent.joinall([gevent.spawn(self.parse, self.queue) for i in range(num)])


if __name__ == '__main__':
    # 使用协程，列表页100页3000条数据，15s左右
    start_time = time()
    link = ['https://sz.lianjia.com/ershoufang/pg{num}/'.format(num=i) for i in range(1, 101)]
    esf = ErShouFang(link)
    esf.run()
    end_time = time()
    print('total time: {}s'.format(end_time-start_time))
    with open('ershoufang.txt', 'w', encoding='utf8') as fp:
        fp.write(json.dumps(esf.value, ensure_ascii=False))
    print('retry:', esf.retry)
    print('html_error:', esf.html_error)
    print('parse_error:', esf.parse_error)
    pass

    # # 解决爬取重复问题
    # from collections import Counter
    # with open('ershoufang.txt', 'r', encoding='utf8') as fp:
    #     s = fp.read()
    # import json
    #
    # a = json.loads(s)
    # b = [i['house_id'] for i in a]
    #
    # # 查看哪些数据是重复的
    # # print(len(set(b)))
    # # print(Counter(b))
    #
    # # 把重复数据放在列表中
    # l = [105100878390, 105101268037, 105101421770]
    # # 找出重复数据对应的列表页，相同则是爬虫问题，不同则是网站排版问题
    # for i in a:
    #     for j in l:
    #         if str(j) in i['house_id']:
    #             print(i)
    # # 结论：网站排版问题
