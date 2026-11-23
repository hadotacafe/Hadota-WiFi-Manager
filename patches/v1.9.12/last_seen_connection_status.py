from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
old="const merged=devices.map(d=>{const prev=byMac[(d.mac||'').toLowerCase()]||old.find(x=>x.ip===d.ip)||{};const owner=(d.mac||'').toLowerCase()==='12:b1:0d:bd:b3:4a'||d.ip==='192.168.1.186';return {...d,name:prev.name&&prev.name!=='جهاز المالك — مستثنى'?prev.name:(d.name||'جهاز متصل'),group:owner?'owner':(prev.group||'unassigned')}});"
new="const seenAt=new Date().toISOString();const merged=devices.map(d=>{const prev=byMac[(d.mac||'').toLowerCase()]||old.find(x=>x.ip===d.ip)||{};const owner=(d.mac||'').toLowerCase()==='12:b1:0d:bd:b3:4a'||d.ip==='192.168.1.186';return {...d,name:prev.name&&prev.name!=='جهاز المالك — مستثنى'?prev.name:(d.name||'جهاز متصل'),group:owner?'owner':(prev.group||'unassigned'),connectionStatus:'connected',lastSeenAt:seenAt}});"
if old not in s: raise SystemExit("live merge expression missing")
s=s.replace(old,new,1)
old2='<div class="small warn">حالة الاتصال: غير متحقق من الراوتر</div>'
new2="""<div class="small \${d.connectionStatus==='connected'?'good':'warn'}">حالة الاتصال: \${d.connectionStatus==='connected'?'ظهر متصلًا في آخر استيراد':'غير متحقق من الراوتر'}\${d.lastSeenAt ? ' — آخر ظهور: ' + new Date(d.lastSeenAt).toLocaleString('ar-EG') : ''}</div>"""
if old2 not in s: raise SystemExit("inventory status label missing")
s=s.replace(old2,new2,1)
s=s.replace("renderInventory();$('classifyImportedBtn').style.display='block';$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من جلسة الراوتر الحالية. راجعها ثم صنّف أجهزة الموظفين.'","renderInventory();$('classifyImportedBtn').style.display='block';$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من جلسة الراوتر الحالية. الحالة المعروضة: متصل وقت آخر استيراد.'",1)
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 47",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.12'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.12: last-seen connection status; no false offline inference")
