package com.hengyi.japp.znwj.application.internal;

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
import io.vertx.core.json.JsonObject;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

import java.util.Map;

import static com.github.ixtf.japp.core.Constant.MAPPER;
import static com.hengyi.japp.znwj.Constant.*;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class BackendServiceImpl implements BackendService {
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
    public Mono<Void> handleRfidNum(int rfidNum) {
        return riambService.fetch(rfidNum).flatMap(silkInfo -> {
            if (silkInfo.hasMesAutoException()) {
                return plcService.handleEliminate(silkInfo);
            } else {
                return pythonService.detect(silkInfo);
            }
        }).doOnError(err -> log.error("", err)).then();
    }

    @Override
    public Mono<Void> handleDetectResult(byte[] bytes) {
        return Mono.fromCallable(() -> MAPPER.readValue(bytes, DetectResult.class))
                .map(silkInfoService::add)
                .flatMap(plcService::handleEliminate)
                .then();
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
