from pathlib import Path
import re

root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")

s=s.replace("14 جهاز موظف","أجهزة الموظفين")
s=s.replace("0 / 14","0 جهاز")
s=s.replace("تم الوصول إلى الحد الأقصى: 14 جهاز موظف","")
s=s.replace("if(a.filter(d=>d.group==='staff').length>=14){alert('');return}","")

old="""  const already=a.filter(d=>d.group==='staff').length;
  const toAdd=matches.filter(d=>d.group!=='staff');
  const slots=Math.max(0,14-already);
  const selected=toAdd.slice(0,slots);
  selected.forEach(d=>d.group='staff');
  localStorage.setItem('hadotaInventory',JSON.stringify(a));
  renderInventory();
  $('classifyImportedBtn').style.display='none';
  const skipped=toAdd.length-selected.length;
  $('inspectResult').textContent='تم تصنيف '+selected.length+' جهازًا جديدًا كموظفين. إجمالي الموظفين: '+(already+selected.length)+' من 14.'+(skipped?' تم ترك '+skipped+' جهازًا دون تصنيف حتى لا نتجاوز الحد.':'');"""
new="""  const toAdd=matches.filter(d=>d.group!=='staff');
  toAdd.forEach(d=>d.group='staff');
  localStorage.setItem('hadotaInventory',JSON.stringify(a));
  renderInventory();
  $('classifyImportedBtn').style.display='none';
  $('inspectResult').textContent='تم تصنيف جميع الأجهزة المستوردة كأجهزة موظفين. إجمالي أجهزة الموظفين: '+a.filter(d=>d.group==='staff').length+'.';"""
if old not in s:
 raise SystemExit("Classification block not found; stopping safely")
s=s.replace(old,new,1)
s=s.replace("staff.length+' / 14'","staff.length+' جهاز'")
s=s.replace("حتى 14 جهازًا","بدون حد ثابت لعدد الأجهزة")
html.write_text(s,encoding="utf-8")

gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,n1=re.subn(r"versionCode\s+\d+","versionCode 66",g,count=1)
g,n2=re.subn(r"versionName\s+'[^']+'","versionName '1.9.31'",g,count=1)
if n1!=1 or n2!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.31: classify all imported devices as employees; remove fixed 14-device limit")
