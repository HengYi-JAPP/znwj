import paho.mqtt.subscribe as subscribe

from constant import DETECT_TOPIC


def on_message(client, userdata, msg):
    print('mqtt msg' + str(msg.payload))


subscribe.callback(on_message, DETECT_TOPIC, hostname='192.168.0.94')
