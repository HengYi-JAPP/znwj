#!/usr/bin/env python
# coding: utf-8

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
camera = app._camera_msg._cameras[0]
camera.grab_by_rfid('0000')
