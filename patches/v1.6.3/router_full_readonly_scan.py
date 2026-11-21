from pathlib import Path
import json

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
gradle = root / "app/build.gradle"

s = router.read_text()
old = """                view.evaluateJavascript("(function(){if(document.getElementById('hadotaReturnBtn'))return;var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع إلى Hadota WiFi Manager';b.style='position:fixed;z-index:2147483647;top:8px;left:8px;padding:13px 16px;background:#d9b36a;color:#17120a;border:2px solid #fff;border-radius:12px;font-weight:bold;font-size:16px;box-shadow:0 2px 12px #000';b.onclick=function(){RouterBridge.capture()};document.body.appendChild(b);})();", null);"""
new = """                view.evaluateJavascript("(function(){if(document.getElementById('hadotaScanBtn'))return;function b(id,t,y,fn){var x=document.createElement('button');x.id=id;x.textContent=t;x.style='position:fixed;z-index:2147483647;top:'+y+'px;left:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';x.onclick=fn;document.body.appendChild(x)}b('hadotaScanBtn','فحص الأجهزة المتصلة وإرسال التقرير',8,function(){this.disabled=true;this.textContent='جارٍ الفحص...';RouterBridge.scanAll()});b('hadotaReturnBtn','رجوع للتطبيق',58,function(){RouterBridge.capture()})})();", null);"""
if old not in s:
    raise SystemExit("RouterActivity button anchor missing")
s = s.replace(old, new)

js = "(async function(){\nconst base=location.origin,seen=new Set(),todo=[],pages=[],endpoints=new Set(),assets=new Set();\nconst rx=/(device|client|wlan|wireless|dhcp|lan|host|mac|qos|queue|traffic|bandwidth|speed|filter|acl|status|network|arp|nat|firewall)/i;\nfunction add(v,set){try{const u=new URL(v,location.href);if(u.origin===base)set.add(u.href)}catch(e){}}\nfunction inspect(url,html,status){\n const d=new DOMParser().parseFromString(html,'text/html');\n pages.push({url,status,title:d.title,forms:[...d.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)}))});\n [...d.querySelectorAll('a[href]')].forEach(x=>{if(rx.test(x.href)||rx.test(x.textContent||''))add(x.href,todo)});\n [...d.querySelectorAll('form[action]')].forEach(x=>add(x.action,endpoints));\n [...d.querySelectorAll('script[src]')].forEach(x=>add(x.src,assets));\n for(const m of html.matchAll(/['\"]((?:\\\\/|\\\\.\\\\/)[^'\"]{1,180})['\"]/g))if(rx.test(m[1]))add(m[1],endpoints);\n}\nconst visibleText=(document.body?.innerText||'').slice(0,18000);\nconst visibleTables=[...document.querySelectorAll('table')].slice(0,30).map(t=>[...t.querySelectorAll('tr')].map(r=>[...r.querySelectorAll('th,td')].map(c=>(c.innerText||'').trim()).filter(Boolean)).filter(r=>r.length));\nconst currentHtml=document.documentElement?.outerHTML||'';\ninspect(location.href,currentHtml,200);seen.add(location.href);\nwhile(todo.length&&pages.length<40){\n const u=todo.shift();if(seen.has(u))continue;seen.add(u);\n try{const r=await fetch(u,{credentials:'include',redirect:'follow',cache:'no-store'});inspect(r.url||u,await r.text(),r.status)}\n catch(e){pages.push({url:u,error:String(e)})}\n}\nfor(const u of [...assets].slice(0,40)){\n try{const r=await fetch(u,{credentials:'include',redirect:'follow',cache:'no-store'});const t=await r.text();for(const m of t.matchAll(/['\"]([^'\"]{1,180})['\"]/g))if(rx.test(m[1])&&(m[1][0]=='/'||/cgi|api|goform/i.test(m[1])))add(m[1],endpoints)}catch(e){}\n}\nconst login=!!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]');\nreturn JSON.stringify({origin:base,currentUrl:location.href,currentTitle:document.title,currentPageAuthenticated:!login,visibleText,visibleTables,scannedAt:new Date().toISOString(),pages,scriptFiles:[...assets],candidateEndpoints:[...endpoints]});\n})()"
java_js = json.dumps(js, ensure_ascii=True)
anchor = """    private class RouterBridge {
        @JavascriptInterface public void capture() {"""
method = """    private class RouterBridge {
        @JavascriptInterface public void scanAll() {
            runOnUiThread(() -> {
                if (router == null) return;
                router.evaluateJavascript(""" + java_js + """, value -> {
                    String report = value == null ? "null" : value;
                    Intent result = new Intent();
                    result.putExtra("router_report", report);
                    setResult(RESULT_OK, result);
                    finish();
                });
            });
        }
        @JavascriptInterface public void capture() {"""
if anchor not in s:
    raise SystemExit("RouterBridge anchor missing")
s = s.replace(anchor, method)
router.write_text(s)

m = main.read_text()
needle = '            String text = data.getStringExtra("router_text");'
if needle not in m:
    raise SystemExit("MainActivity result anchor missing")
addition = '''
            String report = data.getStringExtra("router_report");
            if (report != null && web != null) {
                web.evaluateJavascript("routerInspectResult(" + org.json.JSONObject.quote("تقرير فحص الراوتر: " + report) + ")", null);
            }'''
if 'getStringExtra("router_report")' not in m:
    m = m.replace(needle, needle + addition)
main.write_text(m)

g = gradle.read_text().replace("versionCode 12", "versionCode 13").replace("versionName '1.6.2'", "versionName '1.6.3'")
gradle.write_text(g)
