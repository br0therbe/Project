# coding: utf-8
"""
@File    : split_captcha
@Time    : 2019/3/30 11:44
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
from gevent import monkey; monkey.patch_all()
import cv2
import gevent
import os
from common.common import cost
from queue import Queue

CAPTCHA_FOR_TEST = "captcha_for_test"
CAPTCHA_FOR_ML = "captcha_for_ML"
SPLIT_CAPTCHA = "split_captcha"


class SplitCaptcha(object):
    def __init__(self):
        self.counts = {}

    @staticmethod
    def count_color(image, color=0):
        """
        统计图片数组中color（0：黑色， 255：白色）的个数
        :param image: 图片数组, 数组类型
        :param color: 颜色， 整数类型
        :return: color颜色的个数, 整数类型
        """
        count = 0
        for i in image:
            for j in i:
                if j == color:
                    count += 1
        return count

    def write_image(self, images, captcha):
        """
        将图片写入硬盘
        :param images: 图片数组，数组类型
        :param captcha: 验证码内容
        """
        for image, letter in zip(images, captcha):
            save_path = os.path.join(SPLIT_CAPTCHA, letter.lower())
            # 如果输出目录不存在，请创建它
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # 将字母图像写入文件
            count = self.counts.get(letter, 1)
            file_name = os.path.join(save_path, "{}.png".format(str(count).zfill(6)))
            cv2.imwrite(file_name, image)
            # 递增当前键的计数
            self.counts[letter] = count + 1

    @staticmethod
    def denoise(image, color=0):
        """
        降噪，去除细干扰线和干扰点。
        去除边界颜色，把图片最外层边界赋值为color（0：黑色， 255：白色）。
        判断点周围（九宫格）color颜色的个数。大于5个，则为孤立点或则细干扰线，赋值为color。
        :param image: 图片数组, 数组类型
        :param color: 噪点颜色， 整数类型
        :return: 降噪后的图片数组， 数组类型
        """
        color = int(color)
        h, w = image.shape[:2]
        # 最外层横向边界赋值为color
        for y in range(0, w):
            image[0, y] = color
            image[h - 1, y] = color
        # 最外层纵向边界赋值为color
        for x in range(0, h):
            image[x, 0] = color
            image[x, w - 1] = color
        # 判断点周围的color颜色的点个数
        for x in range(1, h - 1):
            for y in range(1, w - 1):
                nine_point = [image[i, j] for i in range(x - 1, x + 2) for j in range(y - 1, y + 2)]
                if nine_point.count(color) > 5:
                    image[x, y] = color
        return image

    @classmethod
    def load_img(cls, image_path):
        """
        载入图片并灰度、二值化、去噪
        :param image_path: 图片路径，字符串类型
        :return: 图片数组，数组类型
        """
        # 载入图片
        image = cv2.imread(image_path)
        # 灰度化
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 二值化
        ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        # 降噪
        image = cls.denoise(image, 0)
        return image

    @classmethod
    def split_image(cls, image):
        """
        分割图片
        :param image: 图片数组， 数组类型
        :return: 分割后的图片数组， 列表类型
        """
        # 获取图片高和宽
        height, weight = image.shape[:2]
        # RETR_EXTERNAL：外轮廓。轮廓为白色
        contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        letter_regions = []
        for contour in contours:
            # 获取包含轮廓的矩形
            x, y, w, h = cv2.boundingRect(contour)
            # 比较轮廓的宽度和高度，以检测连接到一个块中的字母
            if w / weight > 0.4:
                # 如果轮廓太宽，把它分成两个字母区域！
                half_width = w / 2
                letter_regions.append((x, y, half_width, h))
                letter_regions.append((x + half_width, y, half_width, h))
            else:
                # 分成一个字母区域！
                letter_regions.append((x, y, w, h))
        # 按x坐标排序
        letter_regions = sorted(letter_regions, key=lambda m: m[0])

        images = []
        cache_dict1 = dict()
        cache_dict2 = dict()
        length = len(letter_regions)
        if length == 4:
            for index, location in enumerate(letter_regions):
                # 抓取图像中字母的坐标
                x, y, w, h = location
                # 添加偏移
                offset = 0
                single_image = image[y - offset: y + h + offset, x - offset: x + w + offset]
                images.append(single_image)
        elif length > 4:
            for index, location in enumerate(letter_regions):
                # 抓取图像中字母的坐标
                x, y, w, h = location
                # 添加偏移
                offset = 0
                single_image = image[y - offset: y + h + offset, x - offset: x + w + offset]
                num = cls.count_color(single_image, 255)
                cache_dict1[index] = num
                cache_dict2[index] = single_image
            compared = sorted(cache_dict1.values())[-5]
            preserved = [item[0] for item in cache_dict1.items() if item[1] > compared]
            for index in preserved:
                images.append(cache_dict2[index])

        return images

    def work(self, queue):
        path = CAPTCHA_FOR_ML
        total = len(os.listdir(path))
        while not queue.empty():
            num, file = queue.get()
            captcha = os.path.splitext(file)[0]
            img_path = os.path.join(path, file)
            img = self.load_img(img_path)
            img = self.split_image(img)
            self.write_image(img, captcha)
            print("正在处理：{} {}/{}".format(img_path, num + 1, total))

    @cost
    def xiecheng(self, num=8):
        path = CAPTCHA_FOR_ML
        queue = Queue()
        for num, file in enumerate(os.listdir(path)):
            queue.put_nowait((num, file))

        gevent.joinall([gevent.spawn(self.work, queue) for _ in range(10)])


if __name__ == "__main__":
    sc = SplitCaptcha()
    sc.xiecheng()
