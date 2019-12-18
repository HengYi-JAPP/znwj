import logging
import time

import yaml

from camera.cameras import Cameras
from constant import DETECT_RESULT_TOPIC
from daemon.plc_message import PlcMessage
from daemon.sick_message import SickMessage
from detect.detector import Detector


class PyZnwj(object):
    def __init__(self, path):
        self._running = False
        self._path = path
        with open(path + '/config.yml', 'r') as f:
            self.__yaml = yaml.safe_load(f)
        logging.basicConfig(level=self.config('logging.level', logging.WARNING), format=self.config('logging.format'))
        # 当前处理中的 rfid
        # 串行处理 rfid
        # socket 等待读取
        self.__rfid = None

        if self.config('sick'):
            self._sick_message = SickMessage(self)

        if self.config('cameras'):
            self._cameras = Cameras(self)

        if self.config('detector'):
            self._detector = Detector(self)

        if self.config('plc'):
            self._plc = PlcMessage(self)

    def handle_next_rfid(self, rfid):
        if not self._running:
            return
        if rfid == self.__rfid:
            return
        time.sleep(3)
        logging.debug('rfid [{}],[{}],[{}]'.format(rfid, type(rfid), len(rfid)))
        self.__rfid = rfid
        if not hasattr(self, '_cameras'):
            return
        self._cameras.handle_next_rfid(rfid)
        if not hasattr(self, '_detector'):
            return
        result = self._detector.detect(rfid)
        if not hasattr(self, '_plc'):
            self._plc.handle_detect_result(result)
        self._mqtt.publish(DETECT_RESULT_TOPIC, result)

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
