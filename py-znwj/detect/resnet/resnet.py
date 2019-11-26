# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:17:25 2019

@author: 54198
"""

import json, os, re, sys, time
import cv2
import numpy as np
from PIL import ImageDraw, Image

from keras import backend as K
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
from keras.preprocessing import image


# 画出拌丝位置

class resnet(object):

    def __init__(self, config, **kwargs):
        # self.__db_path = config.dbPath
        self.cx_bs_model_path = config['resnet']['model_path']
        self.bs_threshold = config['resnet']['bs_threshold']
        self.window_count = config['resnet']['window_count']
        self.original_path = config['db_path']['original_path']
        self.load_model()

    def drawbox_bs(self, img, box_nums, rects):
        img = cv2.imread(img)
        for i, num in enumerate(box_nums):
            box = rects[num[0]]
            cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
        return img

    # 输入：
    # img :输入图像
    # window_count: 滑窗数量 0 - 360。例如 window_count = 15， 24度一个滑窗，一个圆滑动15次生成15张图，值需要能被360整除
    # 输出：batch_holder 分割结果, rects每个结果的位置
    def bs_slide_windows(self, img, window_count):
        img_ori = cv2.imread(img)
        gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.1, 1000, param1=150, param2=30, minRadius=0,
                                   maxRadius=650)
        circles = np.round(circles[0, :]).astype("int")

        angle = 0

        step = int(360 / window_count)

        ring_size = 100

        batch_holder = np.zeros((window_count, 224, 224, 3))

        rects = []
        while angle < 360:

            center = [circles[0][0], circles[0][1]]
            radius_lg = int(circles[0][2] + ring_size)
            radius_sm = circles[0][2] - 10

            perimeter_x = np.int(center[0] + radius_lg * np.cos(angle * np.pi / 180.0))
            perimeter_y = np.int(center[1] + radius_lg * np.sin(angle * np.pi / 180.0))
            perimeter_x_sm = np.int(center[0] + radius_sm * np.cos(angle * np.pi / 180.0))
            perimeter_y_sm = np.int(center[1] + radius_sm * np.sin(angle * np.pi / 180.0))

            angle = angle + step

            perimeter_x_1 = np.int(center[0] + radius_lg * np.cos(angle * np.pi / 180.0))
            perimeter_y_1 = np.int(center[1] + radius_lg * np.sin(angle * np.pi / 180.0))
            perimeter_x_sm_1 = np.int(center[0] + radius_sm * np.cos(angle * np.pi / 180.0))
            perimeter_y_sm_1 = np.int(center[1] + radius_sm * np.sin(angle * np.pi / 180.0))

            coordinates = np.array(
                [[perimeter_x, perimeter_y], [perimeter_x_sm, perimeter_y_sm], [perimeter_x_1, perimeter_y_1],
                 [perimeter_x_sm_1, perimeter_y_sm_1]])

            rect = cv2.minAreaRect(coordinates)

            box = cv2.boxPoints(rect)
            box = np.int0(box)

            W = rect[1][0]
            H = rect[1][1]

            Xs = [i[0] for i in box]
            Ys = [i[1] for i in box]
            x1 = min(Xs)
            x2 = max(Xs)
            y1 = min(Ys)
            y2 = max(Ys)

            rotated = False
            rotated_angle = rect[2]
            if rotated_angle < -45:
                rotated_angle += 90
                rotated = True

            mult = 1
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            size = (int(mult * (x2 - x1)), int(mult * (y2 - y1)))

            M = cv2.getRotationMatrix2D((size[0] / 2, size[1] / 2), rotated_angle, 1.0)

            cropped = cv2.getRectSubPix(img_ori, size, center)
            cropped = cv2.warpAffine(cropped, M, size)

            croppedW = W if not rotated else H
            croppedH = H if not rotated else W
            croppedRotated = cv2.getRectSubPix(cropped, (int(croppedW * mult), int(croppedH * mult)),
                                               (size[0] / 2, size[1] / 2))

            n = angle / step

            croppedRotated = cv2.resize(croppedRotated, (224, 224))

            mean_top = np.mean(croppedRotated[0:10, :])
            mean_bot = np.mean(croppedRotated[-10:-1, :])
            mean_left = np.mean(croppedRotated[:, 0:10])
            mean_right = np.mean(croppedRotated[:, -10:-1])
            means = [mean_bot, mean_left, mean_top, mean_right]
            for i, mean in enumerate(means):
                if mean < 50:
                    croppedRotated = np.rot90(croppedRotated, i)
            batch_holder[int(n - 1), :] = croppedRotated
            rects.append(box)

        return batch_holder, rects

    def predict_cx_bs(self, img_path, model, camera_num):
        if camera_num == 12:
            x, box_location = self.bs_slide_windows(img_path, self.window_count)

        else:
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        return preds, x, box_location

    def load_model(self):
        self.model_cx_bs = load_model(self.cx_bs_model_path)

    def detect(self, code):
        path = self.original_path + code + '/original/'
        outdir = self.original_path + code + '/defect/'
        out_file_name = []
        out_label = []

        for jpgfile in os.listdir(path):

            if True:

                pred, img_cx_bs, box_locations = self.predict_cx_bs(path + jpgfile, self.model_cx_bs, 12)

                temp = pred[:, 2]
                res_index = np.argwhere(temp > 0.3)
                result_img = self.drawbox_bs(path + jpgfile, res_index, box_locations)
                result_img = Image.fromarray(result_img)
                out_label.append('绊丝')
                out_file_name.append('defect_' + jpgfile[:-4] + '_BS.jpg')
                result_img.save(os.path.join(outdir, os.path.basename('defect_' + jpgfile[:-4] + '_BS.jpg')))

            # 判断成型
            else:
                pred, img_cx_bs = self.predict_cx_bs(path + jpgfile, self.model_cx_bs)
                temp = pred[0, :]
                index = np.argmax(temp)
                if index == 0:
                    draw = ImageDraw.Draw(img_cx_bs)
                    draw.text((20, 20), 'CX', fill=(0, 255, 0))
                    out_label.append('成型')
                    out_file_name.append('defect_' + jpgfile[:-4] + '_CX.jpg')
                    img_cx_bs.save(os.path.join(outdir, os.path.basename('defect_' + jpgfile[:-4] + '_CX.jpg')))
                else:
                    out_label.append(' ')
                    out_file_name.append(path + '/' + jpgfile)