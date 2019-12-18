package znwj;

import com.hengyi.japp.znwj.MainVerticle;
import io.vertx.core.AsyncResult;
import io.vertx.core.DeploymentOptions;
import io.vertx.core.Vertx;

/**
 * @author jzb 2019-11-19
 */
public class ZnwjDebug {

    private static final Vertx vertx = Vertx.vertx();

    public static void main(String[] args) {
//        System.setProperty("znwj.path", "/home/znwj");
        vertx.deployVerticle(MainVerticle.class, new DeploymentOptions(), ZnwjDebug::test);
    }

    private static void test(AsyncResult<String> stringAsyncResult) {
        if (stringAsyncResult.failed()) {
            stringAsyncResult.cause().printStackTrace();
            return;
        }
        System.out.println(stringAsyncResult.result() + " success!");

//        vertx.periodicStream(5000).fetch(2).handler(l -> {
//            final SilkInfo silkInfo = new SilkInfo();
//            silkInfo.setId(Jcodec.uuid58());
//            silkInfo.setCode(Jcodec.uuid58());
//            final DetectResult detectResult = new DetectResult();
////            detectResult.setClientIdentifier(Jcodec.uuid58());
//            detectResult.setCode(silkInfo.getCode());
//            silkInfo.add(detectResult);
//            final JsonObject message = Constant.silkInfoWebsocketMessage(silkInfo);
//            System.out.println(message.encode());
//            vertx.eventBus().publish(WEBSOCKET_GLOBAL, message);
//        });
    }
}
