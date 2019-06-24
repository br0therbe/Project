# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/24 10:31
# @Version     : Python 3.6.8
# @Description :
import random


class CreateTestData(object):
    def __init__(self, data_list_length: int = 100, create_random_num_limit: int = 20):
        # self.test_name_list = ['int', 'float']
        self.data_list_length = data_list_length
        self.create_random_num_limit = create_random_num_limit

    def create_int_data(self):
        data_list = [random.randint(-self.create_random_num_limit, self.create_random_num_limit)
                     for _ in range(self.data_list_length)]
        return data_list

    def create_float_data(self, decimal_place: int = 2):
        data_list = [round(random.randint(-self.create_random_num_limit, self.create_random_num_limit)
                           + random.random(), decimal_place) for _ in range(self.data_list_length)]
        return data_list

    def create_str_data(self, str_length: int = 10):
        # _str = [chr(i) for i in range(ord("a"), ord("z") + 1)]
        _str = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
        data_list = []
        for _ in range(self.data_list_length):
            data_list.append(''.join([random.choice(_str) for _o_ in range(str_length)]))
        return data_list


if __name__ == '__main__':
    ctd = CreateTestData()
    data_list = ctd.create_str_data()
    print(data_list)
