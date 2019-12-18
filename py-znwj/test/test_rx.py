import asyncio
from threading import current_thread

from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject


class EchoClient(asyncio.Protocol):
    def __init__(self, sink):
        self.sink = sink

    def data_received(self, data):
        print('EchoClient: {}'.format(current_thread().name))
        sink.on_next(data)

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()


loop = asyncio.get_event_loop()
sink = Subject()
aio_scheduler = AsyncIOScheduler(loop=loop)

sink.subscribe(
    on_next=lambda it: print('on_next: {} {}'.format(current_thread().name, it)),
    scheduler=aio_scheduler
)

coro = loop.create_connection(lambda: EchoClient(sink), '127.0.0.1', 8023)
loop.run_until_complete(coro)
loop.run_forever()
print("done")
loop.close()
