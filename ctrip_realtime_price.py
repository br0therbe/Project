# encoding: utf-8
import json
import re
import requests
from app.common import PlatsName
from app.utils.decorator_func import timecost
from app.utils.log_manager import LogManager
from app.utils.proxies_util import ProxyFromRedis
import datetime

my_proxy = ProxyFromRedis()
scenic_headers = {
    'Connection': 'keep-alive',
    'Host'      : 'm.ctrip.com',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
    }

pat = re.compile(r'__INITIAL_STATE__ = (.*)')
find_cid = re.compile(r'"cid":"(\w+)')
logger = LogManager('ctrip_crawl').get_logger_and_add_handlers()

def connect_retry(method: str, url: str, headers: dict, data: dict = None, params: dict = None, allow_redirects=True, timeout=7, retry=5, proxies=None):
    connect_num = 1
    resp = None
    if proxies == False:
        proxies = my_proxy.get_auto_proxy()
    while connect_num <= retry:
        try:
            resp = requests.request(method, url, headers=headers, proxies=proxies, timeout=timeout, data=data, params=params, allow_redirects=allow_redirects)
            break
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
            __message = f'{url}, 连接超时, 第{connect_num}次重试'
            logger.fatal(__message)
            connect_num += 1
    logger.debug(f'resp: {resp}')
    if not resp:
        __message = f'url: {url}, 请求失败, 原因：连接超时'
        logger.fatal(__message)
        raise ConnectionError(__message)

    status_code = resp.status_code
    if status_code != 200:
        __message = f'url: {url}, 请求失败，原因：status_code={status_code}'
        logger.fatal(__message)
        raise ValueError(__message)

    return resp

