package com.hengyi.japp.znwj.interfaces.python.internal;

import com.google.common.collect.Maps;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.inject.name.Named;
import com.hengyi.japp.znwj.application.BackendService.Status;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.python.PythonService;
import com.hengyi.japp.znwj.verticle.BackendVerticle;
import io.vertx.core.Vertx;
import io.vertx.core.buffer.Buffer;
import io.vertx.core.json.JsonObject;
import io.vertx.mqtt.MqttEndpoint;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Date;
import java.util.Map;
import java.util.Objects;

import static com.hengyi.japp.znwj.Constant.DETECT_RESULT_TOPIC;
import static com.hengyi.japp.znwj.application.BackendService.Status.*;
import static io.netty.handler.codec.mqtt.MqttConnectReturnCode.CONNECTION_ACCEPTED;
import static java.util.Optional.ofNullable;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class PythonServiceImpl implements PythonService {
    private final Vertx vertx;
    private final JsonObject detectConfig;
    private Status status = INIT;
    private Date startDateTime;
    private Throwable error;
    private Map<String, Detector> detectorMap = Maps.newConcurrentMap();

    @Inject
    private PythonServiceImpl(Vertx vertx, @Named("detectConfig") JsonObject detectConfig) {
        this.vertx = vertx;
        this.detectConfig = detectConfig;
    }

    @Override
    public Mono<SilkInfo> detect(SilkInfo silkInfo) {
        return Flux.fromIterable(detectorMap.values())
                .doOnNext(it -> it.detect(silkInfo))
                .ignoreElements()
                .then(Mono.just(silkInfo));
    }

    @Override
    public void handler(MqttEndpoint endpoint) {
        if (StringUtils.startsWith(endpoint.clientIdentifier(), "detect")) {
            detectorMap.compute(endpoint.clientIdentifier(), (k, v) -> {
                if (v == null) {
                    v = new Detector(endpoint);
                    endpoint.subscribeHandler(v::subscribeHandler);
                    endpoint.unsubscribeHandler(v::unsubscribeHandler);
                    endpoint.disconnectHandler(it -> detectorMap.remove(k));
                    endpoint.closeHandler(it -> detectorMap.remove(k));
                    endpoint.pingHandler(it -> {
                        System.out.println("Ping received from client");
                    });
                    endpoint.publishHandler(message -> {
                        final String topicName = message.topicName();
                        log.debug("topicName {}", topicName);
                        if (Objects.equals(DETECT_RESULT_TOPIC, topicName)) {
                            final Buffer payload = message.payload();
                            vertx.eventBus().send(BackendVerticle.DETECT_RESULT, payload.getBytes());
                        }
                    });
                    endpoint.accept(false);
                } else {
                    endpoint.reject(CONNECTION_ACCEPTED);
                }
                return v;
            });
        }
    }

    @Override
    public Mono<Map<String, Object>> info() {
        return Mono.fromCallable(() -> {
            final Map<String, Object> map = Maps.newHashMap();
            map.put("status", status);
            map.put("startDateTime", startDateTime);
            map.put("detectors", detectorMap.keySet());
            ofNullable(error).map(Throwable::getMessage).ifPresent(it -> map.put("errorMessage", it));
            return map;
        });
    }

    @Override
    public Mono<Map<String, Object>> start() {
        return Mono.fromCallable(() -> {
            return null;
        }).doOnSuccess(it -> {
            status = RUNNING;
            startDateTime = new Date();
            error = null;
        }).doOnError(e -> {
            status = ERROR;
            error = e;
        }).then(info());
    }

    @Override
    public Mono<Map<String, Object>> stop() {
        return Mono.fromCallable(() -> {
            return null;
        }).doOnSuccess(it -> {
            status = STOPPED;
            error = null;
        }).doOnError(e -> {
            status = ERROR;
            error = e;
        }).then(info());
    }
}
