import multiprocessing

from rx.scheduler import ThreadPoolScheduler

from dahua.camera import Camera
from dahua.sdk.Util import enumCameras

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


class CameraMessage(object):
    def __init__(self, app):
        self._app = app
        self._cameras = []
        # 发现相机
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return
        for index in range(0, cameraCnt):
            camera = Camera(app, cameraList[index])
            if not camera._error:
                self._cameras.append(camera)
