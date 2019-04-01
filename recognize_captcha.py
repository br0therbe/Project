# coding: utf-8
"""
@File    : recognize_captcha
@Time    : 2019/4/1 0:21
@Author  : Big Belly
@Software: PyCharm
@Version : Python 3.7.1
"""
import numpy as np
import os
import pickle
from captcha.resize_captcha import resize_captcha
from captcha.split_captcha import SplitCaptcha
from common.common import cost
from keras.models import load_model

CAPTCHA_FOR_TEST = "captcha_for_test"
CAPTCHA_OF_WEBSITE = 'captcha_of_website'
MODEL_FILENAME = "captcha_model.hdf5"
MODEL_LABELS_FILENAME = "model_labels.dat"


def predict(file, imgs):
    predictions = []
    for img in imgs:
        # 将字母图像重新调整为20x20像素以匹配训练数据
        letter_image = resize_captcha(img, 20, 20)
        # 将单个图像转换为4D图像列表以使Keras满意
        letter_image = np.expand_dims(letter_image, axis=2)
        letter_image = np.expand_dims(letter_image, axis=0)

        # 让神经网络做一个预测
        prediction = model.predict(letter_image)

        # 将一个热编码预测转换回普通字母
        letter = lb.inverse_transform(prediction)[0]
        predictions.append(letter)
    # 打印验证码的文本
    captcha_text = "".join(predictions)
    return captcha_text


@cost
def recognize_captcha():
    global lb, model
    # 加载模型标签（这样我们就可以将模型预测转换为实际字母）
    with open(MODEL_LABELS_FILENAME, "rb") as f:
        lb = pickle.load(f)
    # 加载训练好的神经网络
    model = load_model(MODEL_FILENAME)

    path = CAPTCHA_OF_WEBSITE
    success_rate = 0
    length = len(os.listdir(path))

    for file in os.listdir(path):
        img_name = os.path.join(path, file)
        img = SplitCaptcha.load_img(img_name)
        img = SplitCaptcha.split_image(img)
        captcha = predict(file, img)
        if captcha in file:
            success_rate += 1 / length
            print("{} CAPTCHA text is: {}".format(file, captcha))
        else:
            print("ERROR {} CAPTCHA text is: {}".format(file, captcha))
    success_rate *= 100
    print('success_rate is {:.3f}% '.format(success_rate))


if __name__ == '__main__':
    # 识别问题： l->i、 1->l、
    # ERROR rljx.png CAPTCHA text is: rijx
    # ERROR qqjl.png CAPTCHA text is: qqji
    # ERROR 4liv.png CAPTCHA text is: 4llv
    # ERROR icl1.png CAPTCHA text is: icll
    # ERROR l9qp.png CAPTCHA text is: i9qp
    # success_rate is 95.000%
    # 100 samples, total time is 10.470s

    # 真实网站验证码数据
    # 8pe3.png CAPTCHA text is: 8pe3
    # cr88.png CAPTCHA text is: cr88
    # hcyi.png CAPTCHA text is: hcyi
    # pbvk.png CAPTCHA text is: pbvk
    # rdpr.png CAPTCHA text is: rdpr
    # success_rate is 100.000%
    # 5 samples, total time is 5.661s
    recognize_captcha()
