# coding: utf-8
"""
@File    : create_captcha
@Time    : 2019/3/30 22:52
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""

import cv2
import numpy as np
import random
from common.common import cost
from multiprocessing import Process, Queue
from threading import Thread
CAPTCHA = "0123456789abcdefghijklmnopqrstuvwxyz"


def main(width=90, height=36, num=4):
    def create_img(h, w):
        image = np.zeros((h, w, 3), np.uint8)
        image.fill(255)
        return image

    def character():
        return random.choice(CAPTCHA)

    def color():
        return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)

    def black_to_white(image):
        h, w, c = image.shape
        for x in range(h):
            for y in range(w):
                for i in range(c):
                    if image[x, y, i] == 0:
                        image[x, y, i] = 255
        return image

    captcha = ""
    # 新建一个白色背景的图片
    img = create_img(height, width)
    for i in range(num):
        w = int(width / num)
        location = (w, height)
        char = character()
        captcha += char
        little_img = create_img(height, w)
        cv2.putText(little_img, char, (3, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color(), thickness=2)
        center = tuple(i * 0.5 for i in location)
        # 执行下面两行代码会将图形的高度、宽度转换为宽度、高度
        rotate = cv2.getRotationMatrix2D(center, random.randint(-30, 31), 1)
        little_img = cv2.warpAffine(little_img, rotate, location)

        offset = w * i
        # 因此转置little_img的宽和高，与img的高和宽相对应
        img[: height, offset: offset + w] = little_img  # .transpose((1, 0, 2))

    img = black_to_white(img)
    return img, captcha


def work(queue):
    while not queue.empty():
        task = queue.get()
        img, captcha = main()
        cv2.imwrite("captcha_for_ML/{}.png".format(captcha), img)


@cost
def duojincheng(num=4):
    queue = Queue()
    for i in range(500):
        queue.put_nowait(i)

    processes = []
    for _ in range(num):
        process = Process(target=work, args=(queue,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


@cost
def duoxiancheng(num=8):
    queue = Queue()
    for i in range(500):
        queue.put_nowait(i)

    threads = []
    for _ in range(num):
        thread = Thread(target=work, args=(queue,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # 500图片 total time is 10.266s
    duojincheng()
    # 500图片 total time is 14.105s
    duoxiancheng()

