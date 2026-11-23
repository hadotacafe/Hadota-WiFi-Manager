from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
# Expose the handler on window: WebView inline onclick cannot call a function hidden
# inside the app's initialization closure.
s=s.replace('onclick="classifyImportedAsStaff()"','')
old="function classifyImportedAsStaff(){"
new="window.classifyImportedAsStaff = function(){"
if old not in s: raise SystemExit("Classification function declaration missing")
s=s.replace(old,new,1)
end=""" $('classifyImportedBtn').style.display='none';
}"""
replacement=""" $('classifyImportedBtn').style.display='none';
};"""
if end not in s: raise SystemExit("Classification function ending missing")
s=s.replace(end,replacement,1)
# Bind a real click listener after the DOM is available; no dependence on inline handler scope.
bind="""const classifyBtn=document.getElementById('classifyImportedBtn');
if(classifyBtn){classifyBtn.addEventListener('click',function(){try{window.classifyImportedAsStaff();}catch(e){alert('تعذر تصنيف الأجهزة: '+e.message);}});}"""
if "classifyBtn.addEventListener('click'" not in s:
    # Insert the binding immediately after the exposed handler.
    s=s.replace(replacement,replacement+"\n"+bind,1)
if "window.classifyImportedAsStaff = function()" not in s or "classifyBtn.addEventListener('click'" not in s:
    raise SystemExit("Classification click binding verification failed")
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 41",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.6'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.6: exposes classification handler on window and binds a direct WebView click listener")
