package com.hengyi.japp.znwj.verticle;

import com.github.ixtf.vertx.Jvertx;
import com.hengyi.japp.znwj.ZnwjModule;
import com.hengyi.japp.znwj.interfaces.rest.RestResolver;
import io.vertx.core.AbstractVerticle;
import io.vertx.core.CompositeFuture;
import io.vertx.core.Future;

import java.util.List;

import static java.util.stream.Collectors.toList;

/**
 * @author jzb 2019-10-24
 */
public class RestVerticle extends AbstractVerticle {

    @Override
    public void start(Future<Void> startFuture) throws Exception {
        final List<Future> futures = Jvertx.resolve(RestResolver.class)
                .map(it -> it.consumer(vertx, ZnwjModule::getInstance))
                .collect(toList());
        CompositeFuture.all(futures).<Void>mapEmpty().setHandler(startFuture);
    }

}
