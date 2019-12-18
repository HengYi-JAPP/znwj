import selectors
import socket
import threading


def _loop(message, selector, sock):
    while True:
        events = selector.select()
        if events:
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    message.read(sock)
        if not selector.get_map():
            break


# rfid 读取 daemon 线程
# 可能会需要读取很多的 rfid 点位，所以单独的方法
# todo 实现接口 read()
def start_daemon(message, t_name):
    message._selector = selector = selectors.DefaultSelector()
    message._sock = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(message._addr)
    # sock.setblocking(False)
    # sock.connect_ex(self._addr)
    selector.register(sock, selectors.EVENT_READ)

    daemon = threading.Thread(target=_loop, args=(message, selector, sock), name=t_name)
    daemon.setDaemon(True)
    daemon.start()
    return daemon
