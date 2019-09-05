# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019-09-05 10:50
# @Version     : Python 3.6.8
# @Description : 
ENCODE_STRING = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
ENCODE_MAP = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
              12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W',
              23: 'X', 24: 'Y', 25: 'Z', 26: 'a', 27: 'b', 28: 'c', 29: 'd', 30: 'e', 31: 'f', 32: 'g', 33: 'h',
              34: 'i', 35: 'j', 36: 'k', 37: 'l', 38: 'm', 39: 'n', 40: 'o', 41: 'p', 42: 'q', 43: 'r', 44: 's',
              45: 't', 46: 'u', 47: 'v', 48: 'w', 49: 'x', 50: 'y', 51: 'z', 52: '0', 53: '1', 54: '2', 55: '3',
              56: '4', 57: '5', 58: '6', 59: '7', 60: '8', 61: '9', 62: '+', 63: '/'}
DECODE_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11,
              'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22,
              'X': 23, 'Y': 24, 'Z': 25, 'a': 26, 'b': 27, 'c': 28, 'd': 29, 'e': 30, 'f': 31, 'g': 32, 'h': 33,
              'i': 34, 'j': 35, 'k': 36, 'l': 37, 'm': 38, 'n': 39, 'o': 40, 'p': 41, 'q': 42, 'r': 43, 's': 44,
              't': 45, 'u': 46, 'v': 47, 'w': 48, 'x': 49, 'y': 50, 'z': 51, '0': 52, '1': 53, '2': 54, '3': 55,
              '4': 56, '5': 57, '6': 58, '7': 59, '8': 60, '9': 61, '+': 62, '/': 63}


def encode(paint_text: (str, bytes), encoding='utf-8') -> str:
    if isinstance(paint_text, str):
        paint_byte = bytes(paint_text, encoding=encoding)
    elif isinstance(paint_text, bytes):
        paint_byte = paint_text
    else:
        raise TypeError("paint_text should be string type or byte type")
    length = paint_byte.__len__()
    times = length % 3
    sub_length = length - times
    count = 0
    paint_bin = ''
    while count < sub_length:
        paint_bin += ''.join([f"{each_byte:08b}" for each_byte in paint_byte[count: count + 3]])
        count += 3
    if times == 1:
        paint_bin += f"{paint_byte[-1]:08b}0000"
        pad_str = '=='
    elif times == 2:
        paint_bin += f"{paint_byte[-2]:08b}{paint_byte[-1]:08b}00"
        pad_str = '='
    else:
        pad_str = ''
    bin_length = paint_bin.__len__()
    count = 0
    cipher_text = ''
    while count < bin_length:
        cipher_text += ENCODE_MAP[int(paint_bin[count: count + 6], 2)]
        count += 6
    cipher_text += pad_str
    return cipher_text


def decode(cipher_text: str, encoding=None):
    if cipher_text[-2] == '=':
        pad_len = 4
        pad_num = 2
    elif cipher_text[-1] == '=':
        pad_len = 2
        pad_num = 1
    else:
        pad_len = 0
        pad_num = 0
    count = 0
    paint_bin = ''
    sub_length = cipher_text.__len__() - pad_num - 1
    while count < sub_length:
        paint_bin += f"{DECODE_MAP[cipher_text[count]]:06b}"
        count += 1
    paint_bin = paint_bin + f"{DECODE_MAP[cipher_text[sub_length]]:06b}"[:6 - pad_len]

    count = 0
    paint_byte = []
    length = paint_bin.__len__()
    while count < length:
        paint_byte.append(int(paint_bin[count: count + 8], 2))
        count += 8
    paint_byte = bytes([each_byte for each_byte in paint_byte])
    return paint_byte if encoding is None else paint_byte.decode(encoding=encoding)
