class Cameras(object):
    def __init__(self, config):
        self.__db_path = config.get('dbPath', '/home/znwj/db')

    def grab(self, code):
        pass
