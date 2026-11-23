from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
# Publish the handler explicitly on window and attach a native DOM listener after page load.
s=s.replace('onclick="classifyImportedAsStaff()"','onclick="window.classifyImportedAsStaff()"')
s=s.replace("function classifyImportedAsStaff(){","window.classifyImportedAsStaff = function(){",1)
# close the function at the first matching handler boundary
start=s.index("window.classifyImportedAsStaff = function(){")
end=s.index("\n}\n\n\nfunction routerInspectResult",start)
if end<0: raise SystemExit("Could not locate classification handler end")
s=s[:end]+"\n};"+s[end+2:]
# Add an explicit click/touch listener, status feedback, and prevent duplicate binding.
bind="""(function(){var b=document.getElementById('classifyImportedBtn');if(!b||b.dataset.hadotaBound==='1')return;b.dataset.hadotaBound='1';var run=function(e){if(e){e.preventDefault();e.stopPropagation();}var out=document.getElementById('inspectResult');if(out)out.textContent='جارٍ تصنيف الأجهزة وحفظها...';try{window.classifyImportedAsStaff();}catch(err){if(out)out.textContent='تعذر التصنيف: '+(err&&err.message?err.message:String(err));}};b.addEventListener('click',run,true);b.addEventListener('touchend',run,{capture:true,passive:false});})();"""
if "b.dataset.hadotaBound" not in s:
    s=s.replace("loadPolicy();updateGateway();renderInventory();",bind+"\nloadPolicy();updateGateway();renderInventory();",1)
if "window.classifyImportedAsStaff = function()" not in s or "b.dataset.hadotaBound" not in s:
    raise SystemExit("Classification handler binding verification failed")
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 46",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.11'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.11: explicit window handler, capture-phase click and touchend listeners, immediate progress/error feedback")
