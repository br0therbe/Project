from datetime import datetime
from fake_useragent import UserAgent
from time import time
import base64
import json
import requests


class QiMai(object):
    def __init__(self):
        self.base_url = 'https://api.qimai.cn'
        self.url = 'https://api.qimai.cn/rank/indexPlus/brand_id/'
        pass

    def get_analysis(self, num=1, params=None):
        """
        function get_analysis is for getting analysis parameter which is encrypted by JS
        :param num: {1: 免费榜， 0：付费榜，2：畅销榜}
        :param params: MUST BE DICTIONARY TYPE
        :return: the encrypted parameters, analysis
        """
        p = '@#'
        n = '00000008d78d46a'
        # cur_time: 36989454152
        cur_time = int(1000*time()) - 1515125653845
        if params == {}:
            params = ''
        if params:
            params = base64.b64encode(''.join(sorted(params.values())).encode(encoding='utf8')).decode(encoding='utf8')
        # m: @#/rank/indexPlus/brand_id/2@#36989454152@#1

        m = ''.join([params, p, self.url.replace(self.base_url, ''), str(num), p + str(cur_time), p + str(1)])
        # a may be messy code but it is unimportant
        a = ''.join([chr(ord(j) ^ ord(n[i % len(n)])) for i, j in enumerate(m)])
        analysis = base64.b64encode(a.encode(encoding='utf8')).decode(encoding='utf8')
        return analysis

    def parse(self, num=1):
        """
        function parse is for parsing QiMai data
        :param num: {1: 免费榜， 0：付费榜，2：畅销榜}
        :return: generator type, parsed data
        """
        page = 1
        while page <= 3:

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://www.qimai.cn',
                'Referer': 'https://www.qimai.cn/rank',
                'User-Agent': UserAgent().random
            }
            if page == 1:
                params = {}
            else:
                params = {
                    'brand': 'all',
                    'country': 'cn',
                    'device': 'iphone',
                    'genre': '5000',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'page': str(page)
                }
            analysis = self.get_analysis(num=num, params=params)
            params['analysis'] = analysis
            data = requests.get(url=self.url+str(num), headers=headers, params=params).json()
            print(data)
            if data['code'] != 10000:
                return "DATA ERROR!"

            for each in data['list']:
                yield {
                    'rank': each['index'],
                    'app_id': each['appInfo']['appId'],
                    'app_name': each['appInfo']['appName'],
                    'icon_url': each['appInfo']['icon'],
                    'publisher': each['appInfo']['publisher'],
                    'publisher_id': each['publisher_id'],
                    'country': each['appInfo']['country'],
                    'price': each['appInfo']['price'],
                    'ranking': each['class']['ranking'],
                    'genre': each['genre']
                }
            page += 1


if __name__ == '__main__':
    start_time = time()
    qm = QiMai()
    result = qm.parse(0)
    result = json.dumps(list(result), ensure_ascii=False)
    end_time = time()

    print(result)
    print('total time is {:.3f}s'.format(int(end_time-start_time)))
    pass
