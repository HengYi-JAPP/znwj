package com.hengyi.japp.znwj.verticle;

import com.google.inject.Inject;
import com.hengyi.japp.znwj.ZnwjModule;
import com.hengyi.japp.znwj.application.BackendService;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import io.vertx.core.AbstractVerticle;
import io.vertx.core.eventbus.Message;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

import static com.github.ixtf.japp.core.Constant.MAPPER;

/**
 * @author jzb 2019-10-24
 */
@Slf4j
public class BackendVerticle extends AbstractVerticle {
    public static final String NEXT_RFID_NUM = "znwj:backend:NEXT_RFID_NUM";
    public static final String DETECT_RESULT = "znwj:backend:DETECT_RESULT";
    @Inject
    private BackendService backendService;

    @Override
    public void start() throws Exception {
        ZnwjModule.injectMembers(this);
        vertx.eventBus().consumer(NEXT_RFID_NUM, this::handleRfidNum);
        vertx.eventBus().consumer(DETECT_RESULT, this::handleDetectResult);
    }

    private void handleRfidNum(Message<Integer> reply) {
        backendService.handleRfidNum(reply.body())
                .doOnError(err -> {
                    log.error("", err);
                    reply.fail(400, err.getMessage());
                })
                .doOnSuccess(reply::reply)
                .subscribe();
    }

    private void handleDetectResult(Message<byte[]> reply) {
        Mono.fromCallable(() -> MAPPER.readValue(reply.body(), DetectResult.class))
                .flatMap(backendService::handleDetectResult)
                .doOnError(err -> {
                    log.error("", err);
                    reply.fail(400, err.getMessage());
                })
                .doOnSuccess(reply::reply)
                .subscribe();
    }

}
