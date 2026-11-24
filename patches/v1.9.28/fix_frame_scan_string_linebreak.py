from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
p=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s=p.read_text(encoding="utf-8")
bad="docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});\n\\nseen.add(location.href);"
good="docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});\\nseen.add(location.href);"
if bad not in s: raise SystemExit("unexpected line break in frame scan Java string")
s=s.replace(bad,good,1)
p.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
v=g.read_text(encoding="utf-8")
v,a=re.subn(r"versionCode\s+\d+","versionCode 63",v,count=1)
v,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.28'",v,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
g.write_text(v,encoding="utf-8")
print("v1.9.28: remove stray physical newline from JavaScript string; frame-aware scanner compiles as one Java string")
