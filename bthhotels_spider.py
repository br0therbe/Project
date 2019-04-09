import re
import requests
from lxml import html
from recognize_image import recognize

class BthHotelSpider(object):
    # args = [hotel_id, check_in, check_out, adult_num, child_str]
    def __init__(self, hotel_id, check_in, check_out):
        self._hotel_id = hotel_id
        self._check_in = check_in
        self._check_out = check_out
        self.room_url = 'http://www.bthhotels.com/HotelAct/RoomList_H5'
        self.css_url = 'http://www.bthhotels.com/ajax/getpricestyle'
        self.class_list = list()
        self.css_str = ''
        self.session = requests.session()
        self._headers = {
            'Referer': f'http://www.bthhotels.com/hotel/{self._hotel_id}',
            'Connection': 'keep-alive',
            'Host': 'www.bthhotels.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36',
        }
        self._post_data = {
            "ArrDate": self._check_in,
            "DepDate": self._check_out,
            "hotelCd": self._hotel_id,
            "memberNo": '',
            "ForHighLevel": False
        }

    def css_class(self):
        resp_str = self.session.post(url=self.room_url, headers=self._headers, data=self._post_data).text
        root = html.fromstring(resp_str)
        # 错误示例，会解析所有var节点的class的值，原因未知
        # print(root.xpath('//div[@class="h5_fr fix"][1]/strong/var/@class'))
        self.class_list = root.xpath('//div[@class="h5_fr fix"]')[0].xpath('./strong/var/@class')

    def css_html(self):
        self.css_str = self.session.get(url=self.css_url, headers=self._headers).text
        self.session.close()

    @staticmethod
    def img_position(string):
        # 过滤图片和价格在图片中的位置
        if 'url' in string:
            return re.findall(r'url\((.+?)\)', string)[0]
        else:
            return int((int(re.findall(r'\d+', string)[0]) - 4) / 25)

    @classmethod
    def css_filter(cls, _list, _str):
        # 过滤CSS文件，获取图片和价格在图片中的位置，并组装成字典
        _dict = dict()
        for each in _list:
            _tuple = re.findall(rf'({each}).*?{{(.+?)}}', _str)
            key = each
            value = list(map(lambda x: cls.img_position(x[1]), _tuple))
            _dict[key] = value
        return _dict

    # noinspection PyAttributeOutsideInit
    def run(self):
        self.css_class()
        self.css_html()
        css_dict = self.css_filter(self.class_list, self.css_str)
        price = recognize(css_dict)
        return price
        # self.data.from_ = ELONGC_NAME
        # self.data.canJump = 1
        # self.data.fromLogo = icon_list.ICON_ELONG
        # self.logger.debug(re.search(r'"otherTaxesAvg":(.*?)[\},]', json.dumps(resp_dict, ensure_ascii=False)).group(1))


if __name__ == '__main__':
    # BthHotelSpider(['075516', '2019-04-18', '2019-04-20']).set_log_level(10).get_result()
    print(BthHotelSpider('075516', '2019-04-18', '2019-04-20').run())
