from daemon.daemon import start_daemon


# sick rfid 读取
class SickMessage(object):
    def __init__(self, app):
        self._app = app
        self._addr = (app.config('sick.host'), app.config('sick.port', 2112))
        # rfid 定长读取
        self._data_len = (app.config('sick.data_len', 4))
        self.__daemon = start_daemon(self, 'SickMessageRead');

    def read(self, sock):
        try:
            recv_data = sock.recv(self._data_len)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            return
        if recv_data:
            rfid = repr(recv_data)[2:-1]
            # logging.debug('rfid[{}],[{}]'.format(rfid, len(rfid)))
            # sick 读卡器设置
            # 读取不成功时为 0
            if rfid != '0':
                self._app.handle_next_rfid(rfid)
