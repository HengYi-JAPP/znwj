import asyncio
import time
from threading import current_thread


def handle_next_rfid(rfid):
    time.sleep(3);
    print('EchoClient: {}: {}'.format(current_thread().name, rfid))


class EchoClient(asyncio.Protocol):
    def __init__(self):
        self.buf_data = ''

    def data_received(self, data):
        self.buf_data += data
        handle_next_rfid(data)

    def connection_lost(self, exc):
        print('server closed the connection')


loop = asyncio.get_event_loop()
task = loop.create_connection(EchoClient, '127.0.0.1', 8023)
loop.create_task(task)
loop.run_forever()
print("done")
loop.close()
