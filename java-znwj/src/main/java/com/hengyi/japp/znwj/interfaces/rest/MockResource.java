package com.hengyi.japp.znwj.interfaces.rest;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.hengyi.japp.znwj.application.BackendService;
import io.vertx.core.TimeoutStream;
import io.vertx.core.Vertx;

import javax.ws.rs.*;
import java.security.SecureRandom;

import static javax.ws.rs.core.MediaType.APPLICATION_JSON;

/**
 * @author jzb 2019-11-20
 */
@Singleton
@Path("mock")
@Produces(APPLICATION_JSON)
public class MockResource {
    private static final SecureRandom random = new SecureRandom();
    private static TimeoutStream timeoutStream;
    private final Vertx vertx;
    private final BackendService backendService;

    @Inject
    private MockResource(Vertx vertx, BackendService backendService) {
        this.vertx = vertx;
        this.backendService = backendService;
    }

    public void mockOne() {
        final int rfidNum = random.nextInt();
//        backendService.handleRfid(rfidNum).subscribe();
    }

    @GET
    public void start(@QueryParam("delay") @DefaultValue("5000") long delay) {
        if (timeoutStream != null) {
            timeoutStream.cancel();
        }
        timeoutStream = vertx.periodicStream(delay).handler(l -> mockOne());
    }

    @DELETE
    public void pause() {
        if (timeoutStream != null) {
            timeoutStream.cancel();
        }
    }

    @Path("one")
    @GET
    public void publishSilkInfo() {
        mockOne();
    }

}
