package com.hengyi.japp.znwj;

import com.hengyi.japp.znwj.application.internal.BackendStatus;
import com.hengyi.japp.znwj.domain.SilkInfo;
import io.vertx.core.json.JsonObject;

/**
 * @author jzb 2019-11-20
 */
public class Constant {
    public static final String SILK_INFO_YML = "SilkInfo.yml";
    public static final String ORIGINAL_DIR = "original";
    public static final String DETECT_DIR = "detect";

    public static final String DETECT_TOPIC = "/znwj/detect";
    public static final String DETECT_RESULT_TOPIC = "/znwj/detect/result";

    public static final String WEBSOCKET_GLOBAL = "znwj://websocket/global";

    public static JsonObject silkInfoWebsocketMessage(SilkInfo silkInfo) {
        return new JsonObject()
                .put("type", "SilkInfoUpdate")
                .put("data", JsonObject.mapFrom(silkInfo));
    }

    public static JsonObject backendInfoWebsocketMessage(BackendStatus status) {
        return new JsonObject()
                .put("type", "BackendInfoUpdate")
                .put("data", status.toMap());
    }
}
