from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
s=s.replace('id="classifyImportedBtn" style="display:none" >','id="classifyImportedBtn" style="display:none" type="button" onclick="window.classifyImportedAsStaff()">')
s=s.replace('id="confirmStaffClassify" type="button">','id="confirmStaffClassify" type="button" onclick="window.commitStaffClassification()">')
s=s.replace('id="cancelStaffClassify" type="button">','id="cancelStaffClassify" type="button" onclick="document.getElementById(\\'staffClassifyModal\\').style.display=\\'none\\'">')
s=s.replace('function commitStaffClassification(){','window.commitStaffClassification = function(){',1)
s=s.replace(" $('staffClassifyModal').style.display='none';\n}"," $('staffClassifyModal').style.display='none';\n};",1)
# Remove both previous click-binding approaches; inline handlers are the sole action path.
s=re.sub(r"const classifyBtn=document\.getElementById\('classifyImportedBtn'\);.*?\n(?=function routerInspectResult)", "", s, count=1, flags=re.S)
s=re.sub(r"document\.addEventListener\('click',function\(ev\)\{var target=ev\.target.*?\},true\);", "", s, count=1)
# Add an inline error surface inside the confirmation modal.
s=s.replace('<button class="btn alt" id="cancelStaffClassify"', '<div id="staffClassifyError" class="small" style="color:#ffaaaa;min-height:20px"></div><button class="btn alt" id="cancelStaffClassify"',1)
# Ensure every action is directly wired and callable globally.
checks=['onclick="window.classifyImportedAsStaff()"','onclick="window.commitStaffClassification()"','window.commitStaffClassification = function(){','id="staffClassifyError"']
if not all(x in s for x in checks): raise SystemExit("Direct button action verification failed")
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 44",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.9'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.9: direct inline handlers for classify/confirm/cancel; removed duplicate delegated listeners")
