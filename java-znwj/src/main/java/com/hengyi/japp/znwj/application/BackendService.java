package com.hengyi.japp.znwj.application;

import com.google.inject.ImplementedBy;
import com.hengyi.japp.znwj.application.internal.BackendServiceImpl;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * @author jzb 2019-11-20
 */
@ImplementedBy(BackendServiceImpl.class)
public interface BackendService {

    Mono<Void> handleRfidNum(int rfidNum);

    Mono<Void> handleDetectResult(DetectResult detectResult);

    Mono<Map<String, Object>> info();

    Mono<Map<String, Object>> start();

    Mono<Map<String, Object>> stop();

    enum Status {
        INIT, RUNNING, STOPPED, ERROR
    }
}
