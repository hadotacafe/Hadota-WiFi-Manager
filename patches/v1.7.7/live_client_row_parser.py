from pathlib import Path
import re
root = Path('source/Hadota-WiFi-Manager-Android')
main = root / 'app/src/main/java/com/hadota/wifimanager/MainActivity.java'
s = main.read_text(encoding='utf-8')
start = s.index('    private void captureRouterPage() {')
end = s.index('    private void flushRouterBlock(', start)
replacement = r'''    private void captureRouterPage() {
        if (web == null) return;
        // Read the authenticated page DOM only. Extract each table row as a separate client.
        String js = "(function(){"
          + "var clean=function(x){return (x||'').replace(/\\s+/g,' ').trim()};"
          + "var ipRx=/(?:^|[^0-9])((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.\\d{1,3}\\.\\d{1,3})(?:$|[^0-9])/;"
          + "var macRx=/\\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\\b/i;"
          + "var devices=[],seen={};"
          + "var source=(/lan/i.test(location.href+' '+document.title)?'LAN':'WLAN');"
          + "var add=function(cells,headers){var vals=cells.map(clean),joined=vals.join(' | '),im=joined.match(ipRx),mm=joined.match(macRx);if(!im)return;"
          + "var name='جهاز متصل';for(var i=0;i<vals.length;i++){var h=clean(headers[i]||'').toLowerCase();if(/host|device|client.?name|hostname|اسم|جهاز/.test(h)&&vals[i]&&!ipRx.test(vals[i])&&!macRx.test(vals[i])){name=vals[i];break}}"
          + "if(name==='جهاز متصل'){for(var j=0;j<vals.length;j++){if(vals[j]&&!ipRx.test(vals[j])&&!macRx.test(vals[j])&&!/^(online|connected|active|wlan|lan|yes|no)$/i.test(vals[j])&&!/^(ip address|mac address|host name|device name)$/i.test(vals[j])){name=vals[j];break}}}"
          + "var ip=im[1],mac=mm?mm[1].replace(/-/g,':').toLowerCase():'';var key=mac||ip;if(!seen[key]){seen[key]=1;devices.push({name:name,ip:ip,mac:mac,source:source,group:'unassigned'})}};"
          + "Array.from(document.querySelectorAll('table')).forEach(function(t){var trs=Array.from(t.querySelectorAll('tr'));if(!trs.length)return;"
          + "var first=Array.from(trs[0].querySelectorAll('th,td')).map(function(c){return clean(c.innerText)});"
          + "var hh=trs[0].querySelectorAll('th').length>0||first.some(function(x){return /ip address|mac address|host.?name|device.?name|client/i.test(x)});var headers=hh?first:[];"
          + "for(var n=hh?1:0;n<trs.length;n++){var cells=Array.from(trs[n].querySelectorAll('th,td')).map(function(c){return clean(c.innerText)});if(cells.length)add(cells,headers)}});"
          + "if(!devices.length){Array.from(document.querySelectorAll('tr')).forEach(function(r){var cells=Array.from(r.querySelectorAll('th,td')).map(function(c){return clean(c.innerText)});if(cells.length)add(cells,[])})}"
          + "var rows=Array.from(document.querySelectorAll('tr')).map(function(r){return Array.from(r.querySelectorAll('th,td')).map(function(c){return clean(c.innerText)})}).filter(function(r){return r.length});"
          + "var tables=Array.from(document.querySelectorAll('table')).map(function(t){return clean(t.innerText)});"
          + "return JSON.stringify({url:location.href,title:document.title,text:document.body?document.body.innerText:'',tables:tables,rows:rows,devices:devices})})()";
        web.evaluateJavascript(js, value -> {
            String payload = "";
            try { payload = new org.json.JSONArray("[" + (value == null ? "null" : value) + "]").optString(0, ""); }
            catch(Exception ignored) { }
            final String capturedPayload = payload;
            org.json.JSONArray devices = parseRouterClients(capturedPayload);
            web.removeJavascriptInterface("AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(capturedPayload) + ")", null);
                }
            }, 500);
        });
    }

    private org.json.JSONArray parseRouterClients(String payload) {
        org.json.JSONArray out = new org.json.JSONArray();
        java.util.HashSet<String> seen = new java.util.HashSet<>();
        try {
            org.json.JSONObject root = new org.json.JSONObject(payload);
            String pageText = root.optString("text", "");
            String pageUrl = root.optString("url", "").toLowerCase(java.util.Locale.ROOT);
            String source = (pageUrl.contains("lan") || pageText.toLowerCase(java.util.Locale.ROOT).contains("lan client status")) ? "LAN" : "WLAN";
            org.json.JSONArray extracted = root.optJSONArray("devices");
            if (extracted != null) {
                for (int i = 0; i < extracted.length(); i++) {
                    org.json.JSONObject d = extracted.optJSONObject(i);
                    if (d == null) continue;
                    addRouterDevice(out, seen, d.optString("name", "جهاز متصل"), d.optString("ip", ""), d.optString("mac", ""), d.optString("source", source));
                }
            }
            // Firmware fallback: parse complete device rows separately instead of merging the whole page.
            if (out.length() == 0) {
                org.json.JSONArray rows = root.optJSONArray("rows");
                if (rows != null) {
                    StringBuilder pending = new StringBuilder();
                    String currentName = "جهاز متصل";
                    for (int i = 0; i < rows.length(); i++) {
                        org.json.JSONArray row = rows.optJSONArray(i);
                        if (row == null) continue;
                        StringBuilder line = new StringBuilder();
                        for (int j = 0; j < row.length(); j++) {
                            String cell = row.optString(j, "").trim();
                            if (!cell.isEmpty()) { if (line.length() > 0) line.append(" | "); line.append(cell); }
                        }
                        String value = line.toString();
                        if (value.isEmpty()) continue;
                        if (value.matches("(?is).*client\\s*[-#:]?\\s*\\d+.*")) {
                            flushRouterBlock(out, seen, pending.toString(), source, currentName);
                            pending.setLength(0);
                            currentName = value.replaceAll("(?is).*?(client\\s*[-#:]?\\s*\\d+).*", "$1");
                        }
                        if (value.matches("(?is).*?(?:192\\.168|10\\.|172\\.(?:1[6-9]|2[0-9]|3[01])\\.).*")) {
                            flushRouterBlock(out, seen, pending.toString(), source, currentName);
                            pending.setLength(0);
                            flushRouterBlock(out, seen, value, source, currentName);
                        } else pending.append(value).append('\\n');
                    }
                    flushRouterBlock(out, seen, pending.toString(), source, currentName);
                }
            }
            if (out.length() == 0) {
                java.util.regex.Matcher ips = Pattern.compile("(?i)((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.\\d{1,3}\\.\\d{1,3})").matcher(pageText);
                while (ips.find()) addRouterDevice(out, seen, "جهاز متصل", ips.group(1), "", source);
            }
        } catch(Exception ignored) { }
        return out;
    }

'''
s = s[:start] + replacement + s[end:]
main.write_text(s, encoding='utf-8')
html = root / 'app/src/main/assets/index.html'
h = html.read_text(encoding='utf-8')
h = h.replace('نسخة تطوير 1.5.1:', 'نسخة تطوير 1.7.7:')
h = h.replace('قائمة محفوظة من آخر لقطة. اضغط فتح لوحة الراوتر وسجّل الدخول، ثم اضغط زر استيراد الأجهزة الظاهر أعلى صفحة الراوتر لتحديث القائمة الحية.', 'قائمة محفوظة محليًا. لتحديث الأجهزة الحية افتح لوحة الراوتر وسجّل الدخول، ثم اضغط زر استيراد الأجهزة أعلى الصفحة.')
h = h.replace("const owner=(d.mac||'').toLowerCase()==='12:b1:0d:bd:b3:4a';", "const owner=(d.mac||'').toLowerCase()==='12:b1:0d:bd:b3:4a'||d.ip==='192.168.1.186';")
html.write_text(h, encoding='utf-8')
gradle = root / 'app/build.gradle'
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 27', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '1.7.7'", g, count=1)
gradle.write_text(g, encoding='utf-8')
print('Applied Hadota WiFi Manager v1.7.7 row-based live client extraction patch.')
