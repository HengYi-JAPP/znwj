# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 16:55:55 2019

@author: 54198
"""

import colorsys
import os
from timeit import default_timer as timer

import numpy as np
from PIL import Image, ImageFont, ImageDraw
from keras import backend as K
from keras.layers import Input
from keras.models import load_model
from keras.utils import multi_gpu_model

from yolo3.model import yolo_eval, yolo_body, tiny_yolo_body
from yolo3.utils import letterbox_image


class Yolo(object):
    def __init__(self, config, **kwargs):
        # self.__db_path = config.dbPath
        self.classes_path = config['yolo']['classes_path']
        self.anchors_path = config['yolo']['anchors_path']
        self.model_path = config['yolo']['model_path']
        self.iou = config['yolo']['iou']
        self.score = config['yolo']['score']
        self.gpu_num = config['yolo']['gpu_num']
        self.original_path = config['db_path']['original_path']
        self.defect_path = config['db_path']['defect_path']
        self.label_names = config['yolo']['label_names']

        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # Load model, or construct model and load weights.
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        is_tiny_version = num_anchors == 6  # default setting
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model = tiny_yolo_body(Input(shape=(None, None, 3)), num_anchors // 2, num_classes) \
                if is_tiny_version else yolo_body(Input(shape=(None, None, 3)), num_anchors // 3, num_classes)
            self.yolo_model.load_weights(self.model_path)  # make sure model, anchors and classes match
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                   num_anchors / len(self.yolo_model.output) * (num_classes + 5), \
                'Mismatch between model and given anchor and class sizes'

        print('{} model, anchors, and classes loaded.'.format(model_path))

        # Generate colors for drawing bounding boxes.
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        np.random.seed(10101)  # Fixed seed for consistent colors across runs.
        np.random.shuffle(self.colors)  # Shuffle colors to decorrelate adjacent classes.
        np.random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2,))
        if self.gpu_num >= 2:
            self.yolo_model = multi_gpu_model(self.yolo_model, gpus=self.gpu_num)
        boxes, scores, classes = yolo_eval(self.yolo_model.output, self.anchors,
                                           len(self.class_names), self.input_image_shape,
                                           score_threshold=self.score, iou_threshold=self.iou)
        return boxes, scores, classes

        # 所以初始化的事情这里做

    def detect_image(self, image, model_image_size):
        start = timer()

        if model_image_size != (None, None):
            assert model_image_size[0] % 32 == 0, 'Multiples of 32 required'
            assert model_image_size[1] % 32 == 0, 'Multiples of 32 required'
            boxed_image = letterbox_image(image, tuple(reversed(model_image_size)))
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')

        # print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })

        print('out_scores:%s' % out_scores, 'out_classes:%s' % out_classes)
        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        # 调整字体大小以及框框厚度
        font = ImageFont.truetype(font='D:/python/znwj/font/FiraMono-Medium.otf',
                                  size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 1000

        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            print(label, (left, top), (right, bottom))

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        end = timer()

        print('use time:%s' % (end - start))
        return image, out_boxes, out_classes

    def close_session(self):
        self.sess.close()

    def enumerate_class(self, name, out_classes):
        detect_name = ''
        for i, c in reversed(list(enumerate(out_classes))):
            detect_name = str(detect_name) + '_' + str(name[c])
        return detect_name

    def detect(self, code):
        path = self.original_path + code + '/original/'
        outdir = self.original_path + code + '/defect/'
        out_file_name = []
        out_label = []

        for jpgfile in os.listdir(path):

            # 判断毛丝、油污、成型
            if True:

                img1 = Image.open(path + jpgfile)
                # print(path+'/'+jpgfile)
                img1 = img1.convert('RGB')
                model_image_size = (416, 416)
                img, out_boxes, out_classes = self.detect_image(img1, model_image_size)

                if len(out_boxes) > 0:
                    label = self.enumerate_class(self.label_names, out_classes)
                    name = self.enumerate_class(self.class_names, out_classes)
                    out_label.append(label[1:])
                    img.save(os.path.join(outdir, os.path.basename('defect_' + jpgfile[:-4] + name + '.jpg')))
                    out_file_name.append('defect_' + jpgfile[:-4] + name + '.jpg')
                else:
                    model_image_size = (608, 608)
                    img, out_boxes, out_classes = self.detect_image(img1, model_image_size)

                    if len(out_boxes) > 0:
                        label = self.enumerate_class(self.label_names, out_classes)
                        name = self.enumerate_class(self.class_names, out_classes)
                        out_label.append(label[1:])
                        out_file_name.append('defect_' + jpgfile[:-4] + name + '.jpg')
                        img.save(os.path.join(outdir, os.path.basename('defect_' + jpgfile[:-4] + name + '.jpg')))


        dic_ms = {}
        dic_js = {}
        dic_yw = {}
        dict_all = []
        dic_ms['exception'] = '毛丝'
        dic_js['exception'] = '夹丝'
        dic_yw['exception'] = '油污'
        dic_ms['exceptionImageFileNames'] = dic_js['exceptionImageFileNames'] = dic_yw['exceptionImageFileNames'] = []
        for i in out_file_name:
            if 'MS' in i:
                dic_ms['exceptionImageFileNames'].append(out_file_name)
                dict_all.append(dic_ms)
            elif 'JS' in i:
                dic_js['exceptionImageFileNames'].append(out_file_name)
                dict_all.append(dic_js)
            elif 'YW' in i:
                dic_yw['exceptionImageFileNames'].append(out_file_name)
                dict_all.append(dic_yw)

        return dict_all

# import yaml
# config = yaml.load(open('D:\python\znwj\config.yml'))
# yolo=Yolo(config)


