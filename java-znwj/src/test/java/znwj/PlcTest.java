package znwj;

import lombok.SneakyThrows;

import java.io.DataInputStream;
import java.net.Socket;

/**
 * @author jzb 2019-11-19
 */
public class PlcTest {

    @SneakyThrows
    public static void main(String[] args) {
//        final Socket socket = new Socket("192.168.30.20", 7000);
        // ridf
        final Socket socket = new Socket("192.168.30.168", 2111);
//        final Socket socket = new Socket("172.16.1.27", 2111);

//        final BufferedReader socketReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
//        String line = null;
//        while ((line = socketReader.readLine()) != null) {
//            System.out.println(line);
//        }

        final DataInputStream socketReader = new DataInputStream(socket.getInputStream());
        byte[] bytes = new byte[1024];
        int len;
        while ((len = socketReader.read(bytes)) != -1) {
//        注意指定编码格式，发送方和接收方一定要统一，建议使用UTF-8
            System.out.println(len);

//            final ByteBuffer wrap = ByteBuffer.wrap(bytes);
//            System.out.println(wrap.getInt());
            final String str = new String(bytes, 0, len);
            System.out.println("get message from server: " + str);
//            final String hex = bytesToHex(bytes);
//            System.out.println("get message from server: " + hex);
        }
    }

    private static String bytesToHex(byte[] hashInBytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : hashInBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

}
