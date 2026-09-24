import java.io.File;
import java.net.URI;
import java.security.KeyStore;
import javax.net.ssl.HttpsURLConnection;
/** Public CA store only; TLS validation stays enabled. No credentials. */
public class TrustStoreProbe {
    public static void main(String[] args) throws Exception {
        String path=System.getProperty("javax.net.ssl.trustStore");
        if(path==null) throw new IllegalStateException("Explicit mounted CA store missing");
        KeyStore store=KeyStore.getInstance(new File(path),"changeit".toCharArray());
        if(store.size()==0) throw new IllegalStateException("Empty trusted CA store");
        HttpsURLConnection connection=(HttpsURLConnection)URI.create("https://services.gradle.org/distributions/gradle-8.7-all.zip").toURL().openConnection();
        connection.setRequestMethod("HEAD");connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(30000);connection.setReadTimeout(30000);
        int code=connection.getResponseCode();connection.disconnect();
        if(code<200 || code>=400) throw new IllegalStateException("Gradle TLS preflight HTTP "+code);
        System.out.println("{\"java_ca_entries\":"+store.size()+",\"gradle_tls_http_status\":"+code+",\"certificate_validation_enabled\":true}");
    }
}
