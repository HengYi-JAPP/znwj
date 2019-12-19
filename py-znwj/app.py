import asyncio
import logging
import os
import sys
import threading

import paho.mqtt.client as mqtt

from constant import APP, DETECT_TOPIC, ERROR_TOPIC, START_TOPIC, STOP_TOPIC
from py_znwj import PyZnwj

loop = asyncio.get_event_loop()

if len(sys.argv) == 1:
    path = os.getenv('ZNWJ_PATH')
    if not path:
        path = 'd:/znwj'
else:
    path = sys.argv[1]

app = PyZnwj(path, loop)
app._mqttc = mqttc = mqtt.Client(APP)


def on_connect(client, userdata, rc):
    logging.info('mqtt on_connect')


def on_message(client, userdata, msg):
    logging.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if DETECT_TOPIC == msg.topic:
        code = msg.payload.decode("utf-8")
        # app.handle_next_rfid(code)

    elif START_TOPIC == msg.topic:
        app._running = True

    elif STOP_TOPIC == msg.topic:
        app._running = False

    else:
        logging.error('no handler,topic[{}],message[{}]'.format(msg.topic, str(msg.payload)))
        pass


def on_disconnect(client, userdata, rc):
    if rc != 0:
        raise Exception('mqtt_disconnect')


mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.connect(app.config('mqtt.host'), app.config('mqtt.port', 1883))
mqttc.subscribe(DETECT_TOPIC, qos=1)
mqttc.subscribe(ERROR_TOPIC, qos=1)
mqttc.subscribe(START_TOPIC, qos=1)
mqttc.subscribe(STOP_TOPIC, qos=1)
daemon = threading.Thread(target=mqttc.loop_forever, name='mqttc')
daemon.setDaemon(True)
daemon.start()

loop.run_forever()
