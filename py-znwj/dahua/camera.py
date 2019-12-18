from dahua.sdk.MVSDK import *
from dahua.util import save_image_file_by_frame


class Camera(object):
    def __init__(self, app, camera):
        self._db_path = app.config('dbPath', '/home/znwj/db')
        self._camera = camera
        self._key = str(camera.getKey(camera))
        self._vendor_name = str(camera.getVendorName(camera))
        self._model_name = str(camera.getModelName(camera))
        self._serial_number = str(camera.getSerialNumber(camera))

        # 创建流对象
        self._streamSourceInfo = GENICAM_StreamSourceInfo()
        self._streamSourceInfo.pCamera = pointer(self._camera)
        self._streamSourceInfo.channelId = 0
        nRet = GENICAM_createStreamSource(pointer(self._streamSourceInfo), byref(self._streamSource))
        if (nRet != 0):
            raise Exception("create StreamSource fail!")

        # 开始拉流
        nRet = self._streamSource.contents.startGrabbing(self._streamSource, c_ulonglong(0),
                                                         c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        if (nRet != 0):
            # 释放相关资源
            self._streamSource.contents.release(self._streamSource)
            raise Exception("startGrabbing fail!")

    def grab_by_rfid(self, rfid):
        frame = pointer(GENICAM_Frame())
        nRet = self._streamSource.contents.getFrame(self._streamSource, byref(frame), c_uint(1000))
        if (nRet != 0):
            # 释放相关资源
            self._streamSource.contents.release(self._streamSource)
            raise Exception("SoftTrigger getFrame fail! timeOut [1000]ms")

        save_image_file_by_frame(frame, self._db_path + '/' + rfid + '/original/' + self._serial_number + '.bmp')
        return 0