class Ctrip(object):
    '''
    实时爬取类
    '''
    def __init__(self):
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.price_list = []
        self.flag = False
        self.lowest_price = None
        self.remarks = None
        self.price = None
        self.has_ticket = 0
        self.pingtai = PlatsName.CTRIP[0]

    @timecost(PlatsName.CTRIP[1])
    def get_immediate_price(self, scenic_id, date, supType, expiryTimestamp):
        scenic_url = f'http://m.ctrip.com/webapp/ticket/dest/t{scenic_id}.html'

        resp = connect_retry('get', scenic_url, headers=scenic_headers)
        resp_str = resp.text
        cid = find_cid.search(resp_str)
        if cid:
            cid = cid.group(1)
        else:
            logger.error('解析错误，无法找到 cid')
            raise ValueError('解析错误，无法找到 cid')
        get_dict = pat.search(resp_str)
        if get_dict:
            get_dict = get_dict.group(1)
        else:
            logger.error('解析错误，无法找到__INITIAL_STATE__')
            raise ValueError('解析错误，无法找到__INITIAL_STATE__')
        js_res = json.loads(get_dict)['detailInfo']
        # logger.debug(json.dumps(js_res, ensure_ascii=False))
        price_info_list = js_res['shelfinfo']['renderlist']
        # logger.debug(json.dumps(price_info_list, ensure_ascii=False))
        for price_info in price_info_list:
            if price_info['type'] != 2:
                continue
            for ticket_price in price_info['ress']:
                remark = ''
                for i in ticket_price['tservicetags']:
                    if i['tcode'] == 'TodayCanBook' or i['tcode'] == 'TomorrowCanBook':
                        remark = i['tname']
                self.price_list.append({
                    'price'     : ticket_price['price'],
                    'product_id': ticket_price['resid'],
                    'hasTicket' : 1 if ticket_price['issale'] else 0,
                    'remarks'   : remark
                    })

        if not self.price_list:
            self.remarks = '当日无票'
        else:
            # todo 280
            # self.lowest_price = 280
            self.lowest_price = sorted(self.price_list, key=lambda x: x['price'])[0]['price']
            logger.info(self.lowest_price)
            for price in self.price_list:
                if price['price'] != self.lowest_price:
                    self.remarks = '当日无票'
                    continue
                flag = False
                if date == self.date:
                    flag = True
                # if '今日' in price['remarks']:
                #     flag = True
                calender_list = self.get_calendar(scenic_url, price['product_id'], cid, flag)
                if not calender_list:
                    self.remarks = '当日无票'
                    continue
                else:
                    for _price in calender_list:
                        if date == _price['date']:
                            self.flag = True
                        else:
                            self.remarks = '当日无票'
                            continue
                        if _price['price'] == 0:
                            self.remarks = '景点免费'
                        else:
                            self.remarks = price['remarks'] if flag else ''
                        self.price = _price['price']
                        self.has_ticket = 1
                        break
                if self.flag:
                    break
            logger.debug(json.dumps(self.price_list, ensure_ascii=False))
        # item['remarks'] = '当日无票'
        # item['remarks'] = '景点免费'
        # item['remarks'] = '未提供产品'
        # item['remarks'] = '爬取网站异常'
        item = {}
        item['supType'] = supType
        item['supSpotId'] = scenic_id
        item['date'] = date
        item['expiryTimestamp'] = expiryTimestamp
        item['bookingUrl'] = scenic_url
        item['supName'] = PlatsName.CTRIP[1]
        item['logoUrl'] = PlatsName.CTRIP[2]
        item['remarks'] = self.remarks
        item['hasTicket'] = self.has_ticket
        item['price'] = self.price
        logger.info(json.dumps(item, ensure_ascii=False))
        return item

    def get_calendar(self, scenic_id, product_id, cid, flag=False):
        # scenic_detail_url = 'http://sec-m.ctrip.com/restapi/soa2/12530/json/scenicSpotDetails?_fxpcqlniredt=09031148410852667341'

        calendar_url = f'http://sec-m.ctrip.com/restapi/soa2/12530/json/ticketPriceList?_fxpcqlniredt={cid}'
        spare_calendar_url_ = f'http://sec-m.ctrip.com/restapi/soa2/12530/json/specialProductPrice?_fxpcqlniredt={cid}'
        headers = {
            'Content-Type': 'application/json',
            'cookieorigin': 'http://m.ctrip.com',
            'Origin'      : 'http://m.ctrip.com',
            'Referer'     : f'http://m.ctrip.com/webapp/ticket/booking?spotid={scenic_id}&tid={product_id}',
            'User-Agent'  : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }
        # if flag:
        #     post_data = json.dumps({
        #         "isoversea"   : False,
        #         "resids"      : [int(product_id)],
        #         "pageid"      : 10650006622,
        #         "insuranceids": [347, 348, 349, 350],
        #         "contentType" : "json",
        #         "head"        : {"cid": str(cid), "ctok": "", "cver": "1.0", "lang": "01", "sid": "8888", "syscode": "09", "auth": "", "extension": [{"name": "protocal", "value": "https"}]},
        #         "ver"         : "7.14.2"
        #         })
        # else:
        #     post_data = json.dumps({
        #         "isoversea"  : False,
        #         "resids"     : [int(product_id)],  # [2957789],
        #         "pageid"     : 10650006622,  # 10650006622,
        #         "contentType": "json",
        #         "head"       : {"cid": str(cid), "ctok": "", "cver": "1.0", "lang": "01", "sid": "8888", "syscode": "09", "auth": "", "extension": [{"name": "protocal", "value": "https"}]},
        #         "ver"        : "7.14.2"
        #         })
        post_data = json.dumps({
            "resids"     : [int(product_id)],
            "restype"    : 0,
            "pageid"     : 10650006622,
            "contentType": "json",
            "head"       : {"cid": str(cid), "ctok": "", "cver": "1.0", "lang": "01", "sid": "8888", "syscode": "09", "auth": "", "extension": [{"name": "protocal", "value": "https"}]},
            "ver"        : "7.14.2"
            })
        resp = connect_retry('post', calendar_url, data=post_data, headers=headers)
        calendar_dict = resp.json()
        logger.debug(json.dumps(calendar_url, ensure_ascii=False))
        if 'data' not in calendar_dict.keys():
            __message = 'data 键不在价格日历中'
            logger.error(__message)
            raise KeyError(__message)
        if 'resprices' not in calendar_dict['data']:
            __message = 'resprices 键不在价格日历中'
            logger.error(__message)
            raise KeyError(__message)
        resprices = calendar_dict['data']['resprices']
        if not resprices:
            __message = '价格日历为空'
            return []
        price_list = resprices[0]['dailyprices']
        logger.debug(json.dumps(price_list, ensure_ascii=False))
        return price_list

if __name__ == '__main__':
    # 4336357, 12325, 1409369 10000
    c = Ctrip()
    c.get_immediate_price(12325, '2019-05-31', 'ctrip', 'expiryTimestamp')
