from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text(encoding="utf-8")

old = "scripts:Array.from(document.scripts).map(x=>x.src||'[inline script]'),frames:"
new = "scripts:Array.from(document.scripts).map(x=>x.src||'[inline script]'),scriptDetails:Array.from(document.scripts).filter(x=>!x.src).map((x,i)=>({index:i+1,code:(x.textContent||'').slice(0,10000).replace(/((?:password|passwd|sess_token|IF_LogOff|cookie|authorization|csrf|token)\\s*[=:]\\s*)[^,;\\n}]+/ig,'$1[محجوب]')})),frames:"
if old not in s:
    raise SystemExit("script inventory anchor not found; refusing to patch an unexpected source")
s = s.replace(old, new, 1)
main.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g = re.sub(r"versionCode\\s+\\d+", "versionCode 26", g, count=1)
g = re.sub(r"versionName\\s+'[^']+'", "versionName '1.7.6'", g, count=1)
gradle.write_text(g, encoding="utf-8")
