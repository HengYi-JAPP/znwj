package com.hengyi.japp.znwj.interfaces.python.internal;

import com.google.common.collect.Maps;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.hengyi.japp.znwj.application.BackendService;
import com.hengyi.japp.znwj.application.BackendService.Status;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.python.PythonService;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;
import reactor.core.publisher.Mono;

import java.util.Date;
import java.util.Map;

import static com.hengyi.japp.znwj.Constant.DETECT_RESULT_TOPIC;
import static com.hengyi.japp.znwj.Constant.DETECT_TOPIC;
import static com.hengyi.japp.znwj.ZnwjModule.getInstance;
import static com.hengyi.japp.znwj.application.BackendService.Status.*;
import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.Optional.ofNullable;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class PythonServiceImpl implements PythonService, MqttCallback {
    private final MqttClient mqttClient;
    private Status status = INIT;
    private Date startDateTime;
    private Throwable error;

    @Inject
    private PythonServiceImpl(MqttClient mqttClient) {
        this.mqttClient = mqttClient;
    }

    @Override
    public Mono<SilkInfo> detect(SilkInfo silkInfo) {
        return Mono.fromCallable(() -> {
            final byte[] bytes = silkInfo.getCode().getBytes(UTF_8);
            final MqttMessage message = new MqttMessage(bytes);
            message.setQos(1);
            mqttClient.publish(DETECT_TOPIC, message);
            return silkInfo;
        });
    }

    @Override
    public Mono<Map<String, Object>> info() {
        return Mono.fromCallable(() -> {
            final Map<String, Object> map = Maps.newHashMap();
            map.put("status", status);
            map.put("startDateTime", startDateTime);
            ofNullable(error).map(Throwable::getMessage).ifPresent(it -> map.put("errorMessage", it));
            return map;
        });
    }

    @Override
    public Mono<Map<String, Object>> start() {
        return Mono.fromCallable(() -> {
            if (!mqttClient.isConnected()) {
                final MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
                mqttConnectOptions.setAutomaticReconnect(true);
                mqttConnectOptions.setCleanSession(true);
                mqttClient.connect(mqttConnectOptions);
                mqttClient.setCallback(this);
                mqttClient.subscribe(DETECT_RESULT_TOPIC);
                status = RUNNING;
                startDateTime = new Date();
                error = null;
            }
            return mqttClient;
        }).doOnError(e -> {
            status = ERROR;
            error = e;
        }).then(info());
    }

    @Override
    public void connectionLost(Throwable cause) {

    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        final BackendService backendService = getInstance(BackendService.class);
        backendService.handleDetectResult(message.getPayload()).subscribe();
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {

    }
}
