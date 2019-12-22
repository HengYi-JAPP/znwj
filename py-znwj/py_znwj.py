import logging
import multiprocessing

import yaml
from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
from rx.subject import Subject

from camera_message import CameraMessage
from constant import DETECT_RESULT_TOPIC
from detect.detector import Detector
from plc_message import PlcMessage
from sick_message import SickMessage

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


class PyZnwj(object):
    def __init__(self, path, loop):
        self._path = path
        self._loop = loop
        with open(path + '/config.yml', 'r', encoding='utf8') as f:
            self.__yaml = yaml.safe_load(f)
        logging.basicConfig(level=self.config('logging.level', logging.WARNING), format=self.config('logging.format'))

        self._running = False
        self._sink = Subject()
        self._sink.pipe(
            ops.observe_on(pool_scheduler),
            ops.filter(lambda it: self._running),
            ops.map(lambda it: self.handle_next_rfid(it)),
        ).subscribe(
            on_next=lambda it: print('{} handled {}'.format('CameraMessage', it))
        )

        self._camera_msg = CameraMessage(self)
        self._detector = Detector(self)
        self._plc = PlcMessage(self)
        if self.config('sick'):
            self._sick_msg = SickMessage(self)
            # loop.create_task(self._sick_msg.start())

    def handle_next_rfid(self, rfid):
        for camera in self._camera_msg._cameras:
            camera.grab_by_rfid(rfid)
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
