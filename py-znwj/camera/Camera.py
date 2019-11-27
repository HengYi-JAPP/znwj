class Camera(object):
    def __init__(self, name, config):
        self.__name = name
        self.__db_path = config.get('dbPath', '/home/znwj/db')

    async def grab(self, code):
        print('camera ' + self.__name + ' : ' + code)
