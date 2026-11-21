from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
gradle = root / "app/build.gradle"

s = router.read_text()
if "automaticScanStarted" not in s:
    s = s.replace("    private String gateway;", "    private String gateway;\n    private boolean automaticScanStarted = false;")

# Preserve the existing router-page controls and add a conservative post-login detector.
pattern = r"(@Override public void onPageFinished\(WebView view, String url\) \{).*?(\n            \})"
m = re.search(pattern, s, re.S)
if not m:
    raise SystemExit("onPageFinished method not found")
method = r'''@Override public void onPageFinished(WebView view, String url) {
                view.evaluateJavascript("(function(){if(!document.getElementById('hadotaScanBtn')){var x=document.createElement('button');x.id='hadotaScanBtn';x.textContent='فحص بيانات الراوتر';x.style='position:fixed;z-index:2147483647;top:8px;right:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';x.onclick=function(){RouterBridge.scanAll()};document.body.appendChild(x)}if(!document.getElementById('hadotaReturnBtn')){var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع إلى Hadota WiFi Manager';b.style='position:fixed;z-index:2147483647;top:58px;right:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';b.onclick=function(){RouterBridge.capture()};document.body.appendChild(b)}return {login:!!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]'),text:(document.body&&document.body.innerText||'').slice(0,3000)}})()", value -> {
                    if (automaticScanStarted || router == null || value == null) return;
                    String state = value;
                    if (state.contains("\\\"login\\\":false") && state.length() > 20) {
                        automaticScanStarted = true;
                        router.postDelayed(() -> { if (router != null) new RouterBridge().scanAll(); }, 1800);
                    }
                });
            }'''
s = s[:m.start()] + method + s[m.end():]
router.write_text(s)

g = gradle.read_text()
if "versionName '1.6.5'" not in g:
    g = g.replace("versionCode 13", "versionCode 15").replace("versionName '1.6.3'", "versionName '1.6.4'")
if "versionName '1.6.4'" not in g:
    raise SystemExit("Could not set app version 1.6.4")
gradle.write_text(g)
