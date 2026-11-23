from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
html = root / "app/src/main/assets/index.html"
s = html.read_text(encoding="utf-8")

# Add a safe local roster editor. Router status and enforcement remain explicitly unverified.
anchor = '<button class="btn alt" onclick="exportDiagnostics()">تجهيز تقرير التشخيص</button>'
if anchor not in s:
    raise SystemExit("Inventory diagnostics anchor missing")
s = s.replace(anchor, '<div class="row"><b>إدارة أجهزة الموظفين</b><span class="pill" id="staffDeviceCount">0 / 14</span></div><p class="small">تعديل وحفظ بيانات الأجهزة على الهاتف. حالة الاتصال تظهر «غير متحقق» حتى يقرأها التطبيق من الراوتر.</p><button class="btn alt" onclick="addStaffDevice()">إضافة جهاز موظف</button><div id="staffRoster"></div>' + anchor, 1)

old = "function renderInventory(){const saved=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed; $('inventory').innerHTML=saved.map((d,i)=>`<div class=\"device\"><div class=\"row\"><b>${escapeHtml(d.name)}</b><span class=\"pill\">${d.source}</span></div><div dir=\"ltr\" class=\"muted\">${d.ip}</div>${d.mac?`<div dir=\"ltr\" class=\"small\">MAC: ${escapeHtml(d.mac)}</div>`:''}<label class=\"small\">التصنيف</label><select data-i=\"${i}\" onchange=\"setInventoryGroup(${i},this.value)\" style=\"width:100%;padding:10px;border-radius:8px;background:#0b1017;color:white;border:1px solid var(--line)\"><option value=\"staff\" ${d.group==='staff'?'selected':''}>موظف</option><option value=\"guest\" ${d.group==='guest'?'selected':''}>زبون</option><option value=\"owner\" ${d.group==='owner'?'selected':''}>استثناء — جهاز المالك</option><option value=\"unassigned\" ${d.group==='unassigned'?'selected':''}>غير مصنف</option></select></div>`).join('')}"
new = """function renderInventory(){
 const saved=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 $('inventory').innerHTML=saved.map((d,i)=>`<div class="device"><div class="row"><b>${escapeHtml(d.name)}</b><span class="pill">${d.source||'محلي'}</span></div><div dir="ltr" class="muted">${escapeHtml(d.ip||'بدون IP')}</div>${d.mac?`<div dir="ltr" class="small">MAC: ${escapeHtml(d.mac)}</div>`:''}<label class="small">التصنيف</label><select onchange="setInventoryGroup(${i},this.value)" style="width:100%;padding:10px;border-radius:8px;background:#0b1017;color:white;border:1px solid var(--line)"><option value="staff" ${d.group==='staff'?'selected':''}>موظف</option><option value="guest" ${d.group==='guest'?'selected':''}>زبون</option><option value="owner" ${d.group==='owner'?'selected':''}>استثناء — جهاز المالك</option><option value="unassigned" ${d.group==='unassigned'?'selected':''}>غير مصنف</option></select><div class="small warn">حالة الاتصال: غير متحقق من الراوتر</div></div>`).join('');
 const staff=saved.filter(d=>d.group==='staff');
 $('staffDeviceCount').textContent=staff.length+' / 14';
 $('staffRoster').innerHTML=staff.map((d,i)=>`<div class="device"><b>${escapeHtml(d.name)}</b><div class="small" dir="ltr">${escapeHtml(d.ip||'IP غير مسجل')} ${d.mac?' · '+escapeHtml(d.mac):''}</div><div class="small warn">غير متحقق من الاتصال · التحكم الفعلي غير مفعّل</div><button class="btn alt" onclick="editStaffDevice(${saved.indexOf(d)})">تعديل البيانات</button></div>`).join('')||'<p class="small">لا توجد أجهزة موظفين مسجلة.</p>';
}
function addStaffDevice(){
 const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 if(a.filter(d=>d.group==='staff').length>=14){alert('تم الوصول إلى الحد الأقصى: 14 جهاز موظف');return}
 const name=prompt('اسم الجهاز:');if(!name||!name.trim())return;
 const ip=prompt('عنوان IP للجهاز:');if(!ip||!/^\\d{1,3}(?:\\.\\d{1,3}){3}$/.test(ip.trim())){alert('أدخل عنوان IPv4 صحيحًا');return}
 const mac=prompt('عنوان MAC (اختياري):')||'';
 a.push({name:name.trim(),ip:ip.trim(),mac:mac.trim(),group:'staff',source:'Manual'});
 localStorage.setItem('hadotaInventory',JSON.stringify(a));renderInventory();
}
function editStaffDevice(i){
 const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed,d=a[i];if(!d)return;
 const name=prompt('اسم الجهاز:',d.name||'');if(name===null)return;
 const ip=prompt('عنوان IP:',d.ip||'');if(ip===null)return;
 const mac=prompt('عنوان MAC:',d.mac||'');if(mac===null)return;
 if(ip.trim()&&!/^\\d{1,3}(?:\\.\\d{1,3}){3}$/.test(ip.trim())){alert('عنوان IP غير صحيح');return}
 d.name=name.trim()||'جهاز موظف';d.ip=ip.trim();d.mac=mac.trim();localStorage.setItem('hadotaInventory',JSON.stringify(a));renderInventory();
}"""
if old not in s:
    raise SystemExit("renderInventory anchor not found")
s = s.replace(old, new, 1)
# Keep existing data; only bump app version.
html.write_text(s, encoding="utf-8")
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, n1 = re.subn(r"versionCode\\s+\\d+", "versionCode 33", g, count=1)
g, n2 = re.subn(r"versionName\\s+'[^']+'", "versionName '1.8.3'", g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update v1.8.3 app version")
gradle.write_text(g, encoding="utf-8")
print("Added local 14-device staff roster editor; no router enforcement is claimed. Version 1.8.3")
