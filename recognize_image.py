import cv2
import pickle
import numpy as np
import imutils
import requests
import tensorflow as tf
from keras.models import load_model

MODEL_FILENAME = "captcha_model.hdf5"
MODEL_LABELS_FILENAME = "model_labels.dat"
CAPTCHA = '0123456789-_'
old_v = tf.logging.get_verbosity()
tf.logging.set_verbosity(tf.logging.ERROR)


def load_img(url):
    """
    载入图片，并灰度化
    :param url: 图片链接
    :return: 图片数组
    """
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36'}
    resp_bytes = requests.get(url, headers=headers).content
    img = cv2.imdecode(np.frombuffer(resp_bytes, np.uint8), cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
    return img


def split_image(image):
    """
    分割图片
    :param image: 图片数组
    :return: 列表类型
    """
    images = []
    height, width = image.shape[:2]
    real_w, real_h = width - 4, height - 4
    offset = 25
    num = int(real_w / offset)
    for index in range(num):
        images.append(image[0: real_h, offset * index: offset * (index + 1)])
    if len(images) == num:
        return images
    else:
        raise Exception("SPLIT ERROR")


def resize_captcha(image, width, height):
    """
    调整图片大小
    :param image: 图片数组
    :param width: 将要调整的宽度
    :param height: 将要调整的高度
    :return: 图片数组
    """
    (h, w) = image.shape[:2]
    if w > h:
        image = imutils.resize(image, width=width)
    else:
        image = imutils.resize(image, height=height)
    pad_w = int((width - image.shape[1]) / 2.0)
    pad_h = int((height - image.shape[0]) / 2.0)
    image = cv2.copyMakeBorder(image, pad_h, pad_h, pad_w, pad_w,
                               cv2.BORDER_REPLICATE)
    image = cv2.resize(image, (width, height))
    return image


def recognize(_dict):
    def predict(images, lb, model):
        predictions = []
        for image in images:
            letter_image = resize_captcha(image, 20, 20)
            letter_image = np.expand_dims(letter_image, axis=2)
            letter_image = np.expand_dims(letter_image, axis=0)
            prediction = model.predict(letter_image)
            letter = lb.inverse_transform(prediction)[0]
            predictions.append(letter)
        captcha_text = "".join(predictions)
        return captcha_text

    def recognize_captcha():
        with open(MODEL_LABELS_FILENAME, "rb") as f:
            lb = pickle.load(f)
        model = load_model(MODEL_FILENAME)
        price = list()
        image_position = _dict.values()
        for each in image_position:
            image, position = each
            img = load_img(image)
            img = split_image(img)
            captcha = predict(img, lb, model)
            captcha = captcha.replace('_', ' ').replace('-', '.')
            if len(captcha) != 24:
                raise ValueError('识别错误！')
            price.append(captcha[position])
        return ''.join(price)

    return recognize_captcha()


if __name__ == '__main__':
    di = {'O1438e353ce954e': ['https://images.bthhotels.com/PriceImg/Images/20190407/3e52c8048ef9444db40363adb849dc5b.png', 2], 'T5d472252bb6d45a': ['https://images.bthhotels.com/PriceImg/Images/20190409/6397d4070a6847b7ae0dcd48a055c07d.png', 21], 'H82fef72a1c704': ['https://images.bthhotels.com/PriceImg/Images/20190409/e427a312c56d48c18b83ab264ef41429.png', 6]}
    a = recognize(di)
    print(a)
