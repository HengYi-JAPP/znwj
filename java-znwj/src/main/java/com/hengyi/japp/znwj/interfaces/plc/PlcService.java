package com.hengyi.japp.znwj.interfaces.plc;

import com.google.inject.ImplementedBy;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.plc.internal.PlcServiceImpl;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * @author jzb 2019-11-20
 */
@ImplementedBy(PlcServiceImpl.class)
public interface PlcService {

    Mono<SilkInfo> handleEliminate(SilkInfo silkInfo);

    Mono<Map<String, Object>> info();

    Mono<Map<String, Object>> start();
}
