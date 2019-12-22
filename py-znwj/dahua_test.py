#!/usr/bin/env python
# coding: utf-8
'''
Created on 2017-10-25

@author:
'''
import datetime
import time

from dahua.sdk.Util import *

g_cameraStatusUserInfo = b"statusInfo"


# 取流回调函数Ex
def onGetFrameEx(frame, userInfo):
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
    # 释放驱动图像缓存资源
    frame.contents.release(frame)


# 相机连接状态回调函数
def deviceLinkNotify(connectArg, linkInfo):
    if (EVType.offLine == connectArg.contents.m_event):
        print("camera has off line, userInfo [%s]" % (c_char_p(linkInfo).value))
    elif (EVType.onLine == connectArg.contents.m_event):
        print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))


# 设置外触发
def setLineTriggerConf(camera):
    # 创建control节点
    acqCtrlInfo = GENICAM_AcquisitionControlInfo()
    acqCtrlInfo.pCamera = pointer(camera)
    acqCtrl = pointer(GENICAM_AcquisitionControl())
    nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
    if (nRet != 0):
        print("create AcquisitionControl fail!")
        return -1

    # 设置触发源为软触发
    trigSourceEnumNode = acqCtrl.contents.triggerSource(acqCtrl)
    nRet = trigSourceEnumNode.setValueBySymbol(byref(trigSourceEnumNode), b"Line1")
    if (nRet != 0):
        print("set TriggerSource value [Line1] fail!")
        # 释放相关资源
        trigSourceEnumNode.release(byref(trigSourceEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return -1

    # 需要释放Node资源
    trigSourceEnumNode.release(byref(trigSourceEnumNode))

    # 设置触发方式
    trigSelectorEnumNode = acqCtrl.contents.triggerSelector(acqCtrl)
    nRet = trigSelectorEnumNode.setValueBySymbol(byref(trigSelectorEnumNode), b"FrameStart")
    if (nRet != 0):
        print("set TriggerSelector value [FrameStart] fail!")
        # 释放相关资源
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return -1

    # 需要释放Node资源
    trigSelectorEnumNode.release(byref(trigSelectorEnumNode))

    # 打开触发模式
    trigModeEnumNode = acqCtrl.contents.triggerMode(acqCtrl)
    nRet = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"On")
    if (nRet != 0):
        print("set TriggerMode value [On] fail!")
        # 释放相关资源
        trigModeEnumNode.release(byref(trigModeEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return -1

    # 需要释放Node资源
    trigModeEnumNode.release(byref(trigModeEnumNode))

    # 设置触发沿
    trigActivationEnumNode = acqCtrl.contents.triggerActivation(acqCtrl)
    nRet = trigActivationEnumNode.setValueBySymbol(byref(trigActivationEnumNode), b"RisingEdge")
    if (nRet != 0):
        print("set TriggerActivation value [RisingEdge] fail!")
        # 释放相关资源
        trigActivationEnumNode.release(byref(trigActivationEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return -1

    # 需要释放Node资源
    trigActivationEnumNode.release(byref(trigActivationEnumNode))
    acqCtrl.contents.release(acqCtrl)
    return 0


def grabOne(camera, streamSource):
    # 创建control节点
    acqCtrlInfo = GENICAM_AcquisitionControlInfo()
    acqCtrlInfo.pCamera = pointer(camera)
    acqCtrl = pointer(GENICAM_AcquisitionControl())
    nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
    if (nRet != 0):
        print("create AcquisitionControl fail!")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1

    # 执行一次软触发
    trigSoftwareCmdNode = acqCtrl.contents.triggerSoftware(acqCtrl)
    nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
    if (nRet != 0):
        print("Execute triggerSoftware fail!")
        # 释放相关资源
        trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
        acqCtrl.contents.release(acqCtrl)
        streamSource.contents.release(streamSource)
        return -1

        # 释放相关资源
    trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
    acqCtrl.contents.release(acqCtrl)
    streamSource.contents.release(streamSource)

    return 0


frameCallbackFuncEx = callbackFuncEx(onGetFrameEx)


def demo():
    # 发现相机
    cameraCnt, cameraList = enumCameras()
    if cameraCnt is None:
        return -1

    # 显示相机信息
    for index in range(0, cameraCnt):
        camera = cameraList[index]
        # print("\nCamera Id = " + str(index))
        # print("Key           = " + str(camera.getKey(camera)))
        # print("vendor name   = " + str(camera.getVendorName(camera)))
        # print("Model  name   = " + str(camera.getModelName(camera)))
        # print("Serial number = " + str(camera.getSerialNumber(camera)))

    camera = cameraList[0]

    # 打开相机
    openCamera(camera)

    # 创建流对象
    streamSourceInfo = GENICAM_StreamSourceInfo()
    streamSourceInfo.channelId = 0
    streamSourceInfo.pCamera = pointer(camera)
    streamSource = pointer(GENICAM_StreamSource())
    nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
    if (nRet != 0):
        print("create StreamSource fail!")
        return -1
    setSoftTriggerConf(camera)
    # 开始拉流
    nRet = streamSource.contents.startGrabbing(streamSource, c_ulonglong(0),
                                               c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
    if (nRet != 0):
        print("startGrabbing fail!")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1

    # 软触发取一张图
    nRet = grabOne(camera, streamSource)
    if (nRet != 0):
        print("grabOne fail!")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1
    else:
        print("trigger time: " + str(datetime.datetime.now()))
    # 主动取图
    frame = pointer(GENICAM_Frame())
    nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(1000))
    if (nRet != 0):
        print("SoftTrigger getFrame fail! timeOut [1000]ms")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1
    else:
        print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
        print("get frame time: " + str(datetime.datetime.now()))
    save_image_file_by_frame(frame, 'd:/znwj/dahua/test1.bmp')

    # 软触发取一张图
    nRet = grabOne(camera, streamSource)
    if (nRet != 0):
        print("grabOne fail!")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1
    else:
        print("trigger time: " + str(datetime.datetime.now()))
    # 主动取图
    frame = pointer(GENICAM_Frame())
    nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(1000))
    if (nRet != 0):
        print("SoftTrigger getFrame fail! timeOut [1000]ms")
        # 释放相关资源
        streamSource.contents.release(streamSource)
        return -1
    else:
        print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
        print("get frame time: " + str(datetime.datetime.now()))
    save_image_file_by_frame(frame, 'd:/znwj/dahua/test2.bmp')

    return 0


if __name__ == "__main__":
    nRet = demo()
    if nRet != 0:
        print("Some Error happend")
    print("--------- Demo end ---------")
    # 3s exit
    time.sleep(3)
