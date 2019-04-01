# coding: utf-8
"""
@File    : create_captcha_by_PIL
@Time    : 2019/3/30 22:52
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
import random
import os
import string
import json
from PIL import Image, ImageDraw, ImageFont


class Captcha(object):
    def __init__(self, width, height, color, num, font_path, fontsize, save_path):
        self.width = width  # 生成图片宽度
        self.height = height  # 生成图片高度
        self.bgColor = color  # 生成图片背景颜色
        self.num = num  # 验证码字符个数
        self.font_path = font_path  # 字体路径
        self.fontsize = fontsize  # 字体大小
        self.code = ''  # 验证内容
        self.img = Image.new('RGB', (self.width, self.height), self.bgColor)  # 生成图片对象
        self.save_path = save_path  # 生成图片的保存路径

    # 获取随机颜色，RGB格式
    def get_random_color(self):
        c1 = random.randint(50, 150)
        c2 = random.randint(50, 150)
        c3 = random.randint(50, 150)
        return c1, c2, c3

    # 随机生成1位字符,作为验证码内容
    def get_random_char(self):
        c = ''.join([random.sample('023456789abcdefghjklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 1)[0] for i in
                     range(self.num)])
        return c

    # 生成随机位置(x,y)
    def get_random_xy(self):
        x = random.randint(0, int(self.width))
        y = random.randint(0, int(self.height))
        return x, y

    # 根据字体文件生成字体，无字体文件则生成默认字体
    def get_font(self):
        if self.font_path:
            if os.path.exists(self.font_path):
                if self.fontsize and 0 < self.fontsize < self.height:
                    size = self.fontsize
                else:
                    size = random.randint(int(self.height / 1.5), int(self.height - 10))
                font = ImageFont.truetype(self.font_path, size)
                return font
            raise Exception('字体文件不存在或路径错误', self.font_path)
        return ImageFont.load_default().font

    # 图片旋转
    def rotate(self):
        deg = int(self.height / 3)  # 旋转角度
        self.img = self.img.rotate(random.randint(0, deg), expand=0)

    # 画n条干扰线
    def draw_line(self, n):
        draw = ImageDraw.Draw(self.img)
        for i in range(n):
            x, y = self.get_random_xy()
            x1 = x + random.randint(10, 30)
            y1 = y + random.randint(10, 30)
            draw.line([x, y, x1, y1],
                      self.get_random_color())
        del draw

    # 画n个干扰点
    def draw_point(self, n):
        draw = ImageDraw.Draw(self.img)
        for i in range(n):
            draw.point([self.get_random_xy()], self.get_random_color())
        del draw

    # 写验证码内容
    def draw_text(self, position, char, fillColor):
        draw = ImageDraw.Draw(self.img)
        draw.text(position, char, font=self.get_font(), fill=fillColor)
        del draw

    # 生成验证码图片，并返回图片对象
    def get_captcha(self):
        x_start = 2
        y_start = -5
        self.code = self.get_random_char()
        for i, code in enumerate(self.code):
            x = x_start + i * int(self.width / self.num)
            # y = random.randint(y_start, int(self.height / 30))
            self.draw_text((x, y_start), code, self.get_random_color())

        self.draw_line(5)
        self.draw_point(60)
        return self.img

    # 将图片保存在本地，并以json格式返回验证码内容
    def save_captcha(self):

        img = self.get_captcha()
        path = os.path.join(self.save_path, self.code + '.png')
        if os.path.exists(path):
            os.remove(path)
        try:
            img.save(path)
        except NotADirectoryError:
            raise NotADirectoryError('保存路径错误或不存在:' + self.save_path)


if __name__ == '__main__':
    colors = [(199, 237, 204), (255, 255, 255), (250, 249, 222), (255, 242, 226), (253, 230, 224), (227, 237, 205),
              (220, 226, 241), (233, 235, 254), (234, 234, 239)]
    bgcolor = random.choice(colors)
    width = 72
    height = 24
    bgColor = bgcolor
    num = 4
    # font_path = 'C:/Windows/Fonts/ARLRDBD.TTF'
    font_path = 'C:/Windows/Fonts/ariblk.ttf'
    fontSize = 20
    save_path = 'captcha_images'

    cpt = vertifyCode(width, height, bgColor, num, font_path, fontSize, save_path)
    cpt.save_captcha()
