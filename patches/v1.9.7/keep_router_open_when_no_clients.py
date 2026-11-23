from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
old="""            final String capturedPayload = payload;
            org.json.JSONArray devices = parseRouterClients(capturedPayload);
            web.removeJavascriptInterface("AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(capturedPayload) + ")", null);
                }
            }, 500);"""
new="""            final String capturedPayload = payload;
            org.json.JSONArray devices = parseRouterClients(capturedPayload);
            if (devices.length() == 0) {
                // Keep the authenticated router page open when the current page is not a client list.
                // The user can navigate to WLAN Client Status / LAN Client Status and retry without
                // losing the router session or being thrown back to the app home screen.
                runOnUiThread(() -> {
                    try {
                        android.widget.Toast.makeText(MainActivity.this,
                            "لم أجد أجهزة في الصفحة الحالية. افتح WLAN Client Status أو LAN Client Status ثم اضغط استيراد الأجهزة.",
                            android.widget.Toast.LENGTH_LONG).show();
                    } catch (Throwable ignored) {}
                });
                return;
            }
            web.removeJavascriptInterface("AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(capturedPayload) + ")", null);
                }
            }, 500);"""
if old not in s: raise SystemExit("capture result callback block not found")
s=s.replace(old,new,1)
# Also make the classify action resilient to WebView script scope and dynamic button rendering.
html=root/"app/src/main/assets/index.html"
h=html.read_text(encoding="utf-8")
if "window.classifyImportedAsStaff = function()" not in h:
    h=h.replace("function classifyImportedAsStaff(){","window.classifyImportedAsStaff = function(){",1)
    end=""" $('classifyImportedBtn').style.display='none';
}"""
    if end not in h: raise SystemExit("classify function terminator not found")
    h=h.replace(end,""" $('classifyImportedBtn').style.display='none';
};""",1)
# Use delegated click handling so button works even if it is revealed after import.
h=h.replace('onclick="classifyImportedAsStaff()"','')
delegated="""document.addEventListener('click',function(ev){var target=ev.target&&ev.target.closest?ev.target.closest('#classifyImportedBtn'):null;if(target){ev.preventDefault();try{window.classifyImportedAsStaff();}catch(err){alert('تعذر تصنيف الأجهزة: '+(err&&err.message?err.message:err));}}},true);"""
if "closest('#classifyImportedBtn')" not in h:
    marker="window.classifyImportedAsStaff = function(){"
    if marker not in h: raise SystemExit("global classification handler missing")
    # Insert delegation after the function body by placing it at the end of the script body.
    idx=h.rfind("</script>")
    if idx<0: raise SystemExit("script closing tag missing")
    h=h[:idx]+delegated+"\n"+h[idx:]
main.write_text(s,encoding="utf-8")
html.write_text(h,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 42",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.7'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.7: preserve router session on empty extraction; delegated classification button click")
