package com.hengyi.japp.znwj.application;

import com.google.inject.ImplementedBy;
import com.hengyi.japp.znwj.application.internal.BackendServiceImpl;
import com.hengyi.japp.znwj.domain.SilkInfo;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * @author jzb 2019-11-20
 */
@ImplementedBy(BackendServiceImpl.class)
public interface BackendService {

    Mono<Map<String, Object>> start();

    void handleRfid(MqttMessage rfidValue);

    Mono<SilkInfo> handleDetectResult(MqttMessage message);

    void updateStatistic(SilkInfo silkInfo);

    Mono<Map<String, Object>> info();

    Mono<Map<String, Object>> stop();

    enum Status {
        INIT, RUNNING, STOPPED, ERROR
    }
}
