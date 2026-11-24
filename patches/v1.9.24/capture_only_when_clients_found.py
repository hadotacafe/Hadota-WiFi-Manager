from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

start = s.index("        @JavascriptInterface public void capture() {")
end = s.index("\n    }\n\n    @Override public void onBackPressed()", start)
replacement = r"""        @JavascriptInterface public void capture() {
            runOnUiThread(() -> {
                if (router == null) return;
                String js = "(function(){"
                    + "var clean=function(v){return String(v||'').replace(/\\s+/g,' ').trim()},out=[],seen={};"
                    + "var ipRx=/(?:^|[^0-9])((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.\\d{1,3}\\.\\d{1,3})(?:$|[^0-9])/;"
                    + "var macRx=/\\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\\b/i;"
                    + "var source=/lan/i.test(location.href+' '+document.title)?'LAN':'WLAN';"
                    + "document.querySelectorAll('table tr').forEach(function(row){var cells=Array.from(row.querySelectorAll('th,td')).map(function(c){return clean(c.innerText||c.textContent)});var line=cells.join(' | '),im=line.match(ipRx);if(!im)return;"
                    + "var mm=line.match(macRx),ip=im[1],mac=mm?mm[1].replace(/-/g,':').toLowerCase():'';var key=mac||ip;if(seen[key])return;seen[key]=1;"
                    + "var name=cells.find(function(v){return v&&v!==ip&&!macRx.test(v)&&!/^(online|connected|active|wlan|lan|yes|no|ip address|mac address|host name|device name)$/i.test(v)})||'جهاز متصل';"
                    + "out.push({name:name,ip:ip,mac:mac,source:source,group:'unassigned'});});"
                    + "return JSON.stringify({url:location.href,title:document.title,text:document.body?document.body.innerText:'',devices:out});"
                    + "})()";
                router.evaluateJavascript(js, value -> {
                    if (router == null) return;
                    try {
                        String payload = new org.json.JSONArray("[" + (value == null ? "null" : value) + "]").optString(0, "{}");
                        org.json.JSONObject page = new org.json.JSONObject(payload);
                        org.json.JSONArray devices = page.optJSONArray("devices");
                        if (devices == null || devices.length() == 0) {
                            String note = "لم يتم العثور على أجهزة في الصفحة الحالية. افتح WLAN Client Status أو LAN Client Status من قائمة الراوتر، ثم اضغط «رجوع إلى Hadota» بعد ظهور قائمة الأجهزة.";
                            router.evaluateJavascript("(function(){var n=document.getElementById('hadotaScanHint');if(!n){n=document.createElement('div');n.id='hadotaScanHint';n.style='position:fixed;z-index:2147483647;top:112px;right:8px;left:8px;padding:14px;background:#152536;color:#f4dfad;border:2px solid #d9b36a;border-radius:12px;font:bold 15px sans-serif;line-height:1.7;direction:rtl';document.body.appendChild(n)}n.textContent=" + org.json.JSONObject.quote(note) + ";return true})()", null);
                            return;
                        }
                        Intent result = new Intent();
                        result.putExtra("router_text", page.optString("text", ""));
                        result.putExtra("router_devices", devices.toString());
                        result.putExtra("router_report", payload);
                        setResult(RESULT_OK, result);
                        finish();
                    } catch (Exception e) {
                        android.widget.Toast.makeText(RouterActivity.this, "تعذر قراءة قائمة الأجهزة من الصفحة الحالية.", android.widget.Toast.LENGTH_LONG).show();
                    }
                });
            });
        }"""
s = s[:start] + replacement + s[end:]
router.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\\s+\\d+", "versionCode 59", g, count=1)
g, b = re.subn(r"versionName\\s+'[^']+'", "versionName '1.9.24'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Could not update app version to 1.9.24")
gradle.write_text(g, encoding="utf-8")
print("v1.9.24: capture/return extracts live clients from current router page and refuses empty return")
