from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
start=s.index("function showLiveDevices(devices,rawPayload)")
end=s.index("\nwindow.classifyImportedAsStaff",start)
new=r'''function showLiveDevices(devices,rawPayload){
 if(!Array.isArray(devices)||!devices.length){
  $('inspectResult').textContent='لم يتم استخراج أجهزة من الصفحة الحالية. افتح صفحة WLAN Client Status وLAN Client Status ثم أعد الاستيراد.';
  return;
 }
 const old=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 const keyOf=d=>d.mac?'mac:'+String(d.mac).replace(/-/g,':').toLowerCase():'ip:'+String(d.ip||'').trim();
 const byKey=new Map();
 old.forEach(d=>{const k=keyOf(d);if(k&&k!=='ip:')byKey.set(k,{...d});});
 const seenAt=new Date().toISOString(),liveKeys=[];
 devices.forEach(d=>{
  const k=keyOf(d);if(!k||k==='ip:')return;
  const prev=byKey.get(k)||old.find(x=>x.ip&&x.ip===d.ip)||{};
  const owner=(String(d.mac||'').replace(/-/g,':').toLowerCase()==='12:b1:0d:bd:b3:4a'||d.ip==='192.168.1.186');
  byKey.set(k,{
   ...prev,...d,
   name:prev.name&&prev.name!=='جهاز المالك — مستثنى'?prev.name:(d.name||'جهاز متصل'),
   group:owner?'owner':(prev.group||d.group||'unassigned'),
   connectionStatus:'connected',
   lastSeenAt:seenAt
  });
  liveKeys.push(k);
 });
 // Preserve saved staff/owner records that are not online now; never erase the roster on refresh.
 const merged=Array.from(byKey.values()).map(d=>{
  const k=keyOf(d),isLive=liveKeys.includes(k);
  return {...d,connectionStatus:isLive?'connected':'disconnected'};
 });
 localStorage.setItem('hadotaInventory',JSON.stringify(merged));
 localStorage.setItem('hadotaLastImportedKeys',JSON.stringify([...new Set(liveKeys)]));
 renderInventory();
 $('classifyImportedBtn').style.display='block';
 const online=merged.filter(d=>d.connectionStatus==='connected').length;
 const offline=merged.filter(d=>d.group==='staff'&&d.connectionStatus!=='connected').length;
 $('inspectResult').textContent='تم تحديث '+online+' جهاز متصل. تم الاحتفاظ بالأجهزة المحفوظة غير المتصلة ('+offline+' موظف) دون حذفها من القائمة.';
}'''
s=s[:start]+new+s[end:]
html.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
v=g.read_text(encoding="utf-8")
v,a=re.subn(r"versionCode\s+\d+","versionCode 64",v,count=1)
v,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.29'",v,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
g.write_text(v,encoding="utf-8")
print("v1.9.29: merge live clients into saved inventory; preserve offline staff and owner devices; show connection state")
