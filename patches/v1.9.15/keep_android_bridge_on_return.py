from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
old="""            web.removeJavascriptInterface("AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(capturedPayload) + ")", null);
                }
            }, 500);"""
new="""            // Keep the native bridge installed BEFORE loading the local page.
            // addJavascriptInterface after loadUrl is not visible until the next navigation.
            web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(capturedPayload) + ")", null);
                }
            }, 500);"""
if old not in s: raise SystemExit("capture return bridge sequence not found")
s=s.replace(old,new,1)
# Also ensure the bridge exists on any fresh WebView recreation before its first navigation.
needle='''        web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
        mainFrame = new FrameLayout(this);'''
if needle not in s: raise SystemExit("initial bridge install not found")
# Existing initial installation is correct; verify it remains before loadUrl.
if s.index('web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");') > s.index('web.loadUrl("file:///android_asset/index.html");'):
    raise SystemExit("initial bridge installation ordering invalid")
main.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 50",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.15'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
# Static proof: no bridge removal remains, and bridge install precedes the local home reload.
if 'removeJavascriptInterface("AndroidBridge")' in s: raise SystemExit("bridge removal still present")
idx=s.index('// Keep the native bridge installed BEFORE loading the local page.')
if s.index('web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");',idx) > s.index('web.loadUrl("file:///android_asset/index.html");',idx):
    raise SystemExit("return bridge sequence ordering invalid")
print("v1.9.15: retain/reinstall AndroidBridge before loading home page; removes cause of AndroidBridge unavailable after import")
