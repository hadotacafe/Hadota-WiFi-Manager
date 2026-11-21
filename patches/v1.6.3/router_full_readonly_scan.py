from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
gradle = root / "app/build.gradle"

s = router.read_text()
old = "view.evaluateJavascript(\"(function(){if(document.getElementById('hadotaReturnBtn'))return;var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع إلى Hadota WiFi Manager';b.style='position:fixed;z-index:2147483647;top:8px;left:8px;padding:13px 16px;background:#d9b36a;color:#17120a;border:2px solid #fff;border-radius:12px;font-weight:bold;font-size:16px;box-shadow:0 2px 12px #000';b.onclick=function(){RouterBridge.capture()};document.body.appendChild(b);})();\", null);"
new = """view.evaluateJavascript(\"(function(){if(document.getElementById('hadotaScanBtn'))return;function add(id,label,top,color,fn){var b=document.createElement('button');b.id=id;b.textContent=label;b.style='position:fixed;z-index:2147483647;top:'+top+'px;left:8px;padding:12px 14px;background:'+color+';color:#17120a;border:2px solid #fff;border-radius:11px;font-weight:bold;font-size:14px;box-shadow:0 2px 12px #000';b.onclick=fn;document.body.appendChild(b)}add('hadotaScanBtn','فحص شامل للراوتر',8,'#d9b36a',function(){this.textContent='جارٍ الفحص...';RouterBridge.scanAll()});add('hadotaReturnBtn','رجوع إلى التطبيق',58,'#e8d5ad',function(){RouterBridge.capture()});})();\", null);"""
if old not in s:
    raise SystemExit("RouterActivity injection anchor missing")
s = s.replace(old, new)
old_bridge = """    private class RouterBridge {
        @JavascriptInterface public void capture() {"""
new_bridge = """    private class RouterBridge {
        @JavascriptInterface public void scanAll() {
            runOnUiThread(() -> {
                if (router == null) return;
                String js = \"(async function(){const origin=location.origin,seen=new Set(),queue=[location.href],pages=[],assets=new Set(),api=new Set(),maxPages=35;const key=/\\\\b(device|client|wlan|wireless|dhcp|lan|host|mac|qos|queue|traffic|bandwidth|speed|filter|acl|status|network|arp|nat|firewall)\\\\b/i;function add(u,set){try{let x=new URL(u,location.href);if(x.origin===origin)set.add(x.href)}catch(e){}}while(queue.length&&pages.length<maxPages){let u=queue.shift();if(seen.has(u))continue;seen.add(u);try{let res=await fetch(u,{credentials:'same-origin'});let txt=await res.text();let doc=new DOMParser().parseFromString(txt,'text/html');let title=(doc.title||u).trim();let forms=[...doc.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)}));let links=[...doc.querySelectorAll('a[href]')].map(a=>a.href);let scripts=[...doc.querySelectorAll('script[src]')].map(a=>a.src);let paths=[...txt.matchAll(/['\\\\\"]((?:\\\\/|\\\\.\\\\/)[^'\\\\\"]{1,180})['\\\\\"]/g)].map(m=>m[1]);pages.push({url:u,status:res.status,title,forms});scripts.forEach(x=>add(x,assets));links.forEach(x=>{try{let z=new URL(x);if(z.origin===origin&&key.test(z.href)&&!seen.has(z.href))queue.push(z.href)}catch(e){}});paths.filter(x=>key.test(x)).forEach(x=>add(x,api));}catch(e){pages.push({url:u,error:String(e)})}}let assetText=[];for(let u of [...assets].slice(0,35)){try{let r=await fetch(u,{credentials:'same-origin'}),t=await r.text();for(let m of t.matchAll(/['\\\\\"]([^'\\\\\"]{1,180})['\\\\\"]/g)){let v=m[1];if(key.test(v)&&(v.startsWith('/')||/\\\\b(get|post|query|cgi-bin)\\\\b/i.test(v)))add(v,api)}assetText.push(u+' ['+r.status+']')}catch(e){assetText.push(u+' [failed]')}}return JSON.stringify({generated:new Date().toISOString(),origin,pages,assets:assetText,candidateEndpoints:[...api].slice(0,120)});})()\";
                router.evaluateJavascript(js, value -> {
                    String report = value == null ? \"تعذر إنشاء التقرير\" : value;
                    try { report = new org.json.JSONArray(\"[\" + report + \"]\").optString(0, report); } catch (Exception ignored) {}
                    Intent result = new Intent();
                    result.putExtra(\"router_report\", report);
                    setResult(RESULT_OK, result);
                    finish();
                });
            });
        }
        @JavascriptInterface public void capture() {"""
if old_bridge not in s:
    raise SystemExit("RouterBridge anchor missing")
s = s.replace(old_bridge, new_bridge)
router.write_text(s)

m = main.read_text()
needle = 'String text = data.getStringExtra("router_text");'
if needle not in m:
    raise SystemExit("MainActivity result anchor missing")
m = m.replace(needle, needle + '\n            String report = data.getStringExtra("router_report");\n            if (report != null && web != null) web.evaluateJavascript("routerInspectResult(" + org.json.JSONObject.quote("تقرير الفحص الشامل:\\n" + report) + ")", null);')
main.write_text(m)

g = gradle.read_text()
g = g.replace("versionCode 12", "versionCode 13").replace("versionName '1.6.2'", "versionName '1.6.3'")
gradle.write_text(g)
