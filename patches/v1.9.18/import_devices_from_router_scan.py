from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
router=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s=router.read_text(encoding="utf-8")
s=s.replace("const base=location.origin,seen=new Set(),todo=[],pages=[],endpoints=new Set(),assets=new Set();","const base=location.origin,seen=new Set(),todo=[],pages=[],endpoints=new Set(),assets=new Set(),devices=[],deviceKeys=new Set();",1)
old="pages.push({url,status,title:d.title,forms:[...d.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)}))});"
js=r"""const ipRe=new RegExp('(?:^|[^0-9])((?:192\\.168|10|172\\.(?:1[6-9]|2[0-9]|3[01]))\\.\\d{1,3}\\.\\d{1,3})(?:$|[^0-9])','i');
 const macRe=new RegExp('\\\\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\\\\b','i');
 const clean=v=>(v||'').replace(/\\s+/g,' ').trim();
 function addRow(cells){const line=cells.map(clean).filter(Boolean);const joined=line.join(' | ');const im=ipRe.exec(joined);if(!im)return;const mm=macRe.exec(joined);let name=line.find(v=>v&&!ipRe.test(v)&&!macRe.test(v)&&!/^(online|connected|active|wlan|lan|yes|no|ip address|mac address|host name|device name)$/i.test(v))||'جهاز متصل';const ip=im[1],mac=mm?mm[1].replace(/-/g,':').toLowerCase():'';const key=mac||ip;if(!deviceKeys.has(key)){deviceKeys.add(key);devices.push({name,ip,mac,source:/lan/i.test(url+' '+d.title)?'LAN':'WLAN',group:'unassigned'});}}
 [...d.querySelectorAll('table tr')].forEach(r=>addRow([...r.querySelectorAll('th,td')].map(c=>c.innerText||c.textContent||'')));
 if(!devices.length){for(const line of (d.body?.innerText||'').split(String.fromCharCode(10)))addRow([line]);}"""
def esc_java(x):
    return x.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")
replacement=old+"\\n"+esc_java(js)
if old not in s: raise SystemExit("RouterActivity inspect anchor missing")
s=s.replace(old,replacement,1)
if "candidateEndpoints:[...endpoints]});" not in s: raise SystemExit("RouterActivity report anchor missing")
s=s.replace("candidateEndpoints:[...endpoints]});","candidateEndpoints:[...endpoints],devices});",1)
old2="""                        result.putExtra("router_report", report);
                        result.putExtra("router_text", pageText);"""
new2="""                        result.putExtra("router_report", report);
                        result.putExtra("router_text", pageText);
                        try {
                            String decoded = new org.json.JSONArray("[" + report + "]").optString(0, "{}");
                            org.json.JSONObject scan = new org.json.JSONObject(decoded);
                            org.json.JSONArray found = scan.optJSONArray("devices");
                            result.putExtra("router_devices", found == null ? "[]" : found.toString());
                        } catch (Exception ignored) { result.putExtra("router_devices", "[]"); }"""
if old2 not in s: raise SystemExit("RouterActivity result extras anchor missing")
s=s.replace(old2,new2,1)
router.write_text(s,encoding="utf-8")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
m=main.read_text(encoding="utf-8")
old3="""            org.json.JSONArray devices = parseRouterClients(text == null ? "" : text);
            web.evaluateJavascript("showLiveDevices(" + devices.toString() + ")", null);"""
new3="""            org.json.JSONArray devices = new org.json.JSONArray();
            try {
                String imported = data.getStringExtra("router_devices");
                if (imported != null) devices = new org.json.JSONArray(imported);
            } catch (Exception ignored) {}
            if (devices.length() == 0) devices = parseRouterClients(text == null ? "" : text);
            web.evaluateJavascript("showLiveDevices(" + devices.toString() + ")", null);"""
if old3 not in m: raise SystemExit("MainActivity import result anchor missing")
m=m.replace(old3,new3,1)
main.write_text(m,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 53",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.18'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.18: extract client rows from scanned router pages and return structured devices to the app")
