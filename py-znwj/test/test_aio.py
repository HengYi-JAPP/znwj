import asyncio
import os
import sys
import time
from threading import current_thread

from py_znwj import PyZnwj

if len(sys.argv) == 1:
    path = os.getenv('ZNWJ_PATH')
    if not path:
        path = '/home/znwj'
else:
    path = sys.argv[1]

loop = asyncio.get_event_loop()
print(loop)
app = PyZnwj(path)


def handle_next_rfid(rfid):
    time.sleep(3);
    print('EchoClient: {}: {}'.format(current_thread().name, rfid))


async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8023)
    while True:
        rfid = await reader.read(4)
        app.handle_next_rfid(rfid)


loop = asyncio.get_event_loop()
loop.create_task(app._sick_msg.start())
# loop.create_task(main())

print('test')

loop.run_forever()
