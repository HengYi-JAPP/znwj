package com.hengyi.japp.znwj.application.internal;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.hengyi.japp.znwj.application.BackendService;
import com.hengyi.japp.znwj.application.SilkInfoService;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.camera.CameraService;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import com.hengyi.japp.znwj.interfaces.python.PythonService;
import com.hengyi.japp.znwj.interfaces.plc.PlcService;
import com.hengyi.japp.znwj.interfaces.riamb.RiambService;
import io.vertx.core.Vertx;
import io.vertx.core.json.JsonObject;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

import java.nio.file.Path;
import java.util.Map;

import static com.hengyi.japp.znwj.Constant.WEBSOCKET_GLOBAL;
import static com.hengyi.japp.znwj.Constant.silkInfoWebsocketMessage;

/**
 * @author jzb 2019-11-20
 */
@Slf4j
@Singleton
public class BackendServiceImpl implements BackendService {
    private final Vertx vertx;
    private final PlcService plcService;
    private final RiambService riambService;
    private final CameraService cameraService;
    private final PythonService pythonService;
    private final SilkInfoService silkInfoService;

    @Inject
    private BackendServiceImpl(Vertx vertx, SilkInfoService silkInfoService, PythonService pythonService, PlcService plcService, RiambService riambService, CameraService cameraService) {
        this.vertx = vertx;
        this.silkInfoService = silkInfoService;
        this.plcService = plcService;
        this.riambService = riambService;
        this.cameraService = cameraService;
        this.pythonService = pythonService;
    }

    @Override
    public Mono<Void> handleRfidNum(int rfidNum) {
        final Mono<SilkInfo> silkInfo$ = riambService.fetch(rfidNum);
        final Mono<Path> imgPath$ = cameraService.fetch();
        return Mono.zip(silkInfo$, imgPath$).flatMap(tuple -> {
            final SilkInfo silkInfo = tuple.getT1();
            final Path imgPath = tuple.getT2();
            return silkInfoService.preapareDetectData(silkInfo, imgPath);
        }).flatMap(pythonService::detect).then();
    }

    @Override
    public Mono<Void> handleDetectResult(DetectResult detectResult) {
        return Mono.fromCallable(() -> {
            final String code = detectResult.getCode();
            final SilkInfo silkInfo = silkInfoService.find(code);
            silkInfo.add(detectResult);
            return silkInfo;
        }).flatMap(plcService::handleEliminate).doOnNext(silkInfo -> {
            final JsonObject message = silkInfoWebsocketMessage(silkInfo);
            System.out.println(message);
            vertx.eventBus().publish(WEBSOCKET_GLOBAL, message);
        }).then();
    }

    @Override
    public Mono<Map<String, Object>> info() {
        final Mono<Map<String, Object>> plc$ = plcService.info();
        final Mono<Map<String, Object>> detect$ = pythonService.info();
        final Mono<Map<String, Object>> camera$ = cameraService.info();
        return Mono.zip(plc$, detect$, camera$).map(tuple -> {
            final Map<String, Object> plc = tuple.getT1();
            final Map<String, Object> detect = tuple.getT2();
            final Map<String, Object> camera = tuple.getT3();
            return Map.of("plc", plc, "detect", detect, "camera", camera);
        });
    }

    @Override
    synchronized public Mono<Map<String, Object>> start() {
        try {
            silkInfoService.start();
            cameraService.start().block();
            plcService.start().block();
            pythonService.start().block();
            return info();
        } catch (Throwable e) {
            return Mono.error(e);
        }
    }

    @Override
    synchronized public Mono<Map<String, Object>> stop() {
        try {
            silkInfoService.stop();
            cameraService.stop().block();
            plcService.stop().block();
            pythonService.stop().block();
            return info();
        } catch (Throwable e) {
            return Mono.error(e);
        }
    }

}
