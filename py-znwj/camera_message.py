import multiprocessing
import random
import time

from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
from rx.subject import Subject

from dahua.camera import Camera
from dahua.sdk.MVSDK import *
from dahua.util import enumCameras

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


def intense_calculation(rfid):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    time.sleep(random.randint(10, 30) * 0.1)
    return rfid


class CameraMessage(object):
    def __init__(self, app):
        self._app = app
        self._cameras = []
        self._sink = Subject()
        self._sink.pipe(
            ops.observe_on(pool_scheduler),
            ops.map(lambda it: self.grab_by_rfid(it)),
        ).subscribe(
            on_next=lambda it: print('{} handled {}'.format('CameraMessage', it))
        )
        # 发现相机
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return
        for camera in cameraList:
            # 连接相机
            nRet = camera.connect(camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
            if (nRet == 0):
                self._cameras.append(Camera(app, camera))

    def handle_next_rfid(self, rfid):
        self._sink.on_next(rfid)

    def grab_by_rfid(self, rfid):
        for camera in self._cameras:
            camera.grab_by_rfid(rfid)
        return rfid
