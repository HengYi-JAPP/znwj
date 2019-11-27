#!/usr/bin/python3
# coding: utf-8
import logging
import os

import paho.mqtt.client as mqtt
import yaml

from camera.Cameras import Cameras
from detect.detector import Detector

DETECT_TOPIC = '/znwj/detect'
DETECT_RESULT_TOPIC = '/znwj/detect/result'
DETECT_ERROR_TOPIC = '/znwj/detect/error'

config_file = os.getenv('ZNWJ_CONFIG', '/home/znwj/config.yml')
CONFIG = yaml.safe_load(open(config_file))

logging_config = CONFIG.get('logging', {})
level = logging_config.get('level', logging.INFO)
format = logging_config.get('format')
logging.basicConfig(level=level, format=format)

mqtt_config = CONFIG.get('mqtt', {})
HOST = mqtt_config.get('host', 'localhost')
PORT = mqtt_config.get('port', 1883)

DETECTOR = Detector(CONFIG)
CAMERAS = Cameras(CONFIG)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code: " + mqtt.connack_string(rc))
    client.subscribe(DETECT_TOPIC, qos=1)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.error('Unexpected on_disconnect')


def on_message(client, userdata, msg):
    logging.debug("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    if msg.topic == DETECT_TOPIC:
        code = msg.payload.decode("utf-8")
        CAMERAS.grab(code)
        result = DETECTOR.detect(code)
        client.publish(DETECT_RESULT_TOPIC, result)


CAMERAS.grab('123')
print('grab finish')

CLIENT = mqtt.Client('detect')
CLIENT.on_connect = on_connect
CLIENT.on_message = on_message
CLIENT.on_disconnect = on_disconnect
CLIENT.connect(HOST, PORT)
CLIENT.loop_forever()
