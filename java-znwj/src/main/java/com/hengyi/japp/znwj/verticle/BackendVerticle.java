package com.hengyi.japp.znwj.verticle;

import com.google.inject.Inject;
import com.hengyi.japp.znwj.ZnwjModule;
import com.hengyi.japp.znwj.application.BackendService;
import io.vertx.core.AbstractVerticle;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;

import static com.hengyi.japp.znwj.Constant.DETECT_RESULT_TOPIC;
import static com.hengyi.japp.znwj.Constant.DETECT_TOPIC;

/**
 * @author jzb 2019-10-24
 */
@Slf4j
public class BackendVerticle extends AbstractVerticle implements MqttCallback {
    @Inject
    private MqttClient mqttClient;
    @Inject
    private BackendService backendService;

    @Override
    public void start() throws Exception {
        ZnwjModule.injectMembers(this);
        final MqttConnectOptions connOpts = new MqttConnectOptions();
        connOpts.setAutomaticReconnect(true);
        connOpts.setCleanSession(true);
        mqttClient.setCallback(this);
        mqttClient.connect(connOpts);
        mqttClient.subscribe(DETECT_TOPIC, 1);
        mqttClient.subscribe(DETECT_RESULT_TOPIC, 1);
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        switch (topic) {
            case DETECT_TOPIC: {
                backendService.handleRfid(message);
                return;
            }
            case DETECT_RESULT_TOPIC: {
                backendService.handleDetectResult(message);
                return;
            }
            default: {
                log.error("topic={} no handler", topic);
            }
        }
    }

    @Override
    public void connectionLost(Throwable cause) {
        log.error("", cause);
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
    }
}
