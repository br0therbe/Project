# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/22 7:29
# @Version     : Python 3.7
# @Description : md5 algorithm in python
from algorithm_common import byte2int, int2hex
from md5_algorithm.md5_constants import (CHILDREN_GROUP_BYTE_LENGTH, CYCLE_LENGTH, FIXED_RANDOM_NUMBER_LIST,
                                         LEFT_SHIFT_LIST, GROUP_BYTE_LENGTH, REMAINDER_BYTE_LENGTH,
                                         CHILDREN_GROUP_BIT_LENGTH, FIRST_NUMBER, SECOND_NUMBER, THIRD_NUMBER,
                                         FOURTH_NUMBER)

A, B, C, D = FIRST_NUMBER, SECOND_NUMBER, THIRD_NUMBER, FOURTH_NUMBER


def cycle_left_shift(to_be_shifted_number: int, shift_length: int) -> int:
    """
    无符号数循环左移
    :param to_be_shifted_number: 待移动的数
    :param shift_length: 移动位数
    :return: 移动后的整数
    """
    return (to_be_shifted_number << shift_length) | (to_be_shifted_number >> CHILDREN_GROUP_BIT_LENGTH - shift_length)


def cycle_algorithm(fixed_length_byte):
    """
    组内循环算法，组内执行 64 次，共 4 个函数各 16 次
    :param fixed_length_byte: 定长的数组，长度 64 字节，512 比特
    :return: 运算后的 A, B, C, D，都是整形
    """
    global A, B, C, D
    groups = [byte2int(fixed_length_byte[CHILDREN_GROUP_BYTE_LENGTH * i:CHILDREN_GROUP_BYTE_LENGTH * (i + 1)])
              for i in range(len(fixed_length_byte) // CHILDREN_GROUP_BYTE_LENGTH)]

    a, b, c, d = A, B, C, D
    for index in range(CYCLE_LENGTH):
        if index < 16:
            f = (b & c) | ((~b) & d)
            flag = index
        elif index < 32:
            f = (b & d) | (c & (~d))
            flag = (5 * index + 1) % 16
        elif index < 48:
            f = (b ^ c ^ d)
            flag = (3 * index + 5) % 16
        else:
            f = c ^ (b | (~d))
            flag = (7 * index) % 16

        a = (b + cycle_left_shift((a + f + FIXED_RANDOM_NUMBER_LIST[index] + groups[flag]) & 0xffffffff,
                                  LEFT_SHIFT_LIST[index])) & 0xffffffff
        a, b, c, d = d, a, b, c
    A = (A + a) & 0xffffffff
    B = (B + b) & 0xffffffff
    C = (C + c) & 0xffffffff
    D = (D + d) & 0xffffffff


def message_digest_algorithm(to_be_encrypted_str: str):
    """
    信息摘要算法第五版，即md5加密算法
    :param to_be_encrypted_str: 待加密的字符串
    :return: 加密后的32位长度的16进制字符串
    """
    encrypted_byte = str(to_be_encrypted_str).encode('utf-8')

    # 原始字节的比特位长度， 64个比特位，长度不足 64 比特位，用数字 0 填充
    encrypted_byte_length_byte = chr(encrypted_byte.__len__() * 8).encode()
    filled_length_byte = encrypted_byte_length_byte + b'\x00' * (8 - encrypted_byte_length_byte.__len__())

    while encrypted_byte.__len__() > GROUP_BYTE_LENGTH:
        cycle_algorithm(encrypted_byte[:GROUP_BYTE_LENGTH])
        encrypted_byte = encrypted_byte[GROUP_BYTE_LENGTH:]
    # 添加数字 1
    encrypted_byte += b'\x80'
    # 添加数字 0
    encrypted_byte += b'\x00' * (REMAINDER_BYTE_LENGTH - encrypted_byte.__len__() % GROUP_BYTE_LENGTH)
    # 添加原始字节的比特位长度， 64个比特位
    encrypted_byte += filled_length_byte
    cycle_algorithm(encrypted_byte[:GROUP_BYTE_LENGTH])

    encrypted_str = ''.join([int2hex(i) for i in [A, B, C, D]])
    return encrypted_str


if __name__ == '__main__':
    data = '1234567123148'
    print(message_digest_algorithm(data))
