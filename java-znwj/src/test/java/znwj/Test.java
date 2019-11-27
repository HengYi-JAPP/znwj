package znwj;

import com.github.ixtf.japp.codec.Jcodec;
import io.vertx.core.buffer.Buffer;
import lombok.SneakyThrows;
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

/**
 * @author jzb 2019-11-19
 */
public class Test {

    @SneakyThrows
    public static void main(String[] args) {
        String topic = "/znwj/detect";
        String content = Jcodec.uuid58();
        int qos = 2;
//        String broker = "tcp://test.mosquitto.org:1883";
        String broker = "tcp://192.168.0.94:1883";
        String clientId = "JavaSample";
        MemoryPersistence persistence = new MemoryPersistence();

        try {
            MqttClient sampleClient = new MqttClient(broker, clientId, persistence);
            MqttConnectOptions connOpts = new MqttConnectOptions();
            connOpts.setAutomaticReconnect(true);
            connOpts.setCleanSession(true);

            sampleClient.setCallback(new MqttCallback() {
                @Override
                public void connectionLost(Throwable cause) {

                }

                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    System.out.println(topic + " " + Buffer.buffer(message.getPayload()).toString());
                }

                @Override
                public void deliveryComplete(IMqttDeliveryToken token) {

                }
            });

            sampleClient.connect(connOpts);

            sampleClient.subscribe("/znwj/detect/result", 1);


            MqttMessage message = new MqttMessage(content.getBytes());
            message.setQos(qos);
            sampleClient.publish(topic, message);
//            sampleClient.disconnect();
//            System.out.println("Disconnected");
//            System.exit(0);
            System.in.read();
        } catch (MqttException me) {
            System.out.println("reason " + me.getReasonCode());
            System.out.println("msg " + me.getMessage());
            System.out.println("loc " + me.getLocalizedMessage());
            System.out.println("cause " + me.getCause());
            System.out.println("excep " + me);
            me.printStackTrace();
        }
    }

}
