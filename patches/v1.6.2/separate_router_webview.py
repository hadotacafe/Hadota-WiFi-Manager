from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text()

# Keep the main dashboard WebView on its local HTML page at all times.
s = s.replace("import android.app.Activity;", "import android.app.Activity;\nimport android.content.Intent;")
old = '''    private void openRouterPanel() {
        runOnUiThread(() -> {
            if (web != null) {
                
                web.loadUrl("https://" + getGatewayAddress() + "/");
            }
        });
    }'''
new = '''    private void openRouterPanel() {
        runOnUiThread(() -> {
            Intent intent = new Intent(MainActivity.this, RouterActivity.class);
            intent.putExtra("gateway", getGatewayAddress());
            startActivityForResult(intent, 6201);
        });
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 6201 && resultCode == RESULT_OK && data != null && web != null) {
            String text = data.getStringExtra("router_text");
            org.json.JSONArray devices = parseRouterClients(text == null ? "" : text);
            web.evaluateJavascript("showLiveDevices(" + devices.toString() + ")", null);
        }
    }'''
if old not in s:
    raise SystemExit("openRouterPanel block not found; aborting")
s = s.replace(old, new)
main.write_text(s)

router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
router.write_text(r'''package com.hadota.wifimanager;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.content.Intent;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import android.webkit.JavascriptInterface;
import android.webkit.SslErrorHandler;
import android.net.http.SslError;
import android.view.ViewGroup;

public class RouterActivity extends Activity {
    private WebView router;
    private String gateway;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(11,16,23));
        getWindow().setNavigationBarColor(Color.rgb(11,16,23));
        gateway = getIntent().getStringExtra("gateway");
        if (gateway == null || gateway.isEmpty()) gateway = "192.168.1.1";
        router = new WebView(this);
        router.setBackgroundColor(Color.WHITE);
        WebSettings settings = router.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        router.addJavascriptInterface(new RouterBridge(), "RouterBridge");
        router.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                view.evaluateJavascript("(function(){if(document.getElementById('hadotaReturnBtn'))return;var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع إلى Hadota WiFi Manager';b.style='position:fixed;z-index:2147483647;top:8px;left:8px;padding:13px 16px;background:#d9b36a;color:#17120a;border:2px solid #fff;border-radius:12px;font-weight:bold;font-size:16px;box-shadow:0 2px 12px #000';b.onclick=function(){RouterBridge.capture()};document.body.appendChild(b);})();", null);
            }
            @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                String host = error.getUrl() == null ? "" : android.net.Uri.parse(error.getUrl()).getHost();
                if (host != null && host.equalsIgnoreCase(gateway)) handler.proceed(); else handler.cancel();
            }
            @Override public boolean onRenderProcessGone(WebView view, android.webkit.RenderProcessGoneDetail detail) {
                if (router == view) {
                    ViewGroup parent = (ViewGroup) view.getParent();
                    if (parent != null) parent.removeView(view);
                    view.destroy();
                    router = null;
                    setResult(RESULT_CANCELED);
                    finish();
                }
                return true;
            }
        });
        setContentView(router);
        router.loadUrl("http://" + gateway + "/");
    }

    private class RouterBridge {
        @JavascriptInterface public void capture() {
            runOnUiThread(() -> {
                if (router == null) return;
                router.evaluateJavascript("(function(){return document.body?document.body.innerText:''})()", value -> {
                    String text = value == null ? "" : value;
                    try { text = new org.json.JSONArray("[" + text + "]").optString(0, ""); } catch (Exception ignored) {}
                    Intent result = new Intent();
                    result.putExtra("router_text", text);
                    setResult(RESULT_OK, result);
                    finish();
                });
            });
        }
    }

    @Override public void onBackPressed() {
        if (router != null && router.canGoBack()) router.goBack();
        else { setResult(RESULT_CANCELED); finish(); }
    }

    @Override protected void onDestroy() {
        if (router != null) { router.stopLoading(); router.destroy(); router = null; }
        super.onDestroy();
    }
}
''')

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
needle = '<activity android:name=".MainActivity" android:exported="true">'
if needle not in m: raise SystemExit("MainActivity manifest entry not found")
m = m.replace(needle, '<activity android:name=".RouterActivity" android:exported="false" />\n        ' + needle)
manifest.write_text(m)

gradle = root / "app/build.gradle"
g = gradle.read_text()
g = g.replace("versionCode 11", "versionCode 12").replace("versionName '1.6.1'", "versionName '1.6.2'")
gradle.write_text(g)
