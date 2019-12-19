import multiprocessing
import random
import time

from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
from rx.subject import Subject

from dahua.camera_ctrl import CameraCtrl

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


def intense_calculation(rfid):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    time.sleep(random.randint(10, 30) * 0.1)
    return rfid


class CameraMessage(object):
    def __init__(self, app):
        self._app = app
        self._cameras = CameraCtrl(app).get_cameras()
        self._sink = Subject()
        self._sink.pipe(
            ops.observe_on(pool_scheduler),
            ops.map(lambda it: self.grab_by_rfid(it)),
        ).subscribe(
            on_next=lambda it: print('{} handled {}'.format('CameraMessage', it))
        )

    def handle_next_rfid(self, rfid):
        self._sink.on_next(rfid)

    def grab_by_rfid(self, rfid):
        for camera in self._cameras:
            camera.grab_by_rfid(rfid)
        return rfid
