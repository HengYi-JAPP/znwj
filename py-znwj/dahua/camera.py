from dahua.sdk.Util import *


class Camera(object):
    def __init__(self, app, camera):
        self._db_path = app.config('dbPath', app._path + '/db')
        self._camera = camera
        self._key = str(camera.getKey(camera))
        self._vendor_name = str(camera.getVendorName(camera))
        self._model_name = str(camera.getModelName(camera))
        self._serial_number = str(camera.getSerialNumber(camera))

        self._error = False
        try:
            # 打开相机
            openCamera(camera)
            subscribeCameraStatus(camera, self._onDeviceLinkNotify)
            # 创建流对象
            self._streamSourceInfo, self._streamSource = createStreamSourceInfo(camera)
            # 设置软触发
            setSoftTriggerConf(camera)
            # 开始拉流
            startGrabbing(self._streamSource)
        except Exception as e:
            logging.error('open camera fail:' + str(e))
            self._error = True

    def grab_by_rfid(self, rfid):
        # 软触发取一张图
        nRet = grabOne(self._camera)
        if (nRet != 0):
            logging.error("grabOne fail!")
            return -1
        streamSource = self._streamSource
        # 主动取图
        frame = pointer(GENICAM_Frame())
        nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(1000))
        if (nRet != 0):
            logging.error("SoftTrigger getFrame fail! timeOut [1000]ms")
        else:
            filePath = self._db_path + '/' + rfid + '/original/' + self._serial_number + '.bmp'
            save_image_file_by_frame(frame, filePath)
        return 0

    # 相机连接状态回调函数
    def _onDeviceLinkNotify(self, connectArg, linkInfo):
        if (EVType.offLine == connectArg.contents.m_event):
            print("camera has off line, userInfo [%s]" % (c_char_p(linkInfo).value))
            # // 此处一般要销毁流对象、事件订阅对象， // 反注册流事件回调、相机事件回调、拉流回调，并停止拉
        elif (EVType.onLine == connectArg.contents.m_event):
            print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))
            # // 此处一般要断开相机连接，重新连接相机， // 重新创建流对象、事件订阅对象, // 重新注册流事件回调、相机事件回调、拉流回调， // 重新开始拉

    # 取流回调函数Ex
    def _onGetFrameEx(self, frame, userInfo):
        nRet = frame.contents.valid(frame)
        if (nRet != 0):
            print("frame is invalid!")
            # 释放驱动图像缓存资源
            frame.contents.release(frame)
            return

        print("BlockId = %d userInfo = %s" % (frame.contents.getBlockId(frame), c_char_p(userInfo).value))
        # 此处客户应用程序应将图像拷贝出使用
        '''
        '''
        logging.info('_onGetFrameEx')
        # 释放驱动图像缓存资源
        frame.contents.release(frame)
