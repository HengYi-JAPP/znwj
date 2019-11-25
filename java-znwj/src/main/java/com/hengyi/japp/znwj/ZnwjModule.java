package com.hengyi.japp.znwj;

import com.github.ixtf.japp.core.J;
import com.github.ixtf.vertx.CorsConfig;
import com.google.inject.*;
import com.google.inject.name.Named;
import io.vertx.core.Vertx;
import io.vertx.core.json.JsonObject;
import io.vertx.ext.bridge.PermittedOptions;
import io.vertx.ext.web.handler.sockjs.BridgeOptions;
import io.vertx.ext.web.handler.sockjs.SockJSHandler;
import io.vertx.ext.web.handler.sockjs.SockJSHandlerOptions;
import lombok.SneakyThrows;

import java.io.File;
import java.nio.file.Path;
import java.util.Map;

import static com.github.ixtf.japp.core.Constant.MAPPER;
import static com.github.ixtf.japp.core.Constant.YAML_MAPPER;
import static com.hengyi.japp.znwj.Constant.WEBSOCKET_GLOBAL;
import static java.util.Optional.ofNullable;

//import org.jzb.weixin.mp.MpAccessToken;

/**
 * @author jzb 2019-10-24
 */
public class ZnwjModule extends AbstractModule {
    private static Injector INJECTOR;
    private final Vertx vertx;

    private ZnwjModule(Vertx vertx) {
        this.vertx = vertx;
    }

    synchronized public static void init(Vertx vertx) {
        if (INJECTOR == null) {
            INJECTOR = Guice.createInjector(new ZnwjModule(vertx));
        }
    }

    public static <T> T getInstance(Class<T> clazz) {
        return INJECTOR.getInstance(clazz);
    }

    public static <T> T getInstance(Key<T> key) {
        return INJECTOR.getInstance(key);
    }

    public static void injectMembers(Object o) {
        INJECTOR.injectMembers(o);
    }

    @Override
    protected void configure() {
        bind(Vertx.class).toInstance(vertx);
    }

    @Provides
    @Singleton
    @Named("rootPath")
    private Path rootPath() {
        return Path.of(System.getProperty("znwj.path", "/home/znwj"));
    }

    @SneakyThrows
    @Provides
    @Singleton
    @Named("vertxConfig")
    private JsonObject vertxConfig(@Named("rootPath") Path rootPath) {
        final File ymlFile = rootPath.resolve("config.yml").toFile();
        if (ymlFile.exists()) {
            final Map map = YAML_MAPPER.readValue(ymlFile, Map.class);
            return new JsonObject(map);
        }
        final File jsonFile = rootPath.resolve("config.json").toFile();
        final Map map = MAPPER.readValue(jsonFile, Map.class);
        return new JsonObject(map);
    }

    @Provides
    @Singleton
    @Named("plcConfig")
    private JsonObject plcConfig(@Named("vertxConfig") JsonObject vertxConfig) {
        return vertxConfig.getJsonObject("plc", new JsonObject());
    }

    @Provides
    @Singleton
    @Named("cameraConfig")
    private JsonObject cameraConfig(@Named("vertxConfig") JsonObject vertxConfig) {
        return vertxConfig.getJsonObject("camera", new JsonObject());
    }

    @Provides
    @Singleton
    @Named("detectConfig")
    private JsonObject detectConfig(@Named("vertxConfig") JsonObject vertxConfig) {
        return vertxConfig.getJsonObject("detect", new JsonObject());
    }

    @Provides
    @Singleton
    @Named("silkCacheSpec")
    private String silkCacheSpec(@Named("vertxConfig") JsonObject vertxConfig) {
        return vertxConfig.getString("silkCacheSpec", "maximumSize=100");
    }

    @Provides
    @Singleton
    @Named("dbPath")
    private Path dbPath(@Named("vertxConfig") JsonObject vertxConfig, @Named("rootPath") Path rootPath) {
        return ofNullable(vertxConfig.getString("dbPath"))
                .filter(J::nonBlank)
                .map(Path::of)
                .orElseGet(() -> rootPath.resolve("db"));
    }

    @Provides
    @Singleton
    private CorsConfig CorsConfig(@Named("vertxConfig") JsonObject vertxConfig) {
        final JsonObject cors = vertxConfig.getJsonObject("cors", new JsonObject());
        return MAPPER.convertValue(cors.getMap(), CorsConfig.class);
    }

    @Provides
    private SockJSHandler SockJSHandler() {
        final SockJSHandlerOptions options = new SockJSHandlerOptions();
        final PermittedOptions outboundPermitted = new PermittedOptions().setAddress(WEBSOCKET_GLOBAL);
        final BridgeOptions bo = new BridgeOptions().addOutboundPermitted(outboundPermitted);
        final SockJSHandler sockJSHandler = SockJSHandler.create(vertx, options);
        sockJSHandler.bridge(bo, be -> {
            be.complete(true);
        });
        return sockJSHandler;
    }
}
