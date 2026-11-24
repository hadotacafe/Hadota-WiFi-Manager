from pathlib import Path
import re
root=Path('source/Hadota-WiFi-Manager-Android')
router=root/'app/src/main/java/com/hadota/wifimanager/RouterActivity.java'
s=router.read_text(encoding='utf-8')
bs=chr(92)
anchor="docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});"+bs+"nseen.add(location.href);"
if anchor not in s: raise SystemExit('Router scan insertion anchor not found')
js=r'''// Expand the firmware's collapsed WLAN/LAN client-status accordions before extraction.
const expanded=[];
function frameDocs(){const list=[document],done=new Set();(function walk(w){try{for(let i=0;i<w.frames.length;i++){const f=w.frames[i];if(done.has(f))continue;done.add(f);try{if(f.document&&f.document.documentElement){list.push(f.document);walk(f)}}catch(e){}}}catch(e){}})(window);return list;}
for(const d of frameDocs()){
 try{
  const candidates=[...d.querySelectorAll('body *')].filter(el=>el.children.length<4&&/^(wlan|lan)\s+client\s+status$/i.test((el.innerText||el.textContent||'').replace(/\s+/g,' ').trim()));
  for(const el of candidates){
   let target=el.closest('a,button,[onclick],[role="button"],summary');
   if(!target){let p=el;for(let n=0;n<3&&p&&!target;n++,p=p.parentElement){if(p.hasAttribute('onclick')||p.getAttribute('role')==='button'||p.tagName==='A'||p.tagName==='BUTTON')target=p;}}
   target=target||el;
   const label=(target.innerText||target.textContent||'').replace(/\s+/g,' ').trim();
   if(!expanded.includes(label)){try{target.click();expanded.push(label)}catch(e){}}
  }
  [...d.querySelectorAll('details:not([open]) > summary')].forEach(x=>{try{x.click()}catch(e){}});
 }catch(e){}
}
if(expanded.length)await new Promise(resolve=>setTimeout(resolve,450));
const expandedDocs=frameDocs();
expandedDocs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});
'''
def java_escape(x):
 return x.replace(bs,bs*2).replace('"',bs+'"').replace(chr(10),bs+'n')
replacement="docs.forEach(d=>{try{inspect(d.location.href,d.documentElement?.outerHTML||'',200)}catch(e){}});"+bs+'n'+java_escape(js)+bs+'nseen.add(location.href);'
s=s.replace(anchor,replacement,1)
router.write_text(s,encoding='utf-8')
html=root/'app/src/main/assets/index.html'
h=html.read_text(encoding='utf-8')
h=h.replace("if(d.group==='owner')return false;",'')
h=h.replace("const owner=(mac==='12:b1:0d:bd:b3:4a'||ip==='192.168.1.186');"+chr(10)+"  if(owner)prev.group='owner';",'')
h=h.replace("const owner=(String(d.mac||'').replace(/-/g,':').toLowerCase()==='12:b1:0d:bd:b3:4a'||d.ip==='192.168.1.186');",'const owner=false;')
start=h.index('const inventorySeed=[')
end=h.index(chr(10)+'function renderInventory()',start)
h=h[:start]+'const inventorySeed=[];'+chr(10)+h[end:]
h=h.replace("if(a.filter(d=>d.group==='staff').length>=14){alert('تم الوصول إلى الحد الأقصى: أجهزة الموظفين');return}",'')
h=h.replace("'Owner device excluded from employee/guest speed policies by IP 192.168.1.186 and MAC 12:b1:0d:bd:b3:4a. MAC is the preferred identity if DHCP changes the IP.'","'No device is excluded by a hardcoded IP/MAC. Device groups follow the user's classification.'")
h=h.replace('<b>14</b><span>حد أجهزة الموظفين</span>','<b>∞</b><span>أجهزة الموظفين</span>')
h=h.replace('id="staffCount" type="number" min="1" max="50" value="14"','id="staffCount" type="number" min="1" value="29"')
h=h.replace('حد أجهزة الموظفين','أجهزة الموظفين')
html.write_text(h,encoding='utf-8')
g=root/'app/build.gradle'
v=g.read_text(encoding='utf-8')
v,n1=re.subn(r'versionCode\s+\d+','versionCode 68',v,count=1)
v,n2=re.subn(r"versionName\s+'[^']+'", "versionName '1.10.0'",v,count=1)
if n1!=1 or n2!=1: raise SystemExit('Could not update app version')
g.write_text(v,encoding='utf-8')
print('v1.10.0: expand ZTE client accordions before extraction; remove invented seed devices and hardcoded owner exclusion; keep unlimited employee roster')
