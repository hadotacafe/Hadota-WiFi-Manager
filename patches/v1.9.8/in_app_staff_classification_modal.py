from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
# Replace browser confirm/alert workflow with an in-page modal supported by Android WebView.
anchor='<button class="btn alt" id="classifyImportedBtn" style="display:none" >تصنيف الأجهزة المستوردة كموظفين</button>'
if anchor not in s:
    raise SystemExit("Classification button anchor missing")
modal='''<div id="staffClassifyModal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.78);align-items:center;justify-content:center;padding:22px">
<div style="width:100%;max-width:440px;background:#142233;border:1px solid #c9a45d;border-radius:18px;padding:22px;box-shadow:0 20px 60px #000">
<h2 style="color:#f3d99e;margin:0 0 12px">تأكيد تصنيف أجهزة الموظفين</h2>
<p id="staffClassifyMessage" style="color:#f7f3e9;line-height:1.8">سيتم تصنيف الأجهزة المستوردة الأخيرة كأجهزة موظفين.</p>
<button class="btn" id="confirmStaffClassify" type="button">تأكيد وحفظ</button>
<button class="btn alt" id="cancelStaffClassify" type="button">إلغاء</button>
</div></div>'''
if 'id="staffClassifyModal"' not in s:
    s=s.replace(anchor,anchor+modal,1)
start=s.index("window.classifyImportedAsStaff = function(){")
end=s.index("\n};",start)+3
func="""window.classifyImportedAsStaff = function(){
 const keys=JSON.parse(localStorage.getItem('hadotaLastImportedKeys')||'[]');
 const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 const keyOf=d=>d.mac?'mac:'+d.mac.toLowerCase():'ip:'+d.ip;
 const matches=a.filter(d=>keys.includes(keyOf(d))&&d.group!=='owner');
 const current=a.filter(d=>d.group==='staff').length;
 const addCount=matches.filter(d=>d.group!=='staff').length;
 if(!matches.length){$('inspectResult').textContent='لا توجد أجهزة مستوردة حديثًا للتصنيف. أعد استيراد الأجهزة أولًا.';return}
 if(current+addCount>14){$('inspectResult').textContent='لا يمكن التصنيف: سيزيد عدد أجهزة الموظفين عن 14. راجع التصنيفات الحالية أولًا.';return}
 $('staffClassifyMessage').textContent='تم العثور على '+matches.length+' أجهزة من آخر استيراد. هل تؤكد إضافتها إلى قائمة الموظفين؟';
 $('staffClassifyModal').style.display='flex';
};
function commitStaffClassification(){
 const keys=JSON.parse(localStorage.getItem('hadotaLastImportedKeys')||'[]');
 const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 const keyOf=d=>d.mac?'mac:'+d.mac.toLowerCase():'ip:'+d.ip;
 let count=0;
 a.forEach(d=>{if(keys.includes(keyOf(d))&&d.group!=='owner'){d.group='staff';count++}});
 localStorage.setItem('hadotaInventory',JSON.stringify(a));
 renderInventory();
 $('inspectResult').textContent='تم تصنيف '+count+' أجهزة كموظفين وحفظها على الهاتف.';
 $('classifyImportedBtn').style.display='none';
 $('staffClassifyModal').style.display='none';
}
"""
s=s[:start]+func+s[end:]
# Remove earlier direct binding, use one delegated handler for all three modal controls.
s=re.sub(r"const classifyBtn=document\.getElementById\('classifyImportedBtn'\);if\(classifyBtn\)\{classifyBtn\.addEventListener\('click',function\(\)\{try\{window\.classifyImportedAsStaff\(\);\}catch\(e\)\{alert\('تعذر تصنيف الأجهزة: '\+e\.message\);\}\}\);\}\n?","",s)
s=s.replace("var target=ev.target&&ev.target.closest?ev.target.closest('#classifyImportedBtn'):null;if(target){ev.preventDefault();try{window.classifyImportedAsStaff();}catch(err){alert('تعذر تصنيف الأجهزة: '+(err&&err.message?err.message:err));}}","var target=ev.target&&ev.target.closest?ev.target.closest('#classifyImportedBtn'):null;var yes=ev.target&&ev.target.closest?ev.target.closest('#confirmStaffClassify'):null;var no=ev.target&&ev.target.closest?ev.target.closest('#cancelStaffClassify'):null;if(target){ev.preventDefault();window.classifyImportedAsStaff();}else if(yes){ev.preventDefault();commitStaffClassification();}else if(no){ev.preventDefault();$('staffClassifyModal').style.display='none';}")
if "id=\"staffClassifyModal\"" not in s or "function commitStaffClassification()" not in s or "closest('#confirmStaffClassify')" not in s:
    raise SystemExit("Modal classification flow verification failed")
html.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 43",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.8'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.8: replace JS confirm with in-app confirmation modal and direct delegated confirm/cancel handlers")
