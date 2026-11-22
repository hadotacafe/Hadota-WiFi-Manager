from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text()
needle="buttons:Array.from(document.querySelectorAll('button,input[type=button],input[type=submit]')).map(x=>clean(x.innerText||x.value)),text:"
replacement="buttons:Array.from(document.querySelectorAll('button,input[type=button],input[type=submit]')).map(x=>clean(x.innerText||x.value)),forms:Array.from(document.forms).map(f=>({name:f.name||f.id||'',method:(f.method||'get').toUpperCase(),action:f.action,fields:Array.from(f.elements).map(e=>({name:e.name||e.id||'',type:e.type||e.tagName.toLowerCase(),value:(e.type==='password'||e.type==='hidden')?'[محجوب]':(e.value||'')}))})),scripts:Array.from(document.scripts).map(x=>x.src||'[inline script]'),frames:Array.from(document.querySelectorAll('iframe,frame')).map(x=>({id:x.id||'',name:x.name||'',src:x.src||''})),handlers:Array.from(document.querySelectorAll('[onclick],[onsubmit],[onchange]')).map(x=>({tag:x.tagName,id:x.id||'',name:x.name||'',onclick:x.getAttribute('onclick')||'',onsubmit:x.getAttribute('onsubmit')||'',onchange:x.getAttribute('onchange')||''})),text:"
if needle not in s: raise SystemExit("inspector data anchor not found")
s=s.replace(needle,replacement,1)
main.write_text(s)
g=root/"app/build.gradle"
v=g.read_text()
v=re.sub(r"versionCode\\s+\\d+","versionCode 25",v,count=1)
v=re.sub(r"versionName\\s+'[^']+'","versionName '1.7.5'",v,count=1)
g.write_text(v)
