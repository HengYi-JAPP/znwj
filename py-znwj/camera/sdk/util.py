import logging
import struct

from camera.sdk.ImageConvert import *
from camera.sdk.MVSDK import *


class BITMAPFILEHEADER(Structure):
    _fields_ = [
        ('bfType', c_ushort),
        ('bfSize', c_uint),
        ('bfReserved1', c_ushort),
        ('bfReserved2', c_ushort),
        ('bfOffBits', c_uint),
    ]


class BITMAPINFOHEADER(Structure):
    _fields_ = [
        ('biSize', c_uint),
        ('biWidth', c_int),
        ('biHeight', c_int),
        ('biPlanes', c_ushort),
        ('biBitCount', c_ushort),
        ('biCompression', c_uint),
        ('biSizeImage', c_uint),
        ('biXPelsPerMeter', c_int),
        ('biYPelsPerMeter', c_int),
        ('biClrUsed', c_uint),
        ('biClrImportant', c_uint),
    ]


# 调色板，只有8bit及以下才需要
class RGBQUAD(Structure):
    _fields_ = [
        ('rgbBlue', c_ubyte),
        ('rgbGreen', c_ubyte),
        ('rgbRed', c_ubyte),
        ('rgbReserved', c_ubyte),
    ]


# 枚举相机
def enumCameras():
    # 获取系统单例
    system = pointer(GENICAM_System())
    nRet = GENICAM_getSystemInstance(byref(system))
    if (nRet != 0):
        raise Exception("getSystemInstance fail!")

    # 发现相机
    cameraList = pointer(GENICAM_Camera())
    cameraCnt = c_uint()
    nRet = system.contents.discovery(system, byref(cameraList), byref(cameraCnt), c_int(GENICAM_EProtocolType.typeAll));
    if (nRet != 0):
        raise Exception("discovery fail!")
    elif cameraCnt.value < 1:
        logging.error("discovery no camera!")
        return None, None
    else:
        logging.debug("cameraCnt: " + str(cameraCnt.value))
        return cameraCnt.value, cameraList


def save_image_file_by_frame(frame, path):
    nRet = frame.contents.valid(frame)
    if (nRet != 0):
        # 释放驱动图像缓存资源
        frame.contents.release(frame)
        logging.error("frame is invalid!")
        raise Exception("frame is invalid!")

    # 将裸数据图像拷出
    imageSize = frame.contents.getImageSize(frame)
    buffAddr = frame.contents.getImage(frame)
    frameBuff = c_buffer(b'\0', imageSize)
    memmove(frameBuff, c_char_p(buffAddr), imageSize)

    # 给转码所需的参数赋值
    convertParams = IMGCNV_SOpenParam()
    convertParams.dataSize = imageSize
    convertParams.height = frame.contents.getImageHeight(frame)
    convertParams.width = frame.contents.getImageWidth(frame)
    convertParams.paddingX = frame.contents.getImagePaddingX(frame)
    convertParams.paddingY = frame.contents.getImagePaddingY(frame)
    convertParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

    # 释放驱动图像缓存资源
    frame.contents.release(frame)

    # 保存bmp图片
    bmpInfoHeader = BITMAPINFOHEADER()
    bmpFileHeader = BITMAPFILEHEADER()

    uRgbQuadLen = 0
    rgbQuad = (RGBQUAD * 256)()  # 调色板信息
    rgbBuff = c_buffer(b'\0', convertParams.height * convertParams.width * 3)

    # 如果图像格式是 Mono8 不需要转码
    if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
        # 初始化调色板rgbQuad 实际应用中 rgbQuad 只需初始化一次
        for i in range(0, 256):
            rgbQuad[i].rgbBlue = rgbQuad[i].rgbGreen = rgbQuad[i].rgbRed = i

        uRgbQuadLen = sizeof(RGBQUAD) * 256
        bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + uRgbQuadLen + convertParams.dataSize
        bmpInfoHeader.biBitCount = 8
    else:
        # 转码 => BGR24
        rgbSize = c_int()
        nRet = IMGCNV_ConvertToBGR24(cast(frameBuff, c_void_p), byref(convertParams), \
                                     cast(rgbBuff, c_void_p), byref(rgbSize))

        if (nRet != 0):
            logging.error("image convert fail! errorCode = " + str(nRet))
            return

        bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + rgbSize.value
        bmpInfoHeader.biBitCount = 24

    bmpFileHeader.bfType = 0x4D42  # 文件头类型 'BM'(42 4D)
    bmpFileHeader.bfReserved1 = 0  # 保留字
    bmpFileHeader.bfReserved2 = 0  # 保留字
    bmpFileHeader.bfOffBits = 54 + uRgbQuadLen  # 位图像素数据的起始位置

    bmpInfoHeader.biSize = 40  # 信息头所占字节数
    bmpInfoHeader.biWidth = convertParams.width
    bmpInfoHeader.biHeight = -convertParams.height
    bmpInfoHeader.biPlanes = 1  # 位图平面数

    bmpInfoHeader.biCompression = 0  # 压缩类型，0 即不压缩
    bmpInfoHeader.biSizeImage = 0
    bmpInfoHeader.biXPelsPerMeter = 0
    bmpInfoHeader.biYPelsPerMeter = 0
    bmpInfoHeader.biClrUsed = 0
    bmpInfoHeader.biClrImportant = 0

    imageFile = open(path, 'wb+')

    imageFile.write(struct.pack('H', bmpFileHeader.bfType))
    imageFile.write(struct.pack('I', bmpFileHeader.bfSize))
    imageFile.write(struct.pack('H', bmpFileHeader.bfReserved1))
    imageFile.write(struct.pack('H', bmpFileHeader.bfReserved2))
    imageFile.write(struct.pack('I', bmpFileHeader.bfOffBits))

    imageFile.write(struct.pack('I', bmpInfoHeader.biSize))
    imageFile.write(struct.pack('i', bmpInfoHeader.biWidth))
    imageFile.write(struct.pack('i', bmpInfoHeader.biHeight))
    imageFile.write(struct.pack('H', bmpInfoHeader.biPlanes))
    imageFile.write(struct.pack('H', bmpInfoHeader.biBitCount))
    imageFile.write(struct.pack('I', bmpInfoHeader.biCompression))
    imageFile.write(struct.pack('I', bmpInfoHeader.biSizeImage))
    imageFile.write(struct.pack('i', bmpInfoHeader.biXPelsPerMeter))
    imageFile.write(struct.pack('i', bmpInfoHeader.biYPelsPerMeter))
    imageFile.write(struct.pack('I', bmpInfoHeader.biClrUsed))
    imageFile.write(struct.pack('I', bmpInfoHeader.biClrImportant))

    if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
        # 写入调色板信息
        for i in range(0, 256):
            imageFile.write(struct.pack('B', rgbQuad[i].rgbBlue))
            imageFile.write(struct.pack('B', rgbQuad[i].rgbGreen))
            imageFile.write(struct.pack('B', rgbQuad[i].rgbRed))
            imageFile.write(struct.pack('B', rgbQuad[i].rgbReserved))

        imageFile.writelines(frameBuff)
    else:
        imageFile.writelines(rgbBuff)

    imageFile.close()
