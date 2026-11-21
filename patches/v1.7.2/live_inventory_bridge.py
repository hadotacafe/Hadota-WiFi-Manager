from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
html = root / "app/src/main/assets/index.html"
gradle = root / "app/build.gradle"

s = main.read_text()
# Capture the router's rendered text while the authenticated WebView session is active.
# Do not depend on a particular horizontal layout or require MAC addresses to exist.
old = '''        web.evaluateJavascript("(function(){return document.body?document.body.innerText:''})()", value -> {
            String text = value == null ? "" : value;
            try { text = new org.json.JSONArray("[" + text + "]").optString(0, ""); } catch(Exception ignored) {}
            org.json.JSONArray devices = parseRouterClients(text);'''
new = '''        web.evaluateJavascript("(function(){return JSON.stringify({text:document.body?document.body.innerText:'',html:document.body?document.body.innerHTML:''})})()", value -> {
            String text = "";
            String html = "";
            try {
                org.json.JSONObject captured = new org.json.JSONObject(value == null ? "{}" : value);
                text = captured.optString("text", "");
                html = captured.optString("html", "");
            } catch(Exception ignored) {
                try { text = new org.json.JSONArray("[" + (value == null ? "" : value) + "]").optString(0, ""); } catch(Exception ignoredAgain) {}
            }
            org.json.JSONArray devices = parseRouterClients(text + "\\n" + html);'''
if old not in s:
    raise SystemExit("captureRouterPage anchor not found")
s = s.replace(old, new, 1)

# Replace parser with permissive per-client parsing; MAC is optional, IP is required.
start = s.index("    private org.json.JSONArray parseRouterClients(String text) {")
end = s.index("    private String findValue(String s, String regex) {", start)
parser = r'''    private org.json.JSONArray parseRouterClients(String text) {
        org.json.JSONArray out = new org.json.JSONArray();
        java.util.regex.Matcher blocks = Pattern.compile("(?is)Client[- ](\\d+)(.*?)(?=Client[- ]\\d+|LAN Client Status|USB Storage Status|$)").matcher(text);
        java.util.HashSet<String> seen = new java.util.HashSet<>();
        while (blocks.find()) {
            String b = blocks.group(2);
            String ip = findValue(b, "IPv4 Address\\s*[:\\n\\s]*([0-9]{1,3}(?:\\.[0-9]{1,3}){3})");
            String mac = findValue(b, "MAC Address\\s*[:\\n\\s]*([0-9a-fA-F:]{17})");
            String name = findValue(b, "(?:Device Name|Host Name|Name)\\s*[:\\n\\s]*([^\\n<]{1,80})");
            addRouterDevice(out, seen, name, ip, mac, "WLAN");
        }
        java.util.regex.Matcher lan = Pattern.compile("(?is)LAN Client Status(.*?)(?=USB Storage Status|$)").matcher(text);
        if (lan.find()) {
            String b = lan.group(1);
            java.util.regex.Matcher rows = Pattern.compile("(?is)(?:Client[- ]\\d+)?(.*?)(?=Client[- ]\\d+|$)").matcher(b);
            while (rows.find()) {
                String row = rows.group(1);
                String ip = findValue(row, "IPv4 Address\\s*[:\\n\\s]*([0-9]{1,3}(?:\\.[0-9]{1,3}){3})");
                String mac = findValue(row, "MAC Address\\s*[:\\n\\s]*([0-9a-fA-F:]{17})");
                addRouterDevice(out, seen, "جهاز LAN", ip, mac, "LAN");
            }
        }
        return out;
    }

    private void addRouterDevice(org.json.JSONArray out, java.util.Set<String> seen, String name, String ip, String mac, String source) {
        if (ip == null || ip.isEmpty() || !ip.matches("(?:[0-9]{1,3}\\.){3}[0-9]{1,3}")) return;
        String key = (mac == null || mac.isEmpty()) ? ip : mac.toLowerCase(java.util.Locale.ROOT);
        if (!seen.add(key)) return;
        org.json.JSONObject d = new org.json.JSONObject();
        try {
            d.put("name", name == null || name.trim().isEmpty() ? "جهاز متصل" : name.trim());
            d.put("ip", ip);
            if (mac != null && !mac.isEmpty()) d.put("mac", mac.toLowerCase(java.util.Locale.ROOT));
            d.put("source", source);
            d.put("group", "unassigned");
            out.put(d);
        } catch(Exception ignored) {}
    }
'''
s = s[:start] + parser + s[end:]
main.write_text(s)

h = html.read_text()
# Keep device classifications stable across refreshes by MAC, falling back to IP.
h = h.replace("const prev=byMac[(d.mac||'').toLowerCase()]||{};", "const prev=byMac[(d.mac||'').toLowerCase()]||old.find(x=>x.ip===d.ip)||{};")
h = h.replace("group:owner?'owner':(prev.group||'staff')", "group:owner?'owner':(prev.group||'unassigned')")
h = h.replace('<option value="owner" ${d.group===\'owner\'?\'selected\':\'\'}>استثناء — جهاز المالك</option>', '<option value="owner" ${d.group===\'owner\'?\'selected\':\'\'}>استثناء — جهاز المالك</option><option value="unassigned" ${d.group===\'unassigned\'?\'selected\':\'\'}>غير مصنف</option>')
html.write_text(h)

g = gradle.read_text()
if "versionName '1.7.1'" not in g:
    raise SystemExit("Expected base version 1.7.1 not found")
g = g.replace("versionCode 21", "versionCode 22").replace("versionName '1.7.1'", "versionName '1.7.2'")
gradle.write_text(g)
