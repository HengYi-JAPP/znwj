package com.hengyi.japp.znwj;

import com.hengyi.japp.znwj.verticle.AgentVerticle;
import com.hengyi.japp.znwj.verticle.BackendVerticle;
import com.hengyi.japp.znwj.verticle.RestVerticle;
import io.vertx.core.AbstractVerticle;
import io.vertx.core.DeploymentOptions;
import io.vertx.core.Future;

/**
 * @author jzb 2019-10-24
 */
public class MainVerticle extends AbstractVerticle {

    @Override
    public void start() throws Exception {
        ZnwjModule.init(vertx);
    }

    @Override
    public void start(Future<Void> startFuture) throws Exception {
        start();
        deployBackendVerticle()
                .compose(it -> deployRestVerticle())
                .compose(it -> deployAgentVerticle())
                .<Void>mapEmpty().setHandler(startFuture);
    }

    private Future<String> deployBackendVerticle() {
        return Future.future(p -> {
            final DeploymentOptions deploymentOptions = new DeploymentOptions()
                    .setWorker(true)
                    .setInstances(20);
            vertx.deployVerticle(BackendVerticle.class, deploymentOptions, p);
        });
    }

    private Future<String> deployRestVerticle() {
        return Future.future(p -> {
            final DeploymentOptions deploymentOptions = new DeploymentOptions()
                    .setWorker(true)
                    .setInstances(20);
            vertx.deployVerticle(RestVerticle.class, deploymentOptions, p);
        });
    }

    private Future<String> deployAgentVerticle() {
        return Future.future(p -> {
            final DeploymentOptions deploymentOptions = new DeploymentOptions()
                    .setInstances(20);
            vertx.deployVerticle(AgentVerticle.class, deploymentOptions, p);
        });
    }
}
