package com.hengyi.japp.znwj.verticle;

import com.google.inject.Inject;
import com.hengyi.japp.znwj.ZnwjModule;
import com.hengyi.japp.znwj.interfaces.python.PythonService;
import io.vertx.core.AbstractVerticle;
import io.vertx.mqtt.MqttServer;

import static io.netty.handler.codec.mqtt.MqttConnectReturnCode.CONNECTION_REFUSED_IDENTIFIER_REJECTED;

/**
 * @author jzb 2019-10-24
 */
public class MqttVerticle extends AbstractVerticle {
    @Inject
    private PythonService pythonService;

    @Override
    public void start() throws Exception {
        ZnwjModule.injectMembers(this);
        MqttServer.create(vertx).endpointHandler(pythonService::handler).listen(1883);
        MqttServer.create(vertx).endpointHandler(endpoint -> {
            switch (endpoint.clientIdentifier()) {
                case "detect": {
                    break;
                }
                default: {
                    endpoint.reject(CONNECTION_REFUSED_IDENTIFIER_REJECTED);
                    break;
                }
            }
        }).listen(1883);
    }

}
