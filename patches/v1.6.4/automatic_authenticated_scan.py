from pathlib import Path
import json

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
gradle = root / "app/build.gradle"

s = router.read_text()
if "private boolean automaticScanStarted" not in s:
    s = s.replace("    private String gateway;\n", "    private String gateway;\n    private boolean automaticScanStarted = false;\n")
old = """            @Override public void onPageFinished(WebView view, String url) {
                view.evaluateJavascript("(function(){if(document.getElementById('hadotaScanBtn'))return;function b(id,t,y,fn){var x=document.createElement('button');x.id=id;x.textContent=t;x.style='position:fixed;z-index:2147483647;top:'+y+'px;left:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';x.onclick=fn;document.body.appendChild(x)}b('hadotaScanBtn','فحص بيانات الراوتر',8,function(){RouterBridge.scanAll()});b('hadotaReturnBtn','رجوع للتطبيق',58,function(){RouterBridge.capture()})})();", null);
            }"""
new = """            @Override public void onPageFinished(WebView view, String url) {
                view.evaluateJavascript("(function(){if(!document.getElementById('hadotaReturnBtn')){var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع إلى Hadota WiFi Manager';b.style='position:fixed;z-index:2147483647;top:8px;left:8px;padding:13px 16px;background:#d9b36a;color:#17120a;border:2px solid #fff;border-radius:12px;font-weight:bold';b.onclick=function(){RouterBridge.capture()};document.body.appendChild(b)}return {passwordField:!!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]'),bodyLength:(document.body&&document.body.innerText||'').length,url:location.href}})()", value -> {
                    if (automaticScanStarted || router == null || value == null) return;
                    String state = value;
                    if (state.contains("\\"passwordField\\":false") && state.contains("\\"bodyLength\\":") && !state.contains("\\"bodyLength\\":0")) {
                        automaticScanStarted = true;
                        router.postDelayed(() -> { if (router != null) new RouterBridge().scanAll(); }, 1200);
                    }
                });
            }"""
if old not in s:
    raise SystemExit("Expected v1.6.3 onPageFinished block not found")
s = s.replace(old, new)
router.write_text(s)

g = gradle.read_text()
g = g.replace("versionCode 13", "versionCode 14").replace("versionName '1.6.3'", "versionName '1.6.4'")
if "versionName '1.6.4'" not in g:
    raise SystemExit("Could not bump app version to 1.6.4")
gradle.write_text(g)
