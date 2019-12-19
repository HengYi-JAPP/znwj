import datetime

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
            self._eventSubscribe = openCamera(camera, self._deviceLinkNotify)
            setSoftTriggerConf(camera)
            # 创建流对象
            self._streamSourceInfo, self._streamSource = createStreamSourceInfo(camera)
            # 开始拉流
            startGrabbing(self._streamSource, self._onGetFrameEx)
        except Exception as e:
            logging.error('open camera fail:' + str(e))
            self._error = True

    def grab_by_rfid(self, rfid):
        streamSource = self._streamSource
        # streamSourceInfo, streamSource = createStreamSourceInfo(camera)
        # 主动取图
        frame = pointer(GENICAM_Frame())
        nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(1000))
        if (nRet != 0):
            raise Exception("SoftTrigger getFrame fail! timeOut [1000]ms")
        else:
            print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
            print("get frame time: " + str(datetime.datetime.now()))

        save_image_file_by_frame(
            frame, self._db_path + '/' + rfid + '/original/' + self._serial_number + '.bmp')
        return 0

    # 相机连接状态回调函数
    def _deviceLinkNotify(self, connectArg, linkInfo):
        if (EVType.offLine == connectArg.contents.m_event):
            print("camera has off line, userInfo [%s]" % (c_char_p(linkInfo).value))
        elif (EVType.onLine == connectArg.contents.m_event):
            print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))

    def grabOne(self):
        camera = self._camera
        streamSource = self._streamSource
        # streamSourceInfo, streamSource = createStreamSourceInfo(camera)
        # 创建control节点
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
        if (nRet != 0):
            # 释放相关资源
            streamSource.contents.release(streamSource)
            raise Exception("create AcquisitionControl fail!")

        # 执行一次软触发
        trigSoftwareCmdNode = acqCtrl.contents.triggerSoftware(acqCtrl)
        nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
        if (nRet != 0):
            # 释放相关资源
            trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
            acqCtrl.contents.release(acqCtrl)
            streamSource.contents.release(streamSource)
            raise Exception("Execute triggerSoftware fail!")

            # 释放相关资源
        trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
        acqCtrl.contents.release(acqCtrl)
        logging.info('grabOne')
        return 0

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
