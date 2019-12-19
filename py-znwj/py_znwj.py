import logging

import yaml

from camera_message import CameraMessage
from constant import DETECT_RESULT_TOPIC
from detect.detector import Detector
from plc_message import PlcMessage
from sick_message import SickMessage


class PyZnwj(object):
    def __init__(self, path, loop):
        self._path = path
        self._loop = loop
        with open(path + '/config.yml', 'r', encoding='utf8') as f:
            self.__yaml = yaml.safe_load(f)
        logging.basicConfig(level=self.config('logging.level', logging.WARNING), format=self.config('logging.format'))
        # 当前处理中的 rfid
        # 串行处理 rfid
        # socket 等待读取
        self._running = False

        self._camera_msg = CameraMessage(self)

        if self.config('detector'):
            self._detector = Detector(self)

        if self.config('plc'):
            self._plc = PlcMessage(self)

        if self.config('sick'):
            self._sick_msg = SickMessage(self)
            loop.create_task(self._sick_msg.start())

    def handle_next_detect(self, rfid):
        if not hasattr(self, '_detector'):
            return
        result = self._detector.detect(rfid)
        if not hasattr(self, '_plc'):
            self._plc.handle_detect_result(result)
        self._mqttc.publish(DETECT_RESULT_TOPIC, result)

    def config(self, attrs, default=None):
        ret = None
        for attr in attrs.split('.'):
            if not ret:
                ret = self.__yaml.get(attr)
            else:
                ret = ret.get(attr)
            if not ret:
                return default
        return ret
