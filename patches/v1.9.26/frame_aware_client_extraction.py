from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

# Router UI is frame-based on this ZTE firmware. Read the authenticated child
# frames as well as the top document during the automatic, read-only scan.
old = 'inspect(location.href,document.documentElement?.outerHTML||\'\',200);'
new = """const docs=[document],frameSeen=new Set();
(function walk(w){
 try{
  for(let i=0;i<w.frames.length;i++){
   const f=w.frames[i]; if(frameSeen.has(f))continue; frameSeen.add(f);
   try{const d=f.document;if(d&&d.documentElement){docs.push(d);walk(f)}}catch(e){}
  }
 }catch(e){}
})(window);
docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});
"""
if old not in s:
    raise SystemExit("scanAll top-document inspect anchor missing")
s = s.replace(old, new, 1)

# Replace the narrow capture routine with a frame-aware extractor. It collects
# client rows from nested frames, then falls back to IP/MAC pairs in rendered
# text. It still only reads pages and never submits router settings.
start = s.index("        @JavascriptInterface public void capture() {")
end = s.index("\n        }\n    }\n\n    @Override public void onBackPressed()", start) + len("\n        }")
capture = r'''        @JavascriptInterface public void capture() {
            runOnUiThread(() -> {
                if (router == null) return;
                String js = "(function(){"
                    + "var docs=[document],seenFrames=[];function walk(w){try{for(var i=0;i<w.frames.length;i++){var f=w.frames[i];if(seenFrames.indexOf(f)>=0)continue;seenFrames.push(f);try{if(f.document&&f.document.documentElement){docs.push(f.document);walk(f)}}catch(e){}}}catch(e){}}walk(window);"
                    + "var out=[],seen={},ipRx=/\\b((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.\\d{1,3}\\.\\d{1,3})\\b/g,macRx=/\\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\\b/i;"
                    + "function clean(v){return String(v||'').replace(/\\s+/g,' ').trim()}"
                    + "function add(vals,href,title){var line=vals.map(clean).filter(Boolean).join(' | '),im=line.match(ipRx);if(!im)return;var ip=im[1],mm=line.match(macRx),mac=mm?mm[1].replace(/-/g,':').toLowerCase():'';var key=mac||ip;if(seen[key])return;seen[key]=1;var name=vals.map(clean).find(function(v){return v&&v!==ip&&!macRx.test(v)&&!/^(ssid[0-9]*|ipv[46] address|ip address|mac address|online|connected|active|wlan|lan|yes|no|name|client)$/i.test(v)})||'جهاز متصل';out.push({name:name,ip:ip,mac:mac,source:/lan/i.test(href+' '+title)?'LAN':'WLAN',group:'unassigned'});}"
                    + "docs.forEach(function(d){try{var href=d.location?d.location.href:location.href,title=d.title||'';"
                    + "d.querySelectorAll('table tr').forEach(function(r){var c=Array.from(r.querySelectorAll('th,td')).map(function(x){return clean(x.innerText||x.textContent)});if(c.length)add(c,href,title)});"
                    + "var body=clean(d.body?d.body.innerText:'');var lines=(d.body?d.body.innerText:'').split(/\\n+/).map(clean).filter(Boolean);"
                    + "lines.forEach(function(line,i){if(ipRx.test(line)){ipRx.lastIndex=0;add(lines.slice(Math.max(0,i-2),Math.min(lines.length,i+3)),href,title)}else ipRx.lastIndex=0});"
                    + "}catch(e){}});"
                    + "return JSON.stringify({url:location.href,title:document.title,text:docs.map(function(d){try{return d.body?d.body.innerText:''}catch(e){return ''}}).join('\\n'),frameCount:docs.length,devices:out});"
                    + "})()";
                router.evaluateJavascript(js, value -> {
                    if (router == null) return;
                    try {
                        String payload = new org.json.JSONArray("[" + (value == null ? "null" : value) + "]").optString(0, "{}");
                        org.json.JSONObject page = new org.json.JSONObject(payload);
                        org.json.JSONArray devices = page.optJSONArray("devices");
                        if (devices == null) devices = new org.json.JSONArray();
                        Intent result = new Intent();
                        result.putExtra("router_text", page.optString("text", ""));
                        result.putExtra("router_devices", devices.toString());
                        result.putExtra("router_report", payload);
                        setResult(RESULT_OK, result);
                        if (devices.length() == 0) {
                            android.widget.Toast.makeText(RouterActivity.this,
                                "رجعنا للتطبيق. لم تُستخرج أجهزة؛ تم فحص " + page.optInt("frameCount", 1) + " إطارًا من صفحة الراوتر.",
                                android.widget.Toast.LENGTH_LONG).show();
                        }
                        finish();
                    } catch (Exception e) {
                        android.widget.Toast.makeText(RouterActivity.this, "تعذر قراءة قائمة الأجهزة من الصفحة الحالية.", android.widget.Toast.LENGTH_LONG).show();
                    }
                });
            });
        }'''
s = s[:start] + capture + s[end:]

router.write_text(s, encoding="utf-8")
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\s+\d+", "versionCode 61", g, count=1)
g, b = re.subn(r"versionName\s+'[^']+'", "versionName '1.9.26'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Could not update version to 1.9.26")
gradle.write_text(g, encoding="utf-8")
print("v1.9.26: scan and capture inspect same-origin ZTE child frames and extract client rows/IP-MAC pairs")
