from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
anchor='<div class="result muted" id="inspectResult">لم يتم فحص صفحة الدخول بعد.</div>'
button=anchor+'<button class="btn alt" id="classifyImportedBtn" style="display:none" onclick="classifyImportedAsStaff()">تصنيف الأجهزة المستوردة كموظفين</button>'
if anchor not in s: raise SystemExit("Import result anchor missing")
if 'id="classifyImportedBtn"' not in s: s=s.replace(anchor,button,1)
old="function showLiveDevices(devices,rawPayload){if(!Array.isArray(devices)||!devices.length){$('inspectResult').textContent='لم يتم استخراج أجهزة من الصفحة الحالية. افتح صفحة WLAN Client Status وLAN Client Status ثم أعد الاستيراد.';return}"
new="function showLiveDevices(devices,rawPayload){if(!Array.isArray(devices)||!devices.length){$('inspectResult').textContent='لم يتم استخراج أجهزة من الصفحة الحالية. افتح صفحة WLAN Client Status وLAN Client Status ثم أعد الاستيراد.';return}"
if old not in s: raise SystemExit("showLiveDevices function anchor missing")
# Save the exact set captured in this import; do not classify unrelated saved/manual entries.
needle="localStorage.setItem('hadotaInventory',JSON.stringify(merged));renderInventory();$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من جلسة الراوتر الحالية. '+(rawPayload?'تم التقاط جداول الصفحة مباشرة.':'')}"
replacement="localStorage.setItem('hadotaInventory',JSON.stringify(merged));localStorage.setItem('hadotaLastImportedKeys',JSON.stringify(merged.map(d=>d.mac?'mac:'+d.mac.toLowerCase():'ip:'+d.ip)));renderInventory();$('classifyImportedBtn').style.display='block';$('inspectResult').textContent='تم استيراد '+merged.length+' جهاز من جلسة الراوتر الحالية. راجعها ثم صنّف أجهزة الموظفين.'}"
if needle not in s: raise SystemExit("Import merge completion anchor missing")
s=s.replace(needle,replacement,1)
fn="""function classifyImportedAsStaff(){
 const keys=JSON.parse(localStorage.getItem('hadotaLastImportedKeys')||'[]');
 const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 const keyOf=d=>d.mac?'mac:'+d.mac.toLowerCase():'ip:'+d.ip;
 const matches=a.filter(d=>keys.includes(keyOf(d))&&d.group!=='owner');
 if(!matches.length){alert('لا توجد أجهزة مستوردة حديثًا لتصنيفها.');return}
 const current=a.filter(d=>d.group==='staff').length;
 if(current+matches.filter(d=>d.group!=='staff').length>14){alert('عدد أجهزة الموظفين سيتجاوز الحد المسموح: 14.');return}
 if(!confirm('تم العثور على '+matches.length+' أجهزة من آخر استيراد. هل تؤكد تصنيفها كأجهزة موظفين؟'))return;
 a.forEach(d=>{if(keys.includes(keyOf(d))&&d.group!=='owner')d.group='staff'});
 localStorage.setItem('hadotaInventory',JSON.stringify(a));renderInventory();
 $('inspectResult').textContent='تم تصنيف '+matches.length+' أجهزة كموظفين وحفظها على الهاتف.';
 $('classifyImportedBtn').style.display='none';
}
"""
if "function classifyImportedAsStaff()" not in s:
    s=s.replace("function routerInspectResult(msg){",fn+"function routerInspectResult(msg){",1)
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 39",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.4'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.4: adds explicit confirmation to classify only the latest imported router devices as staff, enforcing 14-device limit and preserving owner exclusions")
