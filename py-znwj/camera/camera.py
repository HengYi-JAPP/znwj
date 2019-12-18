import logging

from camera.sdk.MVSDK import *
from camera.sdk.util import save_image_file_by_frame


class Camera(object):
    def __init__(self, config, camera):
        self.__db_path = config.get('dbPath', '/home/znwj/db')
        self.__camera = camera
        self.__key = str(camera.getKey(camera))
        self.__vendor_name = str(camera.getVendorName(camera))
        self.__model_name = str(camera.getModelName(camera))
        self.__serial_number = str(camera.getSerialNumber(camera))

    def is_connect(self):
        nRet = self.__camera.isConnect(self.__camera)
        # 0代表连接
        if nRet == 0:
            return True
        else:
            return False

    def subscribe(self, client):
        self.__client = client

        # 连接相机
        nRet = self.__camera.connect(self.__camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
        if (nRet != 0):
            logging.error("camera connect fail!")
            return -1

        # 创建流对象
        self.__streamSourceInfo = GENICAM_StreamSourceInfo()
        self.__streamSourceInfo.pCamera = pointer(self.__camera)
        self.__streamSourceInfo.channelId = 0
        nRet = GENICAM_createStreamSource(pointer(self.__streamSourceInfo), byref(self.__streamSourceInfo))
        if (nRet != 0):
            logging.error("startGrabbing fail!")
            raise Exception("create StreamSource fail!")

        # 开始拉流
        nRet = self.__streamSourceInfo.contents.startGrabbing(self.__streamSourceInfo, c_ulonglong(0),
                                                              c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        if (nRet != 0):
            # 释放相关资源
            self.__streamSourceInfo.contents.release(self.__streamSourceInfo)
            logging.error("startGrabbing fail!")
            raise Exception("startGrabbing fail!")

        # # 注册上下线通知
        # eventSubscribe = pointer(GENICAM_EventSubscribe())
        # eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        # eventSubscribeInfo.pCamera = pointer(self.__camera)
        # nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
        # if (nRet != 0):
        #     raise Exception("create eventSubscribe fail!")
        # connectCallBackFuncEx = connectCallBackEx(self.deviceLinkNotify)
        # frameCallbackFunc = callbackFunc(self.onGetFrame)
        # nRet = eventSubscribe.contents.subscribeConnectArgsEx(eventSubscribe, connectCallBackFuncEx, b"statusInfo")
        # if (nRet != 0):
        #     # 释放相关资源
        #     eventSubscribe.contents.release(eventSubscribe)
        #     raise Exception("subscribeConnectArgsEx fail!")
        #
        # # 不再使用时，需释放相关资源
        # eventSubscribe.contents.release(eventSubscribe)
        return 0

    # 相机连接状态回调函数
    def deviceLinkNotify(self, connectArg, linkInfo):
        if (EVType.offLine == connectArg.contents.m_event):
            print("camera has off line, userInfo [%s]" % (c_char_p(linkInfo).value))
        elif (EVType.onLine == connectArg.contents.m_event):
            print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))

    # 取流回调函数
    def onGetFrame(self, frame):
        path = self.__db_path + '/test/' + self.__serial_number + '.bmp'
        save_image_file_by_frame(frame, path)

    async def grab_by_code(self, code):
        # # 创建流对象
        # streamSourceInfo = GENICAM_StreamSourceInfo()
        # streamSourceInfo.channelId = 0
        # streamSourceInfo.pCamera = pointer(self.__camera)
        #
        # streamSource = pointer(GENICAM_StreamSource())
        # nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
        # if (nRet != 0):
        #     raise Exception("create StreamSource fail!")
        #
        # # 通用属性设置:设置触发模式为off --根据属性类型，直接构造属性节点。如触发模式是 enumNode，构造enumNode节点
        # # 自由拉流：TriggerMode 需为 off
        # trigModeEnumNode = pointer(GENICAM_EnumNode())
        # trigModeEnumNodeInfo = GENICAM_EnumNodeInfo()
        # trigModeEnumNodeInfo.pCamera = pointer(self.__camera)
        # trigModeEnumNodeInfo.attrName = b"TriggerMode"
        # nRet = GENICAM_createEnumNode(byref(trigModeEnumNodeInfo), byref(trigModeEnumNode))
        # if (nRet != 0):
        #     # 释放相关资源
        #     streamSource.contents.release(streamSource)
        #     raise Exception("create TriggerMode Node fail!")
        #
        # nRet = trigModeEnumNode.contents.setValueBySymbol(trigModeEnumNode, b"Off")
        # if (nRet != 0):
        #     # 释放相关资源
        #     trigModeEnumNode.contents.release(trigModeEnumNode)
        #     streamSource.contents.release(streamSource)
        #     raise Exception("set TriggerMode value [Off] fail!")
        #
        # # 需要释放Node资源
        # trigModeEnumNode.contents.release(trigModeEnumNode)
        #
        # # 开始拉流
        # nRet = streamSource.contents.startGrabbing(streamSource, c_ulonglong(0), \
        #                                            c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        # if (nRet != 0):
        #     # 释放相关资源
        #     streamSource.contents.release(streamSource)
        #     logging.error("startGrabbing fail!")
        #     raise Exception("startGrabbing fail!")

        if not self.is_connect():
            return -1

        frame = pointer(GENICAM_Frame())
        nRet = self.__streamSource.contents.getFrame(self.__streamSource, byref(frame), c_uint(1000))
        if (nRet != 0):
            # 释放相关资源
            self.__streamSource.contents.release(self.__streamSource)
            logging.error("SoftTrigger getFrame fail! timeOut [1000]ms")
            raise Exception("SoftTrigger getFrame fail! timeOut [1000]ms")

        save_image_file_by_frame(frame, self.__db_path + '/' + code + '/original/' + self.__serial_number + '.bmp')
        return 0
