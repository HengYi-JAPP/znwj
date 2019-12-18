import asyncio

# sick 读卡器设置
# 读取不成功时为 0
no_good_read = '0000'


# sick rfid 读取
class SickMessage(object):
    def __init__(self, app):
        self._app = app
        self._current = None
        self._host = app.config('sick.host')
        self._port = app.config('sick.port', 2112)
        # rfid 定长读取
        self._len = (app.config('sick.data_len', 4))
        self._camera_msg = app._camera_msg

    async def start(self):
        reader, writer = await asyncio.open_connection(host=self._host, port=self._port)
        while True:
            recv_data = await reader.read(self._len)
            rfid = repr(recv_data)[2:-1]
            if rfid == no_good_read:
                continue
            if self._current == rfid:
                continue
            # if not self._app._running:
            #     continue
            print('{} handled {}'.format('sick', rfid))
            self._camera_msg.handle_next_rfid(rfid)
