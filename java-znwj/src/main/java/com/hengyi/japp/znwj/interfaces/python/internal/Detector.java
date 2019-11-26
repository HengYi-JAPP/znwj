package com.hengyi.japp.znwj.interfaces.python.internal;

import com.hengyi.japp.znwj.domain.SilkInfo;
import io.netty.handler.codec.mqtt.MqttQoS;
import io.vertx.core.buffer.Buffer;
import io.vertx.mqtt.MqttEndpoint;
import io.vertx.mqtt.MqttTopicSubscription;
import io.vertx.mqtt.messages.MqttSubscribeMessage;
import io.vertx.mqtt.messages.MqttUnsubscribeMessage;
import lombok.Getter;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

import java.util.List;
import java.util.Objects;

import static com.hengyi.japp.znwj.Constant.DETECT_TOPIC;
import static java.util.stream.Collectors.toList;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@ToString(onlyExplicitlyIncluded = true)
public class Detector {
    private final MqttEndpoint endpoint;
    @ToString.Include
    @Getter
    private boolean subscribed;
    @Getter
    private List<MqttTopicSubscription> mqttTopicSubscriptions;
    @Getter
    private List<String> unsubscribeTopics;

    Detector(MqttEndpoint endpoint) {
        this.endpoint = endpoint;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        Detector detector = (Detector) o;
        return Objects.equals(endpoint.clientIdentifier(), detector.endpoint.clientIdentifier());
    }

    @Override
    public int hashCode() {
        return Objects.hash(endpoint.clientIdentifier());
    }

    void subscribeHandler(MqttSubscribeMessage subscribe) {
        mqttTopicSubscriptions = subscribe.topicSubscriptions();
        final List<MqttQoS> grantedQosLevels = mqttTopicSubscriptions.stream()
                .map(MqttTopicSubscription::qualityOfService)
                .collect(toList());
        endpoint.subscribeAcknowledge(subscribe.messageId(), grantedQosLevels);
        subscribed = true;
    }

    public void unsubscribeHandler(MqttUnsubscribeMessage unsubscribe) {
        unsubscribeTopics = unsubscribe.topics();
        endpoint.unsubscribeAcknowledge(unsubscribe.messageId());
        subscribed = false;
    }

    public void detect(SilkInfo silkInfo) {
        if (!subscribed) {
            log.warn("{} 的 subscribed={}，却在发送队列！", endpoint.clientIdentifier(), subscribed);
        }
        final String code = silkInfo.getCode();
        final Buffer buffer = Buffer.buffer(code);
        endpoint.publish(DETECT_TOPIC, buffer, MqttQoS.AT_LEAST_ONCE, false, false, ar -> {
            if (ar.succeeded()) {
                log.debug(DETECT_TOPIC + " publish " + code);
            } else {
                log.error(DETECT_TOPIC + " publish " + code, ar.cause());
            }
        });
    }
}
