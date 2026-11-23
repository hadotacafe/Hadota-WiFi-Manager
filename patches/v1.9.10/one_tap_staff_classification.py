from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
# Remove the WebView modal/confirm chain completely. The user explicitly requested
# classification and repeated modal attempts did not respond; use one direct action.
s=re.sub(r'<div id="staffClassifyModal".*?</div></div>', '', s, count=1, flags=re.S)
# Replace the classification button with one direct click action.
s=re.sub(r'<button class="btn alt" id="classifyImportedBtn".*?</button>',
         '<button class="btn alt" id="classifyImportedBtn" style="display:none" type="button" onclick="classifyImportedAsStaff()">تصنيف الأجهزة المستوردة كموظفين</button>',
         s, count=1, flags=re.S)
start=s.find("window.classifyImportedAsStaff = function(){")
if start<0: raise SystemExit("classification handler not found")
end=s.find("\n};",start)
if end<0: raise SystemExit("classification handler end not found")
end+=3
fn="""function classifyImportedAsStaff(){
 try {
  const keys=JSON.parse(localStorage.getItem('hadotaLastImportedKeys')||'[]');
  const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
  const keyOf=d=>d.mac?'mac:'+String(d.mac).toLowerCase():'ip:'+String(d.ip||'');
  const matches=a.filter(d=>keys.includes(keyOf(d))&&d.group!=='owner');
  const current=a.filter(d=>d.group==='staff').length;
  const addCount=matches.filter(d=>d.group!=='staff').length;
  if(!matches.length){
   $('inspectResult').textContent='لم أجد أجهزة من آخر استيراد للتصنيف. أعد استيراد الأجهزة أولًا.';
   return;
  }
  if(current+addCount>14){
   $('inspectResult').textContent='لا يمكن التصنيف: عدد أجهزة الموظفين سيتجاوز 14. راجع القائمة أولًا.';
   return;
  }
  matches.forEach(d=>d.group='staff');
  localStorage.setItem('hadotaInventory',JSON.stringify(a));
  renderInventory();
  $('classifyImportedBtn').style.display='none';
  $('inspectResult').textContent='تم بنجاح: تصنيف وحفظ '+matches.length+' جهازًا كأجهزة موظفين على الهاتف.';
 } catch(e) {
  $('inspectResult').textContent='تعذر التصنيف: '+(e&&e.message?e.message:'خطأ غير معروف');
 }
}"""
s=s[:start]+fn+s[end:]
# Remove the obsolete confirmation handler left by earlier patch versions.
old_commit=s.find("window.commitStaffClassification = function(){")
if old_commit>=0:
    old_end=s.find("\n};",old_commit)
    if old_end<0: raise SystemExit("Old commit handler terminator missing")
    s=s[:old_commit]+s[old_end+3:]
# Remove any stale modal references from the markup.
s=s.replace("id=\\"staffClassifyError\\"","")
if 'staffClassifyModal' in s or 'commitStaffClassification' in s:
    raise SystemExit("Old modal code remains")
if 'onclick="classifyImportedAsStaff()"' not in s or 'function classifyImportedAsStaff()' not in s:
    raise SystemExit("Direct classification action verification failed")
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 45",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.10'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.10: one-tap staff classification, no modal/confirm; saves local roster and reports exact count")
