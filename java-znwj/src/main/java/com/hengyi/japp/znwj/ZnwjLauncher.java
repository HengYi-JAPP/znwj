package com.hengyi.japp.znwj;

import io.vertx.core.DeploymentOptions;
import io.vertx.core.Launcher;
import io.vertx.core.Vertx;
import io.vertx.core.VertxOptions;
import lombok.extern.slf4j.Slf4j;

import java.util.concurrent.TimeUnit;

/**
 * @author jzb 2019-11-01
 */
@Slf4j
public class ZnwjLauncher extends Launcher {

    public static void main(String[] args) {
        new ZnwjLauncher().dispatch(args);
    }

    @Override
    public void beforeStartingVertx(VertxOptions options) {
        options.setMaxEventLoopExecuteTime(10)
                .setMaxEventLoopExecuteTimeUnit(TimeUnit.SECONDS)
                .setMaxWorkerExecuteTime(1)
                .setMaxWorkerExecuteTimeUnit(TimeUnit.HOURS);
    }

    @Override
    public void afterStartingVertx(Vertx vertx) {
        ZnwjModule.init(vertx);
    }

    @Override
    public void handleDeployFailed(Vertx vertx, String mainVerticle, DeploymentOptions deploymentOptions, Throwable cause) {
        log.error("handleDeployFailed[" + mainVerticle + "]", cause);
        super.handleDeployFailed(vertx, mainVerticle, deploymentOptions, cause);
    }

    @Override
    public void beforeStoppingVertx(Vertx vertx) {
        // todo 关闭 python
        log.debug("close python");
    }
}
