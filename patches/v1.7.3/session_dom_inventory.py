from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text()
start = s.index("    private void captureRouterPage() {")
end = s.index("    private String getGatewayAddress() {", start)
new = r'''    private void captureRouterPage() {
        if (web == null) return;
        // Read the DOM from the already authenticated WebView. This preserves the router's
        // cookies/session and avoids making a second unauthenticated HTTP request.
        String js = "(function(){var clean=function(x){return (x||'').replace(/\\s+/g,' ').trim()};"
          + "var tables=Array.from(document.querySelectorAll('table')).map(function(t){return clean(t.innerText)});"
          + "var rows=Array.from(document.querySelectorAll('tr')).map(function(r){return Array.from(r.querySelectorAll('th,td')).map(function(c){return clean(c.innerText)})}).filter(function(r){return r.length});"
          + "return JSON.stringify({url:location.href,title:document.title,text:document.body?document.body.innerText:'',tables:tables,rows:rows})})()";
        web.evaluateJavascript(js, value -> {
            String payload = "";
            try { payload = new org.json.JSONArray("[" + (value == null ? "null" : value) + "]").optString(0, ""); }
            catch(Exception ignored) { }
            org.json.JSONArray devices = parseRouterClients(payload);
            web.removeJavascriptInterface("AndroidBridge");
            web.loadUrl("file:///android_asset/index.html");
            web.postDelayed(() -> {
                if (web != null) {
                    web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
                    web.evaluateJavascript("showLiveDevices(" + devices.toString() + "," + org.json.JSONObject.quote(payload) + ")", null);
                }
            }, 500);
        });
    }

    private org.json.JSONArray parseRouterClients(String payload) {
        org.json.JSONArray out = new org.json.JSONArray();
        java.util.HashSet<String> seen = new java.util.HashSet<>();
        try {
            org.json.JSONObject root = new org.json.JSONObject(payload);
            org.json.JSONArray rows = root.optJSONArray("rows");
            String pageText = root.optString("text", "");
            String pageUrl = root.optString("url", "").toLowerCase(java.util.Locale.ROOT);
            String source = (pageUrl.contains("lan") || pageText.toLowerCase(java.util.Locale.ROOT).contains("lan client status")) ? "LAN" : "WLAN";
            if (rows != null) {
                String currentName = "جهاز متصل";
                StringBuilder block = new StringBuilder();
                for (int i=0; i<rows.length(); i++) {
                    org.json.JSONArray row = rows.optJSONArray(i);
                    if (row == null) continue;
                    StringBuilder line = new StringBuilder();
                    for (int j=0; j<row.length(); j++) {
                        String cell = row.optString(j, "").trim();
                        if (cell.isEmpty()) continue;
                        if (line.length()>0) line.append(" | ");
                        line.append(cell);
                    }
                    String value = line.toString();
                    if (value.isEmpty()) continue;
                    if (value.matches("(?is).*client\\s*[-#:]?\\s*\\d+.*")) {
                        flushRouterBlock(out, seen, block.toString(), source, currentName);
                        block.setLength(0);
                        currentName = value.replaceAll("(?is).*?(client\\s*[-#:]?\\s*\\d+).*", "$1");
                    }
                    block.append(value).append('\n');
                }
                flushRouterBlock(out, seen, block.toString(), source, currentName);
            }
            if (out.length()==0) {
                String all = pageText + "\\n" + root.optString("tables", "");
                java.util.regex.Matcher ips = Pattern.compile("(?i)(?:IPv4\\s*)?IP\\s*Address\\s*[:：|]?\\s*((?:\\d{1,3}\\.){3}\\d{1,3})").matcher(all);
                while (ips.find()) addRouterDevice(out, seen, "جهاز متصل", ips.group(1), "", source);
            }
        } catch(Exception ignored) { }
        return out;
    }

    private void flushRouterBlock(org.json.JSONArray out, java.util.Set<String> seen, String block, String source, String name) {
        if (block == null || block.isEmpty()) return;
        String ip = findValue(block, "(?i)(?:IPv4\\s*)?IP\\s*Address\\s*[:：|]?\\s*((?:[0-9]{1,3}\\.){3}[0-9]{1,3})");
        if (ip.isEmpty()) ip = findValue(block, "(?i)((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.[0-9]{1,3}\\.[0-9]{1,3})");
        String mac = findValue(block, "(?i)(?:MAC\\s*Address\\s*[:：|]?\\s*)?([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})");
        String deviceName = findValue(block, "(?i)(?:Host\\s*Name|Device\\s*Name|HostName|Name)\\s*[:：|]?\\s*([^\\n|]{1,70})");
        addRouterDevice(out, seen, deviceName.isEmpty()?name:deviceName, ip, mac, source);
    }

    private void addRouterDevice(org.json.JSONArray out, java.util.Set<String> seen, String name, String ip, String mac, String source) {
        if (ip == null || ip.isEmpty() || !ip.matches("(?:[0-9]{1,3}\\.){3}[0-9]{1,3}")) return;
        String key = (mac == null || mac.isEmpty()) ? ip : mac.toLowerCase(java.util.Locale.ROOT);
        if (!seen.add(key)) return;
        org.json.JSONObject d = new org.json.JSONObject();
        try {
            d.put("name", name == null || name.trim().isEmpty() ? "جهاز متصل" : name.trim());
            d.put("ip", ip);
            if (mac != null && !mac.isEmpty()) d.put("mac", mac.toLowerCase(java.util.Locale.ROOT).replace('-', ':'));
            d.put("source", source);
            d.put("group", "unassigned");
            out.put(d);
        } catch(Exception ignored) {}
    }

    private String findValue(String s, String regex) {
        java.util.regex.Matcher m = Pattern.compile("(?is)" + regex).matcher(s);
        return m.find() ? m.group(1).trim() : "";
    }

'''
s = s[:start] + new + s[end:]
main.write_text(s)

gradle = root / "app/build.gradle"
g = gradle.read_text()
g = re.sub(r"versionCode\\s+\\d+", "versionCode 23", g, count=1)
g = re.sub(r"versionName\\s+'[^']+'", "versionName '1.7.3'", g, count=1)
gradle.write_text(g)

html = root / "app/src/main/assets/index.html"
h = html.read_text()
h = h.replace("function showLiveDevices(devices){", "function showLiveDevices(devices,rawPayload){")
h = h.replace("const prev=byMac[(d.mac||'').toLowerCase()]||{};", "const prev=byMac[(d.mac||'').toLowerCase()]||old.find(x=>x.ip===d.ip)||{};")
h = h.replace("group:owner?'owner':(prev.group||'staff')", "group:owner?'owner':(prev.group||'unassigned')")
h = h.replace("$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من صفحة الراوتر الحالية. هذه قراءة من جلسة الراوتر داخل التطبيق.'", "$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من جلسة الراوتر الحالية. '+(rawPayload?'تم التقاط جداول الصفحة مباشرة.':'')")
html.write_text(h)

