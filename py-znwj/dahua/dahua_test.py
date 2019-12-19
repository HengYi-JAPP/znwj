import asyncio
import os
import platform
import sys

from py_znwj import PyZnwj

loop = asyncio.get_event_loop()

if len(sys.argv) == 1:
    path = os.getenv('ZNWJ_PATH')
    if not path:
        if 'Linux' == platform.system():
            path = '/home/znwj'
        else:
            path = 'd:/znwj'
else:
    path = sys.argv[1]

app = PyZnwj(path, loop)
