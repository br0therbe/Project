from helpers import resize_to_fit
from imutils import paths
import numpy as np
import imutils
import cv2
import pickle
import os
import time
from keras.models import load_model
TEST_IMAGE_FOLDER = "test_captcha_images"
MODEL_FILENAME = "captcha_model.hdf5"
MODEL_LABELS_FILENAME = "model_labels.dat"
CAPTCHA_IMAGE_FOLDER = "captcha_images"
# CAPTCHA_IMAGE_FOLDER = "y"
# 加载模型标签（这样我们就可以将模型预测转换为实际字母）
with open(MODEL_LABELS_FILENAME, "rb") as f:
    lb = pickle.load(f)
# 加载训练好的神经网络
model = load_model(MODEL_FILENAME)
counts = {}
def count_element(element, img):
    count = 0
    for i in img:
        for j in i:
            if j == element:
                count += 1
    return count


def denoise(img, color=0):
    '''干扰线和干扰点降噪'''
    points = []
    color = int(color)
    h, w = img.shape[:2]
    # ！！！opencv矩阵点是反的
    # img[1,2] 1:图片的高度，2：图片的宽度
    for y in range(0, w):
        img[0, y] = color
        img[h-1, y] = color
    for x in range(0, h):
        img[x, 0] = color
        img[x, w-1] = color
    for y in range(1, w - 1):
        for x in range(1, h - 1):
            nine_point = [img[i, j] for i in range(x - 1, x + 2) for j in range(y - 1, y + 2)]
            if nine_point.count(color) > 5:
                img[x, y] = color
    return img

def load_img(img_name):
    img = cv2.imread(img_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    img = denoise(img)
    return img

def split_img(img):
    contours, hierarchy = cv2.findContours(img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    letter_image_regions = []
    for contour in contours:
        # 获取包含轮廓的矩形
        x, y, w, h = cv2.boundingRect(contour)
        # 比较轮廓的宽度和高度，以检测连接到一个块中的字母
        if w / h > 1.5:
            # 如果轮廓太宽，把它分成两个字母区域！
            half_width = int(w / 2)
            letter_image_regions.append((x, y, half_width, h))
            letter_image_regions.append((x + half_width, y, half_width, h))
        else:
            # 分成一个字母区域！
            letter_image_regions.append((x, y, w, h))
    letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

    imgs = []
    for letter_bounding_box in letter_image_regions:
        # 抓取图像中字母的坐标
        x, y, w, h = letter_bounding_box
        # 从原始图像中提取字母，边缘周围有2像素边距
        a = img[y:y + h, x:x + w]
        if h - 6 < 0:
            continue
        b = count_element(255, img[y:y + h - 6, x:x + w])
        if b < 30:
            continue
        # cv2.imshow('gray', a)
        # cv2.waitKey(0)
        imgs.append(a)
    # print(len(imgs))
    return imgs if len(imgs) == 4 else []

def predict(file, imgs):
    predictions = []
    for img in imgs:
        # 将字母图像重新调整为20x20像素以匹配训练数据
        letter_image = resize_to_fit(img, 20, 20)

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
    print("{} CAPTCHA text is: {}".format(file, captcha_text))





def main():
    path = CAPTCHA_IMAGE_FOLDER
    for file in os.listdir(path):
        # 文件名， 如“2A2X”
        correct_text = os.path.splitext(file)[0]
        img_name = os.path.join(path, file)
        img = load_img(img_name)
        img = split_img(img)
        predict(file, img)

t = time.time()
main()
print('total time is {0:.3f}s'.format(time.time()-t))


