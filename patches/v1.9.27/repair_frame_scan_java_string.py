from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
p=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s=p.read_text(encoding="utf-8")
start=s.index("const docs=[document],frameSeen=new Set();")
end=s.index("docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});",start)+len("docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});")
fixed="const docs=[document],frameSeen=new Set();(function walk(w){try{for(let i=0;i<w.frames.length;i++){const f=w.frames[i];if(frameSeen.has(f))continue;frameSeen.add(f);try{const d=f.document;if(d&&d.documentElement){docs.push(d);walk(f)}}catch(e){}}}catch(e){}})(window);docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});"
s=s[:start]+fixed+s[end:]
if "\\nseen.add(location.href)" not in s:
 raise SystemExit("scan crawler continuation missing after frame traversal repair")
p.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
v=g.read_text(encoding="utf-8")
v,a=re.subn(r"versionCode\s+\d+","versionCode 62",v,count=1)
v,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.27'",v,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
g.write_text(v,encoding="utf-8")
print("v1.9.27: repair Java string escaping for frame-aware scan; keep frame traversal inside WebView JavaScript")
