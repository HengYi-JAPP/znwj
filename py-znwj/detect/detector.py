import logging


class Detector(object):
    def __init__(self, app):
        # self.__detector1 = Yolo(config)
        # self.__detector2 = resnet(config)
        pass

    def detect(self, rfid):
        logging.debug('Detector handled ' + rfid)
        pass
        # infos1 = self.__detector1.detect(code)
        # infos2 = self.__detector2.detect(code)
        # return json.dumps({
        #     'code': code,
        #     'detectExceptionInfos': infos1 + infos2
        # })
