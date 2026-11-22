from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text(encoding="utf-8")
pattern = r'            @Override public void onPageFinished\(WebView view, String url\) \{.*?\n            \}\n            @Override public void onReceivedSslError'
replacement = """            @Override public void onPageFinished(WebView view, String url) {
                String host = "";
                try { host = android.net.Uri.parse(url).getHost(); } catch (Exception ignored) {}
                if (host != null && host.equalsIgnoreCase(getGatewayAddress())) {
                    Runnable inject = () -> {
                        if (web != view) return;
                        String js = "(function(){try{if(!document.body)return false;"
                          + "var b=document.getElementById('hadotaCaptureBtn');"
                          + "if(!b){b=document.createElement('button');b.id='hadotaCaptureBtn';"
                          + "b.textContent='استيراد الأجهزة';"
                          + "b.setAttribute('style','position:fixed!important;top:10px!important;left:10px!important;z-index:2147483647!important;padding:14px 16px!important;background:#d9b36a!important;color:#17120a!important;border:3px solid #fff!important;border-radius:12px!important;font-weight:bold!important;font-size:16px!important;display:block!important;visibility:visible!important;opacity:1!important;box-shadow:0 2px 12px #000!important');"
                          + "b.onclick=function(){location.href='hadota://capture'};document.body.appendChild(b)}"
                          + "return true}catch(e){return false}})()";
                        view.evaluateJavascript(js, null);
                    };
                    view.postDelayed(inject, 250);
                    view.postDelayed(inject, 900);
                    view.postDelayed(inject, 1800);
                    view.postDelayed(inject, 3500);
                }
            }
            @Override public void onReceivedSslError"""
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("MainActivity onPageFinished block not found exactly once")
main.write_text(s2, encoding="utf-8")

# Also expose the same import action in the dedicated RouterActivity WebView.
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
r = router.read_text(encoding="utf-8")
old = "if(!document.getElementById('hadotaReturnBtn')){var b=document.createElement('button');"
new = "if(!document.getElementById('hadotaImportBtn')){var z=document.createElement('button');z.id='hadotaImportBtn';z.textContent='استيراد الأجهزة';z.style='position:fixed;z-index:2147483647;top:108px;right:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';z.onclick=function(){RouterBridge.capture()};document.body.appendChild(z)}if(!document.getElementById('hadotaReturnBtn')){var b=document.createElement('button');"
if old not in r:
    raise SystemExit("RouterActivity injection anchor not found")
r = r.replace(old, new, 1)
router.write_text(r, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g = re.sub(r"versionCode\\s+\\d+", "versionCode 29", g, count=1)
g = re.sub(r"versionName\\s+'[^']+'", "versionName '1.7.9'", g, count=1)
gradle.write_text(g, encoding="utf-8")
print("Patched MainActivity retries + RouterActivity import action; version 1.7.9")
