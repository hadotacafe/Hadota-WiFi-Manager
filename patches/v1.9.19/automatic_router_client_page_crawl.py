from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

start = s.find('router.evaluateJavascript("(async function(){')
end_marker = '})()", value -> {'
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate router scan JavaScript")

js = r"""(async function(){
const base=location.origin,seen=new Set(),todo=[],pages=[],endpoints=new Set(),assets=new Set(),devices=[],deviceKeys=new Set();
const rx=/(device|client|wlan|wireless|dhcp|lan|host|mac|qos|queue|traffic|bandwidth|speed|filter|acl|status|network|arp|nat|firewall)/i;
function add(v,set){try{const u=new URL(v,location.href);if(u.origin===base&&!set.has(u.href))set.add(u.href)}catch(e){}}
function collectPaths(text){for(const m of text.matchAll(/["']((?:\/|\.\/)[^"'\s]{1,220})["']/g)){if(rx.test(m[1]))add(m[1],todo)}}
function addRow(cells,headers,url,title){
 const vals=cells.map(v=>(v||'').replace(/\s+/g,' ').trim()),joined=vals.join(' | ');
 const ipm=joined.match(/(?:^|[^0-9])((?:192\.168|10|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3})(?:$|[^0-9])/);
 if(!ipm)return;
 const macm=joined.match(/\b([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})\b/i);
 const ip=ipm[1],mac=macm?macm[1].replace(/-/g,':').toLowerCase():'',hs=headers.map(x=>(x||'').toLowerCase());
 let name='';
 for(let i=0;i<vals.length;i++)if(/host|device|client.?name|hostname|اسم|جهاز/.test(hs[i]||'')&&vals[i]&&!vals[i].includes(ip)){name=vals[i];break}
 if(!name)name=vals.find(v=>v&&!v.includes(ip)&&!(/^[0-9a-f]{2}(?:[:-][0-9a-f]{2}){5}$/i.test(v))&&!/^(online|connected|active|wlan|lan|yes|no|ip address|mac address|host name|device name)$/i.test(v))||'جهاز متصل';
 const key=mac||ip;
 if(!deviceKeys.has(key)){deviceKeys.add(key);devices.push({name,ip,mac,source:/lan/i.test(url+' '+title)?'LAN':'WLAN',group:'unassigned'})}
}
function inspect(url,html,status){
 const d=new DOMParser().parseFromString(html,'text/html');
 pages.push({url,status,title:d.title,forms:[...d.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)}))});
 [...d.querySelectorAll('table')].forEach(t=>{
  const trs=[...t.querySelectorAll('tr')];if(!trs.length)return;
  const first=[...trs[0].querySelectorAll('th,td')].map(c=>c.innerText||c.textContent||'');
  const hasHead=trs[0].querySelectorAll('th').length>0||first.some(v=>/ip.?address|mac.?address|host.?name|device.?name|client/i.test(v));
  const headers=hasHead?first:[];
  trs.slice(hasHead?1:0).forEach(r=>addRow([...r.querySelectorAll('th,td')].map(c=>c.innerText||c.textContent||''),headers,url,d.title));
 });
 for(const line of (d.body?.innerText||'').split('\n'))addRow([line],[],url,d.title);
 [...d.querySelectorAll('a[href]')].forEach(a=>{add(a.href,todo);if(rx.test(a.href)||rx.test(a.textContent||''))add(a.href,endpoints)});
 [...d.querySelectorAll('[onclick]')].forEach(el=>collectPaths(el.getAttribute('onclick')||''));
 [...d.querySelectorAll('form[action]')].forEach(f=>{add(f.action,todo);add(f.action,endpoints)});
 [...d.querySelectorAll('script[src]')].forEach(x=>add(x.src,assets));
 [...d.querySelectorAll('script:not([src])')].forEach(x=>collectPaths(x.textContent||''));
 collectPaths(html);
}
const visibleText=(document.body?.innerText||'').slice(0,18000);
const visibleTables=[...document.querySelectorAll('table')].slice(0,30).map(t=>[...t.querySelectorAll('tr')].map(r=>[...r.querySelectorAll('th,td')].map(c=>(c.innerText||'').trim()).filter(Boolean)).filter(r=>r.length));
inspect(location.href,document.documentElement?.outerHTML||'',200);
seen.add(location.href);
while(todo.length&&pages.length<80){
 const u=todo.shift();if(seen.has(u))continue;seen.add(u);
 try{const r=await fetch(u,{credentials:'include',redirect:'follow',cache:'no-store'});inspect(r.url||u,await r.text(),r.status)}
 catch(e){pages.push({url:u,error:String(e)})}
}
for(const u of [...assets].slice(0,35)){
 try{const r=await fetch(u,{credentials:'include',redirect:'follow',cache:'no-store'});collectPaths(await r.text())}catch(e){}
}
return JSON.stringify({origin:base,currentUrl:location.href,currentTitle:document.title,currentPageAuthenticated:!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]'),visibleText,visibleTables,scannedAt:new Date().toISOString(),pages,scriptFiles:[...assets],candidateEndpoints:[...endpoints],devices});
})()""";

java_string = '"' + js.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
s = s[:start] + 'router.evaluateJavascript(' + java_string + ', value -> {' + s[end + len(end_marker):]
s = s.replace('versionCode 53', 'versionCode 54')
s = s.replace("versionName '1.9.18'", "versionName '1.9.19'")
router.write_text(s, encoding="utf-8")
print("v1.9.19: automatic same-origin router page discovery and per-page client extraction")
