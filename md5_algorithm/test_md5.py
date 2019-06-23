# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/23 10:23
# @Version     : Python 3.7
# @Description : test my md5 algorithm
from _md5 import md5

from md5_algorithm.message_digest_algorithm_5 import message_digest_algorithm

if __name__ == '__main__':
    encrypted_message = '12345678'
    # official md5 algorithm
    print(md5(encrypted_message.encode()).hexdigest())
    # my md5 algorithm
    print(message_digest_algorithm(encrypted_message))
