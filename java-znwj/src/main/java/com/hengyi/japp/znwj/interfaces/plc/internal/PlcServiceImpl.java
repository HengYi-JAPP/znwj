package com.hengyi.japp.znwj.interfaces.plc.internal;

import com.google.common.collect.Maps;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.inject.name.Named;
import com.hengyi.japp.znwj.application.BackendService;
import com.hengyi.japp.znwj.application.BackendService.Status;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.plc.PlcService;
import io.vertx.core.json.JsonObject;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

import java.util.Date;
import java.util.Map;

import static com.hengyi.japp.znwj.ZnwjModule.getInstance;
import static com.hengyi.japp.znwj.application.BackendService.Status.*;
import static java.util.Optional.ofNullable;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class PlcServiceImpl implements PlcService {
    private Status status = INIT;
    private Date startDateTime;
    private Throwable error;

    @Inject
    private PlcServiceImpl(@Named("plcConfig") JsonObject plcConfig) {
    }

    @Override
    public Mono<SilkInfo> handleEliminate(SilkInfo silkInfo) {
        if (silkInfo.isEliminateHandled()) {
            return Mono.just(silkInfo);
        }
        final BackendService backendService = getInstance(BackendService.class);
        final Mono<SilkInfo> result$ = Mono.just(silkInfo);
        if (silkInfo.hasException()) {
            // fixme 处理剔除信息
        }
        log.debug("{}  剔除", silkInfo);
        return result$.doOnNext(backendService::updateStatistic);
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
            // fixme plc连接启动处理
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
}
