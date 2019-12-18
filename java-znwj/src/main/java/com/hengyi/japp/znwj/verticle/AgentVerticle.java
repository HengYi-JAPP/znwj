package com.hengyi.japp.znwj.verticle;

import com.github.ixtf.japp.core.J;
import com.github.ixtf.vertx.CorsConfig;
import com.github.ixtf.vertx.Jvertx;
import com.hengyi.japp.znwj.ZnwjModule;
import com.hengyi.japp.znwj.application.SilkInfoService;
import com.hengyi.japp.znwj.interfaces.rest.RestResolver;
import io.vertx.core.AbstractVerticle;
import io.vertx.core.http.HttpServerOptions;
import io.vertx.ext.healthchecks.HealthCheckHandler;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.BodyHandler;
import io.vertx.ext.web.handler.StaticHandler;
import io.vertx.ext.web.handler.sockjs.SockJSHandler;
import lombok.extern.slf4j.Slf4j;

import java.nio.file.Path;
import java.util.List;

import static com.hengyi.japp.znwj.ZnwjModule.getInstance;
import static org.apache.commons.io.FileUtils.getTempDirectoryPath;

/**
 * @author jzb 2019-10-24
 */
@Slf4j
public class AgentVerticle extends AbstractVerticle {

    @Override
    public void start() throws Exception {
        final Router router = Jvertx.router(vertx, getInstance(CorsConfig.class));
        router.route().handler(BodyHandler.create().setUploadsDirectory(getTempDirectoryPath()));
        router.route("/status").handler(HealthCheckHandler.create(vertx));

        router.route("/eventbus/*").handler(getInstance(SockJSHandler.class));
        router.get("/api/silks/:code/detectImage").handler(rc -> {
            final String code = rc.pathParam("code");
            final List<String> fileNameParam = rc.queryParam("fileName");
            if (J.isEmpty(fileNameParam)) {
                rc.response().end();
            } else {
                final String fileName = fileNameParam.get(0);
                final SilkInfoService silkInfoService = getInstance(SilkInfoService.class);
                final Path path = silkInfoService.detectDir(code).resolve(fileName);
                rc.response().sendFile(path.toString());
            }
        });

        Jvertx.resolve(RestResolver.class).forEach(it -> it.router(router, ZnwjModule::getInstance));

        router.get().handler(StaticHandler.create());
        final HttpServerOptions httpServerOptions = new HttpServerOptions()
                .setDecompressionSupported(true)
                .setCompressionSupported(true);
        vertx.createHttpServer(httpServerOptions).requestHandler(router).listen(8080);
    }

}
