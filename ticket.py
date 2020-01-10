# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-09 15:42
# @Version     : Python 3.6.8
# @Description :
import copy
import datetime
import json
import re
from base64 import b64decode
from time import sleep, time
from urllib.parse import unquote

import requests

from data.basedata import *
from data.constants import HEADERS
from data.setting import USERNAME, PASSWORD

from login_decrypt.fake_decrypt_12306 import DeviceApi
from utils import LogManager

logger = LogManager('12306').add_file_handler(10)


class Ticket(object):
    def __init__(self, is_query: bool = True):
        """
        12306 票务
        """
        self._is_query = is_query
        self.session = requests.session()
        self.session.headers = HEADERS
        # _login = Login(USERNAME, PASSWORD)
        # _is_login = _login.login()
        # if _is_login is True:
        #     self.session = _login.session

        # self.session = requests.session()
        # cookie_dict = {
        #     "JSESSIONID": "1664D79B84743E783BAEA26C1EED1C9A",
        #     "tk": "aTLJ7jP4S6hdDDfvpJxxsC38jz8vW8EXcQCjbw51L1L0",
        #     "_jc_save_toStation": "%u5F00%u5C01%2CKFF",
        #     "_jc_save_fromDate": "2019-11-25",
        #     "_jc_save_toDate": "2019-11-05",
        #     "_jc_save_wfdc_flag": "dc",
        #     "_jc_save_fromStation": "%u90D1%u5DDE%2CZZF",
        #     "RAIL_EXPIRATION": "1576787310474",
        #     "RAIL_DEVICEID": "O45-FklNK91cfh6Rn5yIwo05w-i2uESjlqT0y-B8nBqw6NXa3GKNHp_3SVq0wFI9CoJ3wFyXsVASA3ZpfpGDZwbzD1GH2nr56-79k1ck8sSzQaMWrTnkvuCJKb4jDR55dE8nrPeAkeUdem4GDx70HR14sWoaNumK",
        #     "BIGipServerpassport": "971505930.50215.0000",
        #     "route": "c5c62a339e7744272a54643b3be5bf64",
        #     "BIGipServerpool_passport": "317522442.50215.0000",
        #     "BIGipServerotn": "1641611530.24610.0000"
        # }
        # requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie_dict)

        if self._is_query:
            self.__get_query_ticket_url()

    def __get_query_ticket_url(self):
        """
        获取查询车票的链接
        :return:
        """
        index_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
        resp_str = self.session.request('get', index_url).content.decode("utf-8")
        self._cleft_ticket_url = re.search(r"CLeftTicketUrl = '([/\w]+)';", resp_str).group(1)

    @staticmethod
    def _gmt_time(date: str) -> str:
        """
        把日期转化为格林尼治时间
        :param date: 2019-09-30
        :return: Mon Sep 30 2019 00:00:00 GMT 0800 (中国标准时间)
        """
        # ['Mon', 'Sep', '30', '00:00:00', '2019']
        t_week, t_month, t_day, t_time, t_year = datetime.datetime.strptime(date, '%Y%m%d').ctime().split()
        return f'{t_week} {t_month} {t_day} {t_year} 00:00:00 GMT+0800 (中国标准时间)'

    def query_ticket(self, departure_date: str = None, from_station_name: str = '郑州',
                     to_station_name: str = '开封', is_student: bool = False) -> dict:
        """
        查询余票
        :param departure_date: 出发日期(2019-09-09)
        :param from_station_name: 出发地(上海)
        :param to_station_name: 目的地(北京)
        :param is_student: 是否学生(ADULT, 0X00)
        :return:
        """
        if departure_date is None:
            departure_date = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
        query_api = f'https://kyfw.12306.cn/otn/{self._cleft_ticket_url}'
        print(query_api)
        if from_station_name in STATION_DICT and to_station_name in STATION_DICT:
            query_param = {
                'leftTicketDTO.train_date': departure_date,
                'leftTicketDTO.from_station': STATION_DICT[from_station_name],
                'leftTicketDTO.to_station': STATION_DICT[to_station_name],
                'purpose_codes': '0X00' if is_student else 'ADULT'
            }
        else:
            raise ValueError('车站名称不正确')

        resp_dict = self.session.request('get', query_api, params=query_param).json()
        print(json.dumps(resp_dict))
        ticket_dict = {}
        if all(['status' in resp_dict,
                resp_dict['status'] is True,
                'data' in resp_dict,
                'result' in resp_dict['data']]):
            result_list = resp_dict['data']['result']
            for result in result_list:
                ticket = TicketParse(result)
                ticket_dict[ticket.station_train_code] = {
                    'secret_str': ticket.secretStr,
                    'train_code': ticket.station_train_code,
                    'from_station': TELECODE_STATION_DICT[ticket.from_station_telecode],
                    'to_station': TELECODE_STATION_DICT[ticket.to_station_telecode],
                    'start_station': TELECODE_STATION_DICT[ticket.start_station_telecode],
                    'end_station': TELECODE_STATION_DICT[ticket.end_station_telecode],
                    'start_time': ticket.start_time,
                    'arrive_time': ticket.arrive_time,
                    'duration': ticket.duration,
                    'business_seat': ticket.swz_num,
                    'first_class_seat': ticket.zy_num,
                    'second_class_seat': ticket.ze_num,
                    'high_grade_soft_berth': ticket.gr_num,
                    'soft_berth': ticket.rw_num,
                    'dong_wo': ticket.srrb_num,
                    'hard_berth': ticket.yw_num,
                    'soft_seat': ticket.rz_num,
                    'hard_seat': ticket.yz_num,
                    'no_seat': ticket.wz_num,
                    'other': ticket.qt_num,
                    'can_web_buy': ticket.canWebBuy,
                    'houbu_seat_limit': ticket.houbu_seat_limit,
                    'from_station_no': ticket.from_station_no,
                    'to_station_no': ticket.to_station_no,
                    'seat_types': ticket.seat_types,
                    'train_date': ticket.start_train_date,
                    'train_no': ticket.train_no,
                }
        return ticket_dict

    def query_price(self, train_no: str = '41000011480R', from_station_no: str = '11',
                    to_station_no: str = '12', seat_types: str = '1413', train_date: str = None) -> dict:
        """
        查询车票价格
        :param train_no: 列车号
        :param from_station_no: 出发站号
        :param to_station_no: 到达站号
        :param seat_types: 座位类型
        :param train_date: 出发日期
        :return:
        """
        # ('https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?'
        #  'train_no=240000D70901&from_station_no=01&to_station_no=04&seat_types=OIJ&train_date=2019-09-12')
        if train_date is None:
            train_date = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
        price_api = (f'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?'
                     f'train_no={train_no}&from_station_no={from_station_no}'
                     f'&to_station_no={to_station_no}&seat_types={seat_types}&train_date={train_date}')
        resp_dict = self.session.request('get', price_api).json()
        price_dict = {}
        if all(['status' in resp_dict, resp_dict['status'] is True, 'data' in resp_dict]):
            price_data: dict = resp_dict['data']
            price_dict['train_no'] = price_data['train_no']
            for key in price_data:
                if key in PRICE_DICT:
                    price_dict[PRICE_DICT[key]] = price_data[key]
            return price_dict

    def query_order(self, order_no, order_status: str = 'G', order_type: str = 'my_order') -> list:
        """
        通过订单号查询订单状态
        :param order_type: my_order: 全部订单, my_resign: 可改签订单, my_cs_resign: 可变更到站订单, my_refund: 可退票订单
        :param order_status: 订单状态, G: 未出行订单 H: 历史订单
        :param order_no: 订单号
        :return: 订单列表
        """
        _query_start_date = (datetime.datetime.now() - datetime.timedelta(29)).strftime('%Y-%m-%d')
        _query_end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        _query_data = {
            "come_from_flag": order_type,
            "pageIndex": "0",
            "pageSize": "8",
            "query_where": order_status,
            "queryStartDate": _query_start_date,
            "queryEndDate": _query_end_date,
            "queryType": "1",
            "sequeue_train_name": order_no
        }
        _query_api = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'
        order_dict = self.session.request('post', url=_query_api, data=_query_data).json()
        return order_dict['data']['OrderDTODataList']

    def query_no_complete_order(self):
        """
        查询未完成订单
        :return: 
        """
        _order_api = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
        _order_dict = self.session.request('post', _order_api, data={"_json_att": ""}).json()
        if _order_dict['status'] is True:
            return _order_dict['data']['orderDBList']

    def book(self, passenger_name_list: list = None, seat_type: str = '硬座', ticket_type: str = '成人票',
             train_date: str = None, from_station_name: str = '郑州', to_station_name: str = '开封',
             train_code: str = '1148'):
        """
        :param passenger_name_list: 乘车人名称列表
        :param seat_type: 座位类型
        :param ticket_type: 车票类型
        :param train_date: 出发日期
        :param from_station_name: 出发站名称
        :param to_station_name: 到达站名称
        :param train_code: 车次
        :return:
        """
        # 第零步
        if train_date is None:
            train_date = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
        check_api = 'https://kyfw.12306.cn/otn/login/checkUser'
        check_dict = self.session.request('post', check_api, data={'_json_att': ''}).json()
        print(json.dumps(check_dict))
        if not all(['status' in check_dict,
                    'data' in check_dict,
                    'flag' in check_dict['data'],
                    check_dict['data']['flag'] is True]):
            return False

        # 第一步
        ticket_dict = self.query_ticket(train_date, from_station_name, to_station_name)
        seat_type_code = SEAT_TYPE[seat_type]
        ticket_type_code = TICKET_TYPE[ticket_type]
        from_station_telecode = STATION_DICT[from_station_name]
        to_station_telecode = STATION_DICT[to_station_name]
        reserve_api = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        reserve_data = {
            'secretStr': unquote(ticket_dict[train_code]['secret_str']),
            'train_date': train_date,  # '2019-09-30'
            'back_train_date': datetime.datetime.now().strftime('%Y-%m-%d'),  # 默认当前日期 '2019-09-12
            'tour_flag': 'dc',
            'purpose_codes': '0X00' if ticket_type_code == '3' else 'ADULT',  # 'ADULT', '0X00'
            'query_from_station_name': from_station_name,  # '郑州',
            'query_to_station_name': to_station_name,  # '开封',
            'undefined': ''
        }
        reserve_dict = self.session.request('post', reserve_api, data=reserve_data).json()
        # {"validateMessagesShowId": "_validatorMessage", "status": false, "httpstatus": 200, "messages": ["\u60a8\u8fd8\u6709\u672a\u5904\u7406\u7684\u8ba2\u5355\uff0c\u8bf7\u60a8\u5230<a href=\"../view/train_order.html\">[\u672a\u5b8c\u6210\u8ba2\u5355]</a>\u8fdb\u884c\u5904\u7406!"], "validateMessages": {}}
        print(json.dumps(reserve_dict))
        if reserve_dict['status'] is False:
            return False

        # 第二步, 极其重要
        submit_order_api = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        submit_order_str = self.session.request('post', submit_order_api, data={'_json_att': ''}).content.decode(
            "utf-8")
        _essential_str = re.search('ticketInfoForPassengerForm=(.*?});', submit_order_str)
        _submit_token_str = re.search(r"globalRepeatSubmitToken = '(\w+)';", submit_order_str)
        if _essential_str and _submit_token_str:
            _essential_str = _essential_str.group(1).replace("'", '"')
            essential_dict = json.loads(_essential_str)
            print(json.dumps(essential_dict))
            submit_token = _submit_token_str.group(1)
        else:
            return False

        # 第三步
        passenger_api = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        passenger_data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        passenger_dict = {}
        passenger_resp_dict = self.session.request('post', passenger_api, data=passenger_data).json()
        print(json.dumps(passenger_resp_dict))
        if 'data' in passenger_resp_dict and 'normal_passengers' in passenger_resp_dict['data']:
            for normal_passenger in passenger_resp_dict['data']['normal_passengers']:
                passenger_dict[normal_passenger['passenger_name']] = normal_passenger
        else:
            return False

        # 第四步
        passenger_ticket_list = []
        old_passenger_list = []
        for passenger_name in passenger_name_list:
            if passenger_name in passenger_dict:
                passenger_info = passenger_dict[passenger_name]
                id_type = passenger_info['passenger_id_type_code']
                id_no = passenger_info['passenger_id_no']
                phone_no = passenger_info['mobile_no']
                all_enc_str = passenger_info['allEncStr']
                save_status = ""
                # seat_type: 座位类型: 硬座, 硬卧
                # ticket_type: 车票类型: 成人票, 儿童票
                # passenger_name: 乘车人姓名
                # id_type: 乘车人身份类型
                # id_no: 乘车人身份证编号
                # phone_no: 乘车人手机号
                passenger_ticket_list.append(
                    f'{seat_type_code},0,{ticket_type_code},{passenger_name},{id_type},{id_no},'
                    f'{"" if phone_no is None else phone_no},{"N" if save_status == "" else "Y"},{all_enc_str}'
                )
                old_passenger_list.append(
                    f'{passenger_name},{id_type},{id_no},{"" if phone_no is None else phone_no},'
                    f'{"N" if save_status == "" else "Y"},{all_enc_str}'
                )
        passenger_ticket_str = '_'.join(passenger_ticket_list)
        old_passenger_str = '_'.join(old_passenger_list) + '_'
        check_order_api = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        whats_select = '1'
        tour_flag = essential_dict['tour_flag']
        check_order_data = {
            'cancel_flag': "2",
            'bed_level_order_num': "000000000000000000000000000000",
            'passengerTicketStr': passenger_ticket_str,
            'oldPassengerStr': old_passenger_str,
            'tour_flag': tour_flag,
            'randCode': '',
            'whatsSelect': whats_select,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        _ = self.session.request('post', check_order_api, data=check_order_data)

        # 第五步
        ticket_num_api = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        ticket_info = essential_dict['queryLeftTicketRequestDTO']
        train_date = ticket_info['train_date']
        train_location = essential_dict['train_location']
        purpose_codes = ticket_info['purpose_codes']
        left_ticket_str = ticket_info.get('ypInfoDetail') or essential_dict['leftTicketStr']
        ticket_num_data = {
            'train_date': self._gmt_time(train_date),  # Mon Sep 30 2019 00:00:00 GMT+0800 (中国标准时间)
            'train_no': ticket_info['train_no'],  # 41000011480R
            'stationTrainCode': ticket_info['station_train_code'],
            'seatType': seat_type_code,
            'fromStationTelecode': from_station_telecode,
            'toStationTelecode': to_station_telecode,
            'leftTicket': left_ticket_str,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        ticket_num_dict = self.session.request('post', ticket_num_api, data=ticket_num_data).json()
        print(json.dumps(ticket_num_dict))
        if 'data' in ticket_num_dict and 'ticket' in ticket_num_dict['data']:
            ticket_num = ticket_num_dict['data']['ticket']  # 硬座格式:1,0;代表硬座 1 张,无座 0 张,其他座位类型:1(不带,)
        else:
            return False

        # 第六步
        key_check_is_change = essential_dict['key_check_isChange']
        seat_detail_type = (re.search(r'.*?id="x_no".*?>(\w+?)<', submit_order_str).group(1)
                            + re.search(r'.*?id="z_no".*?>(\w+?)<', submit_order_str).group(1)
                            + re.search(r'.*?id="s_no".*?>(\w+?)<', submit_order_str).group(1))
        confirm_api = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        confirm_data = {
            'passengerTicketStr': passenger_ticket_str,
            'oldPassengerStr': old_passenger_str,
            'randCode': '',
            'purpose_codes': purpose_codes,
            'key_check_isChange': key_check_is_change,
            'leftTicketStr': left_ticket_str,
            'train_location': train_location,
            'choose_seats': '',
            'seatDetailType': seat_detail_type,
            'whatsSelect': whats_select,
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        confirm_dict = self.session.request('post', confirm_api, data=confirm_data).json()
        print(json.dumps(confirm_dict))
        if not all(['data' in confirm_dict,
                    'submitStatus' in confirm_dict['data'],
                    confirm_dict['data']['submitStatus'] is True]):
            return False

        # 第七步
        sleep(5)
        wait_api = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        wait_params = {
            'random': int(time() * 1000),
            'tourFlag': tour_flag,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        wait_dict = self.session.request('get', wait_api, params=wait_params).json()
        print(json.dumps(wait_dict))
        if all(['status' in wait_dict,
                wait_dict['status'] is True,
                'data' in wait_dict,
                'orderId' in wait_dict['data']]):
            order_id = wait_dict['data']['orderId']
        else:
            return False

        # 第八步
        result_api = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        result_data = {
            'orderSequence_no': order_id,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': submit_token
        }
        result_dict = self.session.request('post', result_api, data=result_data).json()
        print(json.dumps(result_dict))
        if all(['data' in result_dict,
                'submitStatus' in result_dict['data'],
                result_dict['data']['submitStatus'] is True]):
            return True
        else:
            return False

    def cancel(self, order_no) -> bool:
        """
        取消订单
        :param order_no: 订单号
        :return: {
            "validateMessagesShowId": "_validatorMessage",
            "status": true,
            "httpstatus": 200,
            "data": {
                "existError": "N"
            },
            "messages": [],
            "validateMessages": {}
        }
        """
        _cancel_api = 'https://kyfw.12306.cn/otn/queryOrder/cancelNoCompleteMyOrder'
        _cancel_data = {
            'sequence_no': order_no,
            'cancel_flag': 'cancel_order'
        }
        _cancel_dict = self.session.request('post', _cancel_api, data=_cancel_data).json()
        print(json.dumps(_cancel_dict))
        return _cancel_dict['status']

    def refund(self, order_no, passenger_name):
        """
        退票
        :param order_no: 订单号
        :param passenger_name: 乘车人姓名
        :return: {
            'code': 507,
            'data': {
                "validateMessagesShowId":"_validatorMessage",
                "status":true,
                "httpstatus":200,
                "data":{
                    "errMsg":"该票不允许退票，请到我的订单中查询车票状态！"
                },
                "messages":[],
                "validateMessages":{}
            },
            'message': '退票失败'
        }
        """
        _order_list = self.query_order(order_no)
        if not _order_list:
            return {
                'code': 507,
                'data': {},
                'message': '订单不存在'
            }
        ticket_info = None
        for order_info in _order_list[0]['tickets']:
            if passenger_name == order_info.get('passengerDTO', {}).get('passenger_name'):
                ticket_info = order_info
                break
        if ticket_info is None:
            return {
                'code': 507,
                'data': {},
                'message': f'订单中不存在乘车人: {passenger_name} 的信息'
            }
        _refund_api = 'https://kyfw.12306.cn/otn/queryOrder/returnTicketAffirm'
        _refund_data = {
            "sequence_no": ticket_info['sequence_no'],
            "batch_no": ticket_info['batch_no'],
            "coach_no": ticket_info['coach_no'],
            "seat_no": ticket_info['seat_no'],
            "start_train_date_page": ticket_info['start_train_date_page'],
            "train_code": ticket_info['stationTrainDTO']['trainDTO']['train_code'],
            "coach_name": ticket_info['coach_name'],
            "seat_name": ticket_info['seat_name'],
            "seat_type_name": ticket_info['seat_type_name'],
            "train_date": ticket_info['train_date'],
            "from_station_name": ticket_info['stationTrainDTO']['from_station_name'],
            "to_station_name": ticket_info['stationTrainDTO']['to_station_name'],
            "start_time": ticket_info['stationTrainDTO']['start_time'],
            "passenger_name": passenger_name,
            "from_station_telecode": ticket_info['stationTrainDTO']['from_station_telecode'],
            "to_station_telecode": ticket_info['stationTrainDTO']['to_station_telecode'],
            "train_no": ticket_info['stationTrainDTO']['trainDTO']['train_no'],
            "id_type": ticket_info['passengerDTO']['passenger_id_type_code'],
            "id_no": ticket_info['passengerDTO']['passenger_id_no'],
            "_json_att": ""
        }
        refund_dict = self.session.request('post', url=_refund_api, data=_refund_data).json()['data']
        print(json.dumps(refund_dict))
        _validate_api = 'https://kyfw.12306.cn/otn/queryOrder/returnTicket'
        _validate_dict = self.session.request('post', url=_validate_api).json()
        # print(json.dumps(resp_dict))
        _err_msg = _validate_dict['data'].get('errmes')
        if _err_msg:
            return {
                'code': 507,
                'data': _err_msg,
                'message': '退票失败'
            }
        else:
            return {
                'code': 200,
                'data': {
                    'passenger_name': refund_dict['passengerDTO']['passenger_name'],
                    'train_no': refund_dict['stationTrainDTO']['station_train_code'],
                    'station': (f"{refund_dict['stationTrainDTO']['from_station_name']}-"
                                f"{refund_dict['stationTrainDTO']['to_station_name']}"),
                    'coach_no': refund_dict['coach_no'],
                    'seat_name': refund_dict['seat_name'],
                    'seat_type_name': refund_dict['seat_type_name'],
                    'return_price': refund_dict['return_price']
                },
                'message': '退票成功'
            }

    def passengers(self) -> dict:
        """
        获取常用联系人信息
        :return: {
            'code': 200,
            'data': passenger_list,
            'message': '获取乘车人成功'
        }
        """
        _passenger_url = 'https://kyfw.12306.cn/otn/passengers/query'
        _passenger_data = {
            'pageIndex': 1,
            'pageSize': 100
        }
        passenger_list = []
        try:
            _passenger_dict = self.session.request('post', _passenger_url, data=_passenger_data).json()
            for passenger_info in _passenger_dict['data']['datas']:
                total_times = passenger_info['total_times']
                passenger_id_type_code = passenger_info['passenger_id_type_code']
                if passenger_id_type_code == '2':
                    passenger_status = '未通过'
                elif total_times in ['95', '97']:
                    if total_times == '97' and passenger_id_type_code in ['C', 'G']:
                        passenger_status = '预通过'
                    else:
                        passenger_status = '已通过'
                elif total_times in ['93', '99']:
                    if passenger_id_type_code != 'B':
                        passenger_status = '已通过'
                    else:
                        passenger_status = '预通过'
                elif total_times in ['94', '96']:
                    passenger_status = '未通过'
                elif total_times in ['92', '98']:
                    if passenger_id_type_code == 'B':
                        passenger_status = '请报验'
                    else:
                        passenger_status = '待核验'
                elif total_times == '91':
                    if passenger_id_type_code == 'B':
                        passenger_status = '请报验'
                    else:
                        passenger_status = '待核验'
                else:
                    passenger_status = '未知状态'
                passenger_list.append({
                    'passenger_name': passenger_info['passenger_name'],
                    'passenger_id_type_code': passenger_info['passenger_id_type_code'],
                    'passenger_id_type_name': passenger_info['passenger_id_type_name'],
                    'passenger_id_no': passenger_info['passenger_id_no'],
                    'mobile_no': passenger_info['mobile_no'] if 'mobile_no' in passenger_info else None,
                    'passenger_type_code': passenger_info['passenger_type'],
                    'passenger_type_name': passenger_info['passenger_type_name'],
                    'passenger_status': passenger_status
                })
            return {
                'code': 200,
                'data': passenger_list,
                'message': '获取乘车人成功'
            }
        except Exception as e:
            logger.error(f'获取乘车人失败.\n{e}', exc_info=1)
        return {
            'code': 506,
            'data': passenger_list,
            'message': '获取乘车人失败'
        }

    def add_passenger(self, passenger_params):
        """
        添加常用联系人
        :param passenger_params: 常用联系人基本数据
        :return: 
        """
        vp = ValidateParams(passenger_params)
        err_msg = vp.validate()
        if err_msg:
            return {
                'code': 508,
                'data': err_msg,
                'message': 'Failure'
            }
        else:
            _add_api = 'https://kyfw.12306.cn/otn/passengers/add'
            _add_data = vp.get_data()
            resp_dict = self.session.request('post', url=_add_api, data=_add_data).json()
            msg = resp_dict['data'].get('flag')
            if msg is True:
                return {
                    'code': 200,
                    'data': '添加常用联系人成功',
                    'message': 'Success'
                }
            else:
                return {
                    'code': 508,
                    'data': '添加常用联系人失败',
                    'message': 'Failure'
                }

    def _schools(self) -> dict:
        """
        获取支持学生票的学校
        :return:
        """
        school_api = 'https://kyfw.12306.cn/otn/userCommon/schoolNames'
        resp_dict = self.session.request('post', school_api, data={'provinceCode': 1}).json()
        print(json.dumps(resp_dict))
        return resp_dict

    def _cities(self) -> dict:
        """
        获取支持学生票的城市
        :return:
        """
        city_api = 'https://kyfw.12306.cn/otn/userCommon/allCitys'
        resp_dict = self.session.request('post', city_api, data={'station_name': ''}).json()
        print(json.dumps(resp_dict))
        return resp_dict

    def _stations(self) -> list:
        """
        获取所有车站
        :return:
        """
        station_js = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9109'
        resp_str = self.session.request('get', station_js).content.decode("utf-8")
        station_list = []
        for station_info in resp_str.replace("var station_names ='@", "").replace("';", "").split("@"):
            short_pinyin, name_cn, name_en, pinyin, _, station_id = station_info.split('|')
            station_list.append({
                'short_pinyin': short_pinyin,
                'name_cn': name_cn,
                'name_en': name_en,
                'pinyin': pinyin,
                'station_id': station_id
            })
        print(json.dumps(station_list))
        return station_list


class TicketParse(object):
    def __init__(self, ticket: str):
        """
        12306 车票解析
        :param ticket: 车票数据
        """
        (secretStr, buttonTextInfo, train_no, station_train_code, start_station_telecode,
         end_station_telecode, from_station_telecode, to_station_telecode, start_time,
         arrive_time, duration, canWebBuy, yp_info, start_train_date, train_seat_feature,
         location_code, from_station_no, to_station_no, is_support_card, controlled_train_flag,
         gg_num, gr_num, qt_num, rw_num, rz_num, tz_num, wz_num, yb_num, yw_num, yz_num,
         ze_num, zy_num, swz_num, srrb_num, yp_ex, seat_types, exchange_train_flag, houbu_train_flag,
         *a, houbu_seat_limit) = ticket.split('|')
        self.secretStr = secretStr  # 加密串
        self.buttonTextInfo = buttonTextInfo  # 备注
        self.train_no = train_no  # 列车号
        self.station_train_code = station_train_code  # 车次
        self.start_station_telecode = start_station_telecode  # 始发站
        self.end_station_telecode = end_station_telecode  # 终点站
        self.from_station_telecode = from_station_telecode  # 出发站
        self.to_station_telecode = to_station_telecode  # 到达站
        self.start_time = start_time  # 出发时间
        self.arrive_time = arrive_time  # 到达时间
        self.duration = duration  # 历时
        self.canWebBuy = canWebBuy  # 是否可购买
        self.yp_info = yp_info  # 余票信息
        self.start_train_date = start_train_date  # 出发日期
        self.train_seat_feature = train_seat_feature
        self.location_code = location_code
        self.from_station_no = from_station_no
        self.to_station_no = to_station_no
        self.is_support_card = is_support_card  # 是否支持二代身份证进出站
        self.controlled_train_flag = controlled_train_flag
        self.gg_num = gg_num
        self.gr_num = gr_num  # 高级软卧
        self.qt_num = qt_num  # 其它
        self.rw_num = rw_num  # 软卧
        self.rz_num = rz_num  # 软座
        self.tz_num = tz_num
        self.wz_num = wz_num  # 无座
        self.yb_num = yb_num
        self.yw_num = yw_num  # 硬卧
        self.yz_num = yz_num  # 硬座
        self.ze_num = ze_num  # 二等座
        self.zy_num = zy_num  # 一等座
        self.swz_num = swz_num  # 商务座
        self.srrb_num = srrb_num  # 动卧
        self.yp_ex = yp_ex  # 余票额外信息
        self.seat_types = seat_types  # 座位类型
        self.exchange_train_flag = exchange_train_flag  # 是否为小运转列车
        self.houbu_train_flag = houbu_train_flag  # 是否为候补列车
        self.houbu_seat_limit = houbu_seat_limit  # 候补座位限制 哪些座位不能候补


class Login(object):
    def __init__(self, username: str, password: str):
        """
        # 12306 登录
        :param username: 12306 账号
        :param password: 12306 密码
        """
        self.session = requests.session()
        self.session.headers = HEADERS
        self._username = username
        self._password = password

    @staticmethod
    def _current_time() -> int:
        return int(time() * 1000)

    def _current_time_str(self) -> str:
        return str(self._current_time())

    def _index(self):
        """
        请求主页,添加会话
        :return:
        """
        login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self._request_index_time = self._current_time()
        _ = self.session.request('get', login_url)

    def _set_device_cookie(self):
        device_api = DeviceApi().get_device_api()
        resp_str = self.session.request('get', url=device_api).content.decode("utf-8")
        logger.debug(f"设备特征接口返回数据：{resp_str}")
        rail_expiration = re.search('"exp":"(.+?)"', resp_str).group(1)
        rail_deviceid = re.search('"dfp":"(.+?)"', resp_str).group(1)
        self.session.cookies.set("RAIL_EXPIRATION", rail_expiration)
        self.session.cookies.set("RAIL_DEVICEID", rail_deviceid)

    def _get_captcha(self, *, image_path: str = None, is_show_image: bool = False) -> str:
        """
        获取验证码图片
        :param image_path: 验证码存储路径
        :param is_show_image: 是否展示验证码
        :return: 验证码的base64加密流
        """
        captcha_api = 'https://kyfw.12306.cn/passport/captcha/captcha-image64'
        captcha_params = {
            'login_site': 'E',
            'module': 'login',
            'rand': 'sjrand',
            self._current_time_str(): '',
            'callback': 'callback',
            '_': self._request_index_time
        }
        captcha_resp = self.session.request('get', captcha_api, params=captcha_params)
        captcha_resp_dict = json.loads(
            captcha_resp.content.decode("utf-8").replace('/**/callback(', '').replace(');', ''))
        img_bytes = b64decode(captcha_resp_dict['image'])
        # img_byte_array = bytearray(img_bytes)
        # if is_show_image:
        #     image = np.asarray(img_byte_array, dtype="uint8")
        #     image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        #     cv2.imshow('image_show', image)
        #     cv2.waitKey(15000)

        # 写入验证码
        if image_path:
            with open(image_path, 'wb') as fw:
                fw.write(img_bytes)
        return img_bytes

    def _check_captcha(self, index_list: list) -> dict:
        """
        验证码校验
        :param index_list: 验证码序号列表
        :return: 验证码校验是否正确的相关信息
        """
        captcha_check_api = 'https://kyfw.12306.cn/passport/captcha/captcha-check'

        # 验证码点击的位置
        answer = ','.join([IMAGE_LOCATION_DICT[str(index)] for index in index_list])
        logger.info(f"验证码位置：{answer}")

        captcha_check_params = {
            'callback': 'callback',
            'answer': answer,
            'rand': 'sjrand',
            'login_site': 'E',
            '_': self._request_index_time
        }

        # 查看是否验证成功
        resp_str = self.session.request('get', captcha_check_api, params=captcha_check_params).content.decode("utf-8")
        # {"result_message":"验证码校验失败,信息为空","result_code":"8"}
        resp_dict = json.loads(resp_str.replace('/**/callback({', '{').replace('});', '}'))
        logger.debug(f"验证码校验接口返回数据：{resp_dict}")
        return resp_dict

    def _login(self) -> dict:
        """
        请求登录接口
        :return: 是否登陆成功的相关信息
        """
        login_api = 'https://kyfw.12306.cn/passport/web/login'
        login_data = {
            'username': self._username,
            'password': self._password,
            'appid': 'otn'
        }
        # {'result_message': '密码输入错误。如果输错次数超过4次，用户将被锁定。', 'result_code': 1}
        resp_dict = self.session.request('post', login_api, data=login_data).json()
        logger.debug(f"请求登录接口返回数据：{resp_dict}")
        return resp_dict

    def _check_login_first(self) -> dict:
        uamtk_api = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        headers = copy.deepcopy(HEADERS)
        headers['Referer'] = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
        # {'result_message': '用户未登录', 'result_code': 1}
        resp_dict = self.session.request('post', uamtk_api, headers=headers, data={'appid': 'otn'}).json()
        logger.info(f"第一次检查登录接口返回数据：{resp_dict}")
        return resp_dict

    def _check_login_second(self, tk: str) -> dict:
        uamauthclient_api = 'https://kyfw.12306.cn/otn/uamauthclient'
        resp_dict = self.session.request('post', uamauthclient_api, data={'tk': tk}).json()
        logger.info(f"第二次检查登录接口返回数据：{resp_dict}")
        return resp_dict

    def login(self):
        """
        12306 登录
        :return:
        """

        self._index()
        self._set_device_cookie()

        # 获取验证码
        img_path = f'{self._username}.png'
        self._get_captcha(image_path=img_path)

        # 验证码校验
        index_str = input('请输入验证码位置: ')
        msg = self._check_captcha(index_str.split())
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != '4' or result_message != '验证码校验成功':
            return False

        # 登录
        _login_dict = self._login()
        if _login_dict.get('result_code') is not 0 or _login_dict.get('result_message') != '登录成功':
            return False

        # 第一次检查登录状态
        msg = self._check_login_first()
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != 0 or result_message != '验证通过':
            return False

        # 第二次检查登录状态
        tk = msg.get('newapptk')
        msg = self._check_login_second(tk)
        result_message = msg.get('result_message')
        result_code = msg.get('result_code')
        if result_code != 0 or result_message != '验证通过':
            return False

        logger.info(f"登录后的cookie：{requests.utils.dict_from_cookiejar(self.session.cookies)}")
        return True


class AddPassengerParams(object):
    def __init__(self, passenger_params: dict):
        """
        添加常用联系人参数
        :param passenger_params: 常用联系人参数
        """
        self.passenger_name = passenger_params['passenger_name']
        self._sex = passenger_params['sex']
        self.sex_code = self.__get_sex_code()
        self.passenger_id_no = passenger_params['passenger_id_no']
        self.mobile_no = passenger_params.get('mobile_no', '')
        self.phone_no = passenger_params.get('phone_no', '')
        self.email = passenger_params.get('email', '')
        self.address = passenger_params.get('address', '')
        self.postalcode = passenger_params.get('postalcode', '')
        self.school_name = passenger_params.get('school_name', '北京大学')
        self.school_code = self.__get_school_code()
        self.department = passenger_params.get('department', '')
        self.school_class = passenger_params.get('school_class', '')
        self.student_no = passenger_params['student_no']
        self.preference_card_no = passenger_params.get('preference_card_no', '')
        self.GAT_valid_date_end = passenger_params.get('GAT_valid_date_end', '')
        self.GAT_born_date = passenger_params.get('GAT_born_date', '')
        self.old_passenger_name = passenger_params.get('old_passenger_name', '')
        self._country_name = passenger_params.get('country_name', '中国CHINA')
        self.country_code = self.__get_country_code()
        self._birthDate = '2017-01-05'
        self.old_passenger_id_type_code = passenger_params.get('old_passenger_id_type_code', '')
        self._passenger_id_type_name = passenger_params['passenger_id_type_name']
        self.passenger_id_type_code = self.__get_passenger_id_code()
        self.old_passenger_id_no = passenger_params.get('old_passenger_id_no', '')
        self._passenger_type_name = passenger_params['passenger_type_name']
        self.passenger_type = self.__get_passenger_code()
        self._province_name = passenger_params.get('province_name', '北京')
        self.province_code = self.__get_province_code()
        self.school_system = passenger_params.get('school_system', '1')
        self.enter_year = passenger_params.get('enter_year', '2019')
        self.preference_from_station_name = passenger_params.get('preference_from_station_name', '简码/汉字')
        self.preference_from_station_code = self.__get_from_station_code()
        self.preference_to_station_name = passenger_params.get('preference_to_station_name', '简码/汉字')
        self.preference_to_station_code = self.__get_to_station_code()

    def get_data(self):
        return {
            "passenger_name": self.passenger_name,
            "sex_code": self.sex_code,
            "passenger_id_no": self.passenger_id_no,
            "mobile_no": self.mobile_no,
            "phone_no": self.phone_no,
            "email": self.email,
            "address": self.address,
            "postalcode": self.postalcode,
            "studentInfoDTO.school_code": self.school_code,
            "studentInfoDTO.school_name": self.school_name,
            "studentInfoDTO.department": self.department,
            "studentInfoDTO.school_class": self.school_class,
            "studentInfoDTO.student_no": self.student_no,
            "studentInfoDTO.preference_card_no": self.preference_card_no,
            "GAT_valid_date_end": self.GAT_valid_date_end,
            "GAT_born_date": self.GAT_born_date,
            "old_passenger_name": self.old_passenger_name,
            "country_code": self.country_code,
            "_birthDate": self._birthDate,
            "old_passenger_id_type_code": self.old_passenger_id_type_code,
            "passenger_id_type_code": self.passenger_id_type_code,
            "old_passenger_id_no": self.old_passenger_id_no,
            "passenger_type": self.passenger_type,
            "studentInfoDTO.province_code": self.province_code,
            "studentInfoDTO.school_system": self.school_system,
            "studentInfoDTO.enter_year": self.enter_year,
            "studentInfoDTO.preference_from_station_name": self.preference_from_station_name,
            "studentInfoDTO.preference_from_station_code": self.preference_from_station_code,
            "studentInfoDTO.preference_to_station_name": self.preference_to_station_name,
            "studentInfoDTO.preference_to_station_code": self.preference_to_station_code
        }

    def __get_school_code(self):
        if self.school_name in SCHOOL_MAP:
            return SCHOOL_MAP[self.school_name]
        else:
            return '10001'

    def __get_passenger_id_code(self):
        if self._passenger_id_type_name in PASSENGER_ID_MAP:
            return PASSENGER_ID_MAP[self._passenger_id_type_name]
        else:
            return '1'

    def __get_sex_code(self):
        if self._sex in GENDER_MAP:
            return GENDER_MAP[self._sex]
        else:
            return 'M'

    def __get_passenger_code(self):
        if self._passenger_type_name in PASSENGER_MAP:
            return PASSENGER_MAP[self._passenger_type_name]
        else:
            return '1'

    def __get_country_code(self):
        if self._country_name in COUNTRY_MAP:
            return COUNTRY_MAP[self._country_name]
        else:
            return 'CN'

    # def __get_birthday(self):
    #     return f'{self.id_number[6:10]}-{self.id_number[10:12]}-{self.id_number[12:14]}'

    def __get_province_code(self):
        if self._province_name in PROVINCE_MAP:
            return PROVINCE_MAP[self._province_name]
        else:
            return '11'

    def __get_from_station_code(self):
        if self.preference_from_station_name in STATION_MAP:
            return STATION_MAP[self.preference_from_station_name]
        else:
            return ''

    def __get_to_station_code(self):
        if self.preference_to_station_name in STATION_MAP:
            return STATION_MAP[self.preference_to_station_name]
        else:
            return ''


class ValidateParams(AddPassengerParams):
    def __init__(self, passenger_params):
        """
        验证参数合法性
        :param passenger_params: 参数
        """
        super().__init__(passenger_params)

    @staticmethod
    def _validate_username(username):
        if re.compile('^[A-Za-z0-9][A-Za-z0-9_]{0,29}$').fullmatch(username):
            return True
        else:
            return False

    @staticmethod
    def __id_card_update(_str):
        id_card_15 = re.compile(r'^(\d){15}$')
        if id_card_15.fullmatch(_str):
            temp = 0
            int_list = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            char_list = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
            _str = _str[0:6] + '1' + '9' + _str[6:]
            for i in _str:
                temp += int(_str[i: i + 1]) * int_list[i]
            _str += char_list[temp % 11]
            id_card_18 = _str
        else:
            id_card_18 = '#'
        return id_card_18

    @staticmethod
    def __is_validate_date(_str):
        try:
            datetime.datetime.strptime(_str, '%Y-%m-%d')
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def __only_eng_cn(value):
        # 学号 院系 班级 优惠卡号
        if value:
            if re.compile('^[a-zA-Z\u3400-\u9FFF0-9_]+$').fullmatch(value):
                return True
            else:
                return False
        else:
            return True

    def _validate_passenger_id_no(self):
        if self.passenger_id_type_code in ['1', '2']:
            if self.passenger_id_no.__len__() == 15:
                sid = self.__id_card_update(self.passenger_id_no)
            else:
                sid = self.passenger_id_no
            if not re.compile(r'^\d{17}(\d|x)$', re.I).fullmatch(sid):
                return False
            sid = re.sub('[xX]$', 'a', sid)

            # 非法地区
            if CITY_MAP[int(sid[0:2])] is None:
                return False

            # 非法生日
            birthday = sid[6:10] + '-' + sid[10:12] + '-' + sid[12:14]
            if not self.__is_validate_date(birthday):
                return False
            _sum = 0
            for i in range(sid.__len__() - 1, -1, -1):
                _sum += (pow(2, int(i)) % 11) * int(sid[17 - i], 11)
            if _sum % 11 != 1:
                return False
            return True
        if self.passenger_id_type_code == 'H':
            # foreigner
            return bool(re.compile('^[a-zA-Z]{3}[0-9]{12}$').fullmatch(self.passenger_id_no))
        elif self.passenger_id_type_code == '1':
            if self.passenger_id_no[:2] in ['81', '82', '83']:
                return False
        return True

    def _validate_mobile_no(self):
        if self.mobile_no:
            if re.compile(r'^1[3-9][0-9]\d{8}$').findall(self.mobile_no):
                return True
            else:
                return False
        else:
            return True

    def _validate_phone_no(self):
        if self.phone_no:
            if re.compile(r'(^[0-9]{3,4}-[0-9]{3,8}$)|(^[0-9]{3,8}$)|(^[0-9]{3,4}\)[0-9]{3,8}$)'
                          r'|(^0?13[0-9]{9}#)').fullmatch(self.phone_no):
                return True
            else:
                return False
        else:
            return True

    def _validate_passenger_name(self):
        if self.passenger_id_type_code in ['1', '2']:
            return bool(re.compile('^[a-zA-Z·.．\u3400-\u9FFF]+$').fullmatch(self.passenger_name))
        elif self.passenger_id_type_code == 'B':
            if re.compile('^[-]+$').fullmatch(self.passenger_name):
                return False
            else:
                return bool(re.compile(r'^[a-z A-Z·.．\u3400-\u9FFF\-]+$').fullmatch(self.passenger_name))
        elif self.passenger_id_type_code == 'H':
            return True
        else:
            return bool(re.compile('^[a-z A-Z·.．\u3400-\u9FFF]+$').fullmatch(self.passenger_name))

    def _validate_passenger_id_type(self):
        if self.passenger_id_type_code == 'C':
            # hongkong macao
            return bool(re.compile('^[HMhm]([0-9]{8})$').fullmatch(self.passenger_id_no))
        elif self.passenger_id_type_code == 'G':
            # taiwan
            return bool(re.compile('^[0-9]{8}$').fullmatch(self.passenger_id_no))
        elif self.passenger_id_type_code == 'B':
            # passport
            return bool(re.compile('^[a-zA-Z0-9]{5,17}$').fullmatch(self.passenger_id_no))
        else:
            return True

    def _validate_postalcode(self):
        if self.postalcode:
            if re.compile('^[0-9]{6}$').fullmatch(self.postalcode):
                return True
            else:
                return False
        else:
            return True

    def _validate_email(self):
        if self.email:
            if (re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])"
                           r"?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$").fullmatch(self.email) and
                    re.compile(r'^([a-zA-Z0-9_.\-])+@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$').fullmatch(self.email)):
                return True
            else:
                return False
        else:
            return True

    def _validate_address(self):
        for illegal_char in ''''"<>?$''':
            if illegal_char in self.address:
                return False
        return True

    def _validate_student_no(self):
        return self.__only_eng_cn(self.student_no)

    def _validate_department(self):
        return self.__only_eng_cn(self.department)

    def _validate_school_class(self):
        return self.__only_eng_cn(self.school_class)

    def _validate_preference_card_no(self):
        return self.__only_eng_cn(self.preference_card_no)

    # def validate(self):
    #     err_msg = {}
    #     if not self._validate_passenger_id_no():
    #         err_msg['passenger_id_no_error'] = '请输入正确的证件号码'
    #     if not self._validate_mobile_no():
    #         err_msg['mobile_no_error'] = '您输入的手机号码不是有效的格式'
    #     if not self._validate_phone_no():
    #         err_msg['phone_no_error'] = '您输入的固定电话格式不正确'
    #     if not self._validate_passenger_name():
    #         err_msg['passenger_name_error'] = '请输入正确的姓名'
    #     if not self._validate_passenger_id_type():
    #         err_msg['passenger_id_type_error'] = '证件号码与证件类型不符'
    #     if not self._validate_postalcode():
    #         err_msg['postalcode_error'] = '您输入的邮编不是有效的格式'
    #     if not self._validate_email():
    #         err_msg['email_error'] = '请输入有效的电子邮件地址'
    #     if not self._validate_address():
    #         err_msg['address_error'] = '您输入的地址中含有非法字符'
    #     if not self._validate_student_no():
    #         err_msg['student_no_error'] = '学号只能包含中文、英文、数字'
    #     if not self._validate_department():
    #         err_msg['department_error'] = '院系只能包含中文、英文、数字'
    #     if not self._validate_school_class():
    #         err_msg['school_class_error'] = '班级只能包含中文、英文、数字'
    #     if not self._validate_preference_card_no():
    #         err_msg['preference_card_no_error'] = '优惠卡号只能包含中文、英文、数字'
    #     return err_msg
    def validate(self) -> str:
        if not self._validate_passenger_id_no():
            err_msg = '请输入正确的证件号码'
        elif not self._validate_mobile_no():
            err_msg = '您输入的手机号码不是有效的格式'
        elif not self._validate_phone_no():
            err_msg = '您输入的固定电话格式不正确'
        elif not self._validate_passenger_name():
            err_msg = '请输入正确的姓名'
        elif not self._validate_passenger_id_type():
            err_msg = '证件号码与证件类型不符'
        elif not self._validate_postalcode():
            err_msg = '您输入的邮编不是有效的格式'
        elif not self._validate_email():
            err_msg = '请输入有效的电子邮件地址'
        elif not self._validate_address():
            err_msg = '您输入的地址中含有非法字符'
        elif not self._validate_student_no():
            err_msg = '学号只能包含中文、英文、数字'
        elif not self._validate_department():
            err_msg = '院系只能包含中文、英文、数字'
        elif not self._validate_school_class():
            err_msg = '班级只能包含中文、英文、数字'
        elif not self._validate_preference_card_no():
            err_msg = '优惠卡号只能包含中文、英文、数字'
        else:
            err_msg = ''
        return err_msg


class Test12306(object):
    def test_login(self):
        result = Login(USERNAME, PASSWORD).login()
        print(json.dumps(result, indent=4, ensure_ascii=False))

    def test_book(self):
        result = Ticket().book(passenger_name_list=['LJQ'])
        print(json.dumps(result, indent=4, ensure_ascii=False))

    def test_refund(self):
        result = Ticket().refund('Exxxxx', 'LJQ')
        print(json.dumps(result, indent=4, ensure_ascii=False))

    def test_cancel(self):
        result = Ticket().cancel('Exxxxx')
        print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    # t = Test12306()
    # t.test_login()
    # t = Ticket()
    # r = t.query_ticket('2020-02-01')
    # print(json.dumps(r))
    # print(r.__len__())
    r = Login(USERNAME, PASSWORD).login()
    print(r)
