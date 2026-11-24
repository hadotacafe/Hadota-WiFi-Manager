from pathlib import Path
import re

root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")

start=s.index("function showLiveDevices(devices,rawPayload)")
end=s.index("\nfunction routerInspectResult",start)
replacement=r'''function showLiveDevices(devices,rawPayload){
 if(!Array.isArray(devices)||!devices.length){
  $('inspectResult').textContent='لم يتم استخراج أجهزة من الصفحة الحالية. افتح صفحة WLAN Client Status وLAN Client Status ثم أعد الاستيراد.';
  return;
 }
 const old=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
 const normMac=d=>String(d.mac||'').replace(/-/g,':').toLowerCase().trim();
 const normIp=d=>String(d.ip||'').trim();
 const byMac=new Map(),byIp=new Map(),all=[];
 old.forEach(d=>{
  const c={...d};all.push(c);
  if(normMac(c))byMac.set(normMac(c),c);
  if(normIp(c))byIp.set(normIp(c),c);
 });
 const seenAt=new Date().toISOString(),liveKeys=[];
 devices.forEach(d=>{
  const mac=normMac(d),ip=normIp(d);
  if(!mac&&!ip)return;
  // Match by either MAC or IP to avoid duplicate entries when a router adds MAC data later.
  let prev=(mac&&byMac.get(mac))||(ip&&byIp.get(ip));
  if(!prev){
   prev={...d,group:d.group||'unassigned'};
   all.push(prev);
  }else{
   Object.assign(prev,d);
   // Preserve the user's existing classification and display name.
   if(!prev.group)prev.group='unassigned';
  }
  const owner=(mac==='12:b1:0d:bd:b3:4a'||ip==='192.168.1.186');
  if(owner)prev.group='owner';
  prev.name=prev.name||d.name||'جهاز متصل';
  prev.connectionStatus='connected';
  prev.lastSeenAt=seenAt;
  if(mac)byMac.set(mac,prev);
  if(ip)byIp.set(ip,prev);
  liveKeys.push(mac?'mac:'+mac:'ip:'+ip);
 });
 const liveSet=new Set(liveKeys);
 all.forEach(d=>{
  const mac=normMac(d),ip=normIp(d),k=mac?'mac:'+mac:'ip:'+ip;
  d.connectionStatus=liveSet.has(k)||(ip&&devices.some(x=>normIp(x)===ip))?'connected':'disconnected';
 });
 localStorage.setItem('hadotaInventory',JSON.stringify(all));
 localStorage.setItem('hadotaLastImportedKeys',JSON.stringify(liveKeys));
 renderInventory();
 $('classifyImportedBtn').style.display='block';
 const online=all.filter(d=>d.connectionStatus==='connected').length;
 const offline=all.filter(d=>d.group==='staff'&&d.connectionStatus!=='connected').length;
 $('inspectResult').textContent='تم تحديث '+online+' جهاز متصل. تم الاحتفاظ بالأجهزة المحفوظة غير المتصلة ('+offline+' موظف) دون حذفها من القائمة.';
}
window.classifyImportedAsStaff = function(){
 try{
  const keys=JSON.parse(localStorage.getItem('hadotaLastImportedKeys')||'[]');
  const a=JSON.parse(localStorage.getItem('hadotaInventory')||'null')||inventorySeed;
  const normMac=d=>String(d.mac||'').replace(/-/g,':').toLowerCase().trim();
  const normIp=d=>String(d.ip||'').trim();
  const keySet=new Set(keys.map(k=>String(k).replace(/-/g,':').toLowerCase()));
  const matches=a.filter(d=>{
   if(d.group==='owner')return false;
   const mk=normMac(d),ik=normIp(d);
   return (mk&&keySet.has('mac:'+mk))||(ik&&keySet.has('ip:'+ik))||d.connectionStatus==='connected';
  });
  if(!matches.length){
   $('inspectResult').textContent='لم أجد أجهزة من آخر استيراد للتصنيف. أعد استيراد الأجهزة أولًا.';
   return;
  }
  const already=a.filter(d=>d.group==='staff').length;
  const toAdd=matches.filter(d=>d.group!=='staff');
  const slots=Math.max(0,14-already);
  const selected=toAdd.slice(0,slots);
  selected.forEach(d=>d.group='staff');
  localStorage.setItem('hadotaInventory',JSON.stringify(a));
  renderInventory();
  $('classifyImportedBtn').style.display='none';
  const skipped=toAdd.length-selected.length;
  $('inspectResult').textContent='تم تصنيف '+selected.length+' جهازًا جديدًا كموظفين. إجمالي الموظفين: '+(already+selected.length)+' من 14.'+(skipped?' تم ترك '+skipped+' جهازًا دون تصنيف حتى لا نتجاوز الحد.':'');
 }catch(e){
  $('inspectResult').textContent='تعذر التصنيف: '+(e&&e.message?e.message:'خطأ غير معروف');
 }
};'''
s=s[:start]+replacement+s[end:]
html.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
v=g.read_text(encoding="utf-8")
v,a=re.subn(r"versionCode\s+\d+","versionCode 65",v,count=1)
v,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.30'",v,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
g.write_text(v,encoding="utf-8")
print("v1.9.30: deduplicate live inventory by IP/MAC and classify only available employee slots")
