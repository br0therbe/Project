# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/7/2 10:27
# @Version     : Python 3.6.8
# @Description : AES algorithm in python
import base64
from typing import Union
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad

BLOCK_SIZE = AES.block_size


# remind ECB 不需要 iv, segment_size参数
# remind CBC 不需要 segment_size参数
# remind CFB 需要 iv, segment_size参数
# remind OFB 不需要 segment_size参数

class AESAlgorithm(object):
    # padding
    PADDING_NONE = None
    PADDING_ZERO = 'zero'
    PADDING_PKCS5 = 'pkcs5'
    PADDING_PKCS7 = 'pkcs7'
    PADDING_ANSIX923 = 'ansix923'
    PADDING_ISO10126 = 'iso10126'
    PADDING_ISO7816 = 'iso7816'

    # mode
    MODE_ECB = 1
    MODE_CBC = 2
    MODE_CFB = 3
    MODE_OFB = 5

    def __init__(self, key: Union[str, bytes], mode: int, iv: Union[str, bytes] = None,
                 segment_size: int = 128, style: str = None):
        """
        AES algorithm
        :param key: The secret key to use in the symmetric cipher.
            It must be 16, 24 or 32 bytes long (respectively for *AES-128*, *AES-192* or *AES-256*).
        :param mode: The chaining mode to use for encryption or decryption.
            MODE_ECB(电子密码本模式:Electronic codebook): int = 1, not need param iv, segment_size.
            MODE_CBC(密码分组链接:Cipher-block chaining): int = 2, need param iv.
            MODE_CFB(密文反馈:Cipher feedback): int = 3, need param iv, segment_size.
            MODE_OFB(输出反馈:Output feedback): int = 5, need param iv.
        :param iv: The initialization vector to use for encryption or decryption.
            For ``MODE_CBC``, ``MODE_CFB``, and ``MODE_OFB`` it must be 16 bytes long.
        :param segment_size:  (Only ``MODE_CFB``).The number of bits the plaintext and ciphertext
            are segmented in. It must be a multiple of 8. If not specified, it will be assumed to be 128.
        """
        if mode not in [1, 2, 3, 5]:
            raise ValueError('The chaining mode must be ECB, CBC, CFB or OFB mode.\n'
                             'Please use AES.MODE_ECB or 1, AES.MODE_CBC or 2, AES.MODE_CFB or 3, AES.MODE_OFB or 5!')
        if key.__len__() not in [16, 24, 32]:
            raise ValueError(f'The secret key must be 16, 24 or 32 bytes long.\n'
                             f'Your secret key is {key}.\nLength is {key.__len__()} bytes.')
        if mode in [2, 3, 5] and iv.__len__() != 16:
            raise ValueError(f'The initialization vector must be 16 bytes long in MODE_CBC, MODE_CFB, or MODE_OFB.\n'
                             f'Your initialization vector is {iv}.\nLength is {iv.__len__()} bytes.')
        if isinstance(key, str):
            self.__key = key.encode('utf-8')
        elif isinstance(key, bytes):
            self.__key = key
        else:
            raise ValueError('The secret key must be str type or bytes type.')

        if isinstance(iv, str):
            self.__iv = iv.encode('utf-8')
        elif isinstance(iv, bytes):
            self.__iv = iv
        else:
            raise ValueError('The initialization vector must be str type or bytes type.')
        self.__mode = mode
        self.__segment_size = segment_size
        self.__style = style

    def encode(self, plain_text: Union[str, bytes]) -> str:
        """
        AES encrypt
        :param plain_text: The plaintext must be str type or bytes type.
        :return: ciphertext
        """
        if self.__mode == 1:
            aes = AES.new(key=self.__key, mode=self.__mode)
        elif self.__mode == 3:
            aes = AES.new(key=self.__key, mode=self.__mode, iv=self.__iv, segment_size=128)
        else:
            aes = AES.new(key=self.__key, mode=self.__mode, iv=self.__iv)

        if isinstance(plain_text, str):
            plain_byte = plain_text.encode('utf-8')
        elif isinstance(plain_text, bytes):
            plain_byte = plain_text
        else:
            raise ValueError('The plaintext must be str type or bytes type.')
        padding_length = BLOCK_SIZE - plain_byte.__len__() % BLOCK_SIZE

        if self.__style is None:
            pad_or_not = plain_byte
        elif self.__style == 'zero':
            pad_or_not = plain_byte + padding_length * b'\x00'
        elif self.__style == 'pkcs5':
            pad_or_not = plain_byte + padding_length * chr(padding_length).encode('utf-8')
        elif self.__style == 'pkcs7':
            pad_or_not = pad(plain_byte, BLOCK_SIZE, style='pkcs7')
        elif self.__style == 'ansix923':
            pad_or_not = pad(plain_byte, BLOCK_SIZE, style='x923')
        elif self.__style == 'iso10126':
            pad_or_not = plain_byte + Random.get_random_bytes(padding_length - 1) + chr(padding_length).encode('utf-8')
        elif self.__style == 'iso7816':
            pad_or_not = pad(plain_byte, BLOCK_SIZE, style='iso7816')
        else:
            raise ValueError('Unknown padding style')

        cipher_byte = aes.encrypt(pad_or_not)
        cipher_text = base64.b64encode(cipher_byte).decode('utf-8')
        return cipher_text

    def decode(self, cipher_text: Union[str, bytes]) -> str:
        """
        AES decrypt
        :param cipher_text: The ciphertext must be str type or bytes type.
        :return: plaintext
        """
        if isinstance(cipher_text, str):
            cipher_byte = base64.b64decode(cipher_text)
        elif isinstance(cipher_text, bytes):
            cipher_byte = base64.b64decode(cipher_text)
        else:
            raise ValueError('The ciphertext must be str type or bytes type.')

        if self.__mode == 1:
            aes = AES.new(key=self.__key, mode=self.__mode)
        elif self.__mode == 3:
            aes = AES.new(key=self.__key, mode=self.__mode, iv=self.__iv, segment_size=128)
        else:
            aes = AES.new(key=self.__key, mode=self.__mode, iv=self.__iv)

        pad_or_not = aes.decrypt(cipher_byte)

        if self.__style is None:
            plain_text = pad_or_not
        elif self.__style == 'zero':
            # remind 【zero 填充方式】 如果结果不对， 打开下面的注释
            plain_text = pad_or_not.rstrip(b'\x00')
            # plain_text = pad_or_not
        elif self.__style == 'pkcs5':
            plain_text = pad_or_not[0:-pad_or_not[-1]]
        elif self.__style == 'pkcs7':
            plain_text = unpad(pad_or_not, BLOCK_SIZE, style='pkcs7')
        elif self.__style == 'ansix923':
            plain_text = unpad(pad_or_not, BLOCK_SIZE, style='x923')
        elif self.__style == 'iso10126':
            plain_text = pad_or_not[0:-pad_or_not[-1]]
        elif self.__style == 'iso7816':
            plain_text = unpad(pad_or_not, BLOCK_SIZE, style='iso7816')
        else:
            raise ValueError('Unknown padding style')
        return plain_text.decode('utf-8')
