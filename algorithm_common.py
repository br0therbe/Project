# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/6/22 18:42
# @Version     : Python 3.7
# @Description : algorithm common function
import ctypes


def unsigned_num(to_be_converted_int):
    """
    将整数转化为 32 位的无符号数
    :param to_be_converted_int: 待转化的整数
    :return: 32 位的无符号数
    """
    return ctypes.c_uint32(to_be_converted_int).value


def byte2int(to_be_converted_byte: bytes) -> int:
    """
    小端存储， 字节转化为整数
    :param to_be_converted_byte: 待转化的字节
    :return: 整数
    """
    bit_str = ''
    for char in to_be_converted_byte[::-1]:
        _bit = bin(char).replace('0b', '')
        bit_length = _bit.__len__()
        filled_bit = "0" * (8 - bit_length) + _bit
        bit_str += filled_bit
    return int(bit_str, 2) & 0xffffffff


def int2hex(to_be_converted_int: int) -> str:
    """
    小端存储，整数转化为字节
    :param to_be_converted_int: 待转化的整数
    :return: 不含前缀 0x 的 16 进制的字符串
    """
    hex_number = hex(to_be_converted_int).replace('0x', '')
    hex_str = ''
    while hex_number.__len__() > 1:
        hex_str += hex_number[-2:]
        hex_number = hex_number[:-2]

    hex_str += "0" * (-hex_number.__len__() % 2) + hex_number
    return hex_str


if __name__ == '__main__':
    print(bin(unsigned_num(-10)))
    print(bin(unsigned_num(10)))
    print(type(unsigned_num(10)))
    print(chr(1245))
