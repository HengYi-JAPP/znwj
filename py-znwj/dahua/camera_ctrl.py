from dahua.camera import Camera
from dahua.sdk.Util import enumCameras


class CameraCtrl(object):
    def __init__(self, app):
        self._cameras = []
        # 发现相机
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return
        for index in range(0, cameraCnt):
            camera = cameraList[index]
            self._cameras.append(Camera(app, camera))

    def get_cameras(self):
        ret = []
        for camera in self._cameras:
            if not camera._error:
                ret.append(camera)
        return ret
