import asyncio

from camera.Camera import Camera


class Cameras(object):
    def __init__(self, config):
        self.__config = config

    def grab(self, code):
        tasks = []
        for i in range(18):
            camera = Camera(str(i), self.__config)
            task = asyncio.ensure_future(camera.grab(code))
            tasks.append(task)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*tasks))
