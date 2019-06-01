import ctypes

""""
JavaScript 移位操作模块
使用方式:
   signed_right_shift:
   有符号数右移操作 >>
   >>> import js_shift_operator
   >>> rs = js_shift_operator.signed_right_shift(1880389095, 31)
   >>> rs
   0

... signed_left_shift:
    有符号数左移操作 <<
   >>> ls = js_shift_operator.signed_left_shift(1880389095, 31)
   >>> ls
   -2147483648

... unsigned_right_shift:
    无符号数右移操作 >>>
   >>> urs = js_shift_operator.unsigned_right_shift(1880389095, 31)
   >>> urs
   0
"""


def signed_number(num: int) -> ctypes.c_int32:
    return ctypes.c_int32(num).value


def signed_right_shift(num: int, shift_num: int) -> ctypes.c_int:
    # -1880389095 >> 29 -4
    # -1880389095 >> 30 -2
    # -1880389095 >> 31 -1
    # -1880389095 >> 32 -1880389095
    # -1880389095 >> 33 -940194548
    # -1880389095 >> 34 -470097274

    # 1880389095 >> 29 3
    # 1880389095 >> 30 1
    # 1880389095 >> 31 0
    # 1880389095 >> 32 1880389095
    # 1880389095 >> 33 940194547
    # 1880389095 >> 34 470097273
    shift_num %= 32
    return ctypes.c_int32(num >> shift_num).value


def signed_left_shift(num: int, shift_num: int) -> ctypes.c_int:
    # 1880389095 << 29 -536870912
    # 1880389095 << 30 -1073741824
    # 1880389095 << 31 -2147483648
    # 1880389095 << 32 1880389095
    # 1880389095 << 33 -534189106
    # 1880389095 << 34 -1068378212

    # -1880389095 << 29 536870912
    # -1880389095 << 30 1073741824
    # -1880389095 << 31 -2147483648
    # -1880389095 << 32 -1880389095
    # -1880389095 << 33 534189106
    # -1880389095 << 34 1068378212
    shift_num %= 32
    return ctypes.c_int32(num << shift_num).value


def unsigned_right_shift(num: int, shift_num: int) -> ctypes.c_uint32:
    # 1880389095 >>> 35     235048636
    # 1880389095 >>> 34     470097273
    # 1880389095 >>> 33     940194547
    # 1880389095 >>> 32     1880389095
    # 1880389095 >>> 31     0
    # 1880389095 >>> 30     1

    # -1880389095 >>> 29 4
    # -1880389095 >>> 30 2
    # -1880389095 >>> 31 1
    # -1880389095 >>> 32 2414578201
    # -1880389095 >>> 33 1207289100
    # -1880389095 >>> 34 603644550
    shift_num %= 32
    unsigned_num = ctypes.c_uint32(num).value
    unsigned_num_bin = bin(unsigned_num)[2:]
    unsigned_num_length = len(unsigned_num_bin)
    cut_len = unsigned_num_length - shift_num
    if cut_len > 0:
        return int(unsigned_num_bin[:cut_len], 2)
    elif cut_len == 0:
        return 0
    else:
        new_unsigned_num_bin = unsigned_num_bin[-cut_len:]
        if new_unsigned_num_bin:
            return int(new_unsigned_num_bin, 2)
        else:
            return 0


if __name__ == '__main__':
    a = 1880389095
    b = -a
    for i in range(23, 26):
        print(i, unsigned_right_shift(-32, i))
