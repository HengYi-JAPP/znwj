import asyncio

from camera.camera import Camera
from camera.sdk.util import enumCameras


class Cameras(object):
    def __init__(self, config):
        self.__cameras = []
        # 发现相机
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return

        for it in cameraList:
            camera = Camera(config, it)
            self.__cameras.append(camera)

    def subscribe(self, client):
        for it in self.__cameras:
            it.subscribe(client)

    def grab_by_code(self, code):
        tasks = []
        for camera in self.__cameras:
            task = asyncio.ensure_future(camera.grab_by_code(code))
            tasks.append(task)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*tasks))
