package znwj.mock;

import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

import static com.hengyi.japp.znwj.Constant.DETECT_TOPIC;
import static com.hengyi.japp.znwj.ZnwjModule.getInstance;

/**
 * @author jzb 2019-11-09
 */
@Slf4j
@ChannelHandler.Sharable
public class MockServerHandler extends SimpleChannelInboundHandler<String> implements MqttCallback {
    final ScheduledExecutorService ses = Executors.newScheduledThreadPool(2);
    final MqttClient mqttClient;
    ScheduledFuture<?> sf1;
    ScheduledFuture<?> sf2;

    @SneakyThrows(MqttException.class)
    public MockServerHandler() {
        mqttClient = getInstance(MqttClient.class);
        final MqttConnectOptions connOpts = new MqttConnectOptions();
        connOpts.setAutomaticReconnect(true);
        connOpts.setCleanSession(true);
        mqttClient.setCallback(this);
        mqttClient.connect(connOpts);
    }

    @Override
    public void channelActive(ChannelHandlerContext ctx) throws Exception {
        sf1 = ses.scheduleWithFixedDelay(() -> mockMqtt(ctx), 2, 3, TimeUnit.SECONDS);
        sf2 = ses.scheduleWithFixedDelay(() -> mockRfid(ctx), 3, 3, TimeUnit.SECONDS);
    }

    private void mockRfid(ChannelHandlerContext ctx) {
        ctx.write("0000");
        ctx.flush();
    }

    @SneakyThrows(MqttException.class)
    private void mockMqtt(ChannelHandlerContext ctx) {
        final MqttClient client = getInstance(MqttClient.class);
        final MqttMessage message = new MqttMessage("9999".getBytes());
        client.publish(DETECT_TOPIC, message);
    }

    @Override
    public void channelRead0(ChannelHandlerContext ctx, String request) {
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        sf1.cancel(true);
        sf2.cancel(true);
        ctx.close();
    }

    @Override
    public void connectionLost(Throwable cause) {

    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {

    }

    @SneakyThrows(MqttException.class)
    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        final MqttMessage message = token.getMessage();
        log.info("message[{}] deliveryComplete", message.getId());
    }
}
