package com.hengyi.japp.znwj.application.internal;

import com.google.common.collect.Maps;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.hengyi.japp.znwj.application.BackendService;
import com.hengyi.japp.znwj.application.SilkInfoService;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.plc.PlcService;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import com.hengyi.japp.znwj.interfaces.python.PythonService;
import com.hengyi.japp.znwj.interfaces.riamb.RiambService;
import io.vertx.core.Vertx;
import io.vertx.core.buffer.Buffer;
import io.vertx.core.json.JsonObject;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.math.NumberUtils;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.Map;

import static com.github.ixtf.japp.core.Constant.MAPPER;
import static com.hengyi.japp.znwj.Constant.*;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class BackendServiceImpl implements BackendService {
    private final Map<Integer, Mono<SilkInfo>> rfidReadedMap = Maps.newConcurrentMap();
    private final Vertx vertx;
    private final PlcService plcService;
    private final RiambService riambService;
    private final PythonService pythonService;
    private final SilkInfoService silkInfoService;
    private BackendStatus status;

    @Inject
    private BackendServiceImpl(Vertx vertx, SilkInfoService silkInfoService, PythonService pythonService, PlcService plcService, RiambService riambService) {
        this.vertx = vertx;
        this.silkInfoService = silkInfoService;
        this.plcService = plcService;
        this.riambService = riambService;
        this.pythonService = pythonService;
    }

    @Override
    synchronized public Mono<Map<String, Object>> start() {
        try {
            silkInfoService.cleanUp();
            plcService.start().block();
            pythonService.start().block();
            return info();
        } catch (Throwable e) {
            return Mono.error(e);
        }
    }

    @Override
    public void handleRfid(MqttMessage message) {
        final Buffer buffer = Buffer.buffer(message.getPayload());
        final String rfidValue = buffer.toString();
        final int rfidNum = NumberUtils.toInt(rfidValue);
        // rfid 读取失败时返回为 0
        if (rfidNum > 0) {
            rfidReadedMap.compute(rfidNum, (k, v) -> {
                if (v != null) {
                    return v;
                }
                return riambService.fetch(k);
            });
        }
    }

    @Override
    public Mono<SilkInfo> handleDetectResult(MqttMessage message) {
        return Mono.fromCallable(() -> {
            final byte[] payload = message.getPayload();
            return MAPPER.readValue(payload, DetectResult.class);
        }).subscribeOn(Schedulers.elastic())
                .map(silkInfoService::add)
                .flatMap(plcService::handleEliminate);
    }

    @Override
    public void updateStatistic(SilkInfo silkInfo) {
        status.updateStatistic(silkInfo);
        final JsonObject silkInfoMessage = silkInfoWebsocketMessage(silkInfo);
        vertx.eventBus().publish(WEBSOCKET_GLOBAL, silkInfoMessage);
        final JsonObject backendInfoMessage = backendInfoWebsocketMessage(status);
        vertx.eventBus().publish(WEBSOCKET_GLOBAL, backendInfoMessage);
    }

    @Override
    public Mono<Map<String, Object>> info() {
        final Mono<Map<String, Object>> plc$ = plcService.info();
        final Mono<Map<String, Object>> detect$ = pythonService.info();
        return Mono.zip(plc$, detect$).map(tuple -> {
            final Map<String, Object> plc = tuple.getT1();
            final Map<String, Object> detect = tuple.getT2();
            return Map.of("plc", plc, "detect", detect);
        });
    }

    @Override
    synchronized public Mono<Map<String, Object>> stop() {
        try {
            silkInfoService.cleanUp();
            return info();
        } catch (Throwable e) {
            return Mono.error(e);
        }
    }

}
