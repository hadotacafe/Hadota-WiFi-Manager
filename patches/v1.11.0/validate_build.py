from pathlib import Path
import re,subprocess,sys
root=Path('source/Hadota-WiFi-Manager-Android')
h=(root/'app/src/main/assets/index.html').read_text(encoding='utf-8')
r=(root/'app/src/main/java/com/hadota/wifimanager/RouterActivity.java').read_text(encoding='utf-8')
m=(root/'app/src/main/java/com/hadota/wifimanager/MainActivity.java').read_text(encoding='utf-8')
g=(root/'app/build.gradle').read_text(encoding='utf-8')
checks={
'Android version 1.11.0':"versionName '1.11.0'" in g and 'versionCode 69' in g,
'Router report parser wired':'function routerReportResult(raw)' in h and 'routerReportResult(' in m,
'No automatic scan before login':'automaticScanStarted' not in r,
'HTTP fallback for local router':'triedHttpFallback' in r and 'http://" + gateway + "/"' in r,
'Scan reports empty inventory':'router_scan_note' in r,
'Router page fields captured':"fields:[...d.querySelectorAll('input,select,textarea')]" in r,
'No fake device seed':'const inventorySeed=[];' in h,
'Inventory status template active':(chr(92)+chr(36)+'{d.connectionStatus') not in h and (chr(36)+'{d.connectionStatus===') in h,
'MAC/QoS detection not misrepresented':'هذه مؤشرات اكتشاف وليست إثباتًا لتطبيق التغيير.' in h,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL')+' — '+k)
if not all(checks.values()): sys.exit(1)
for i,src in enumerate(re.findall(r'<script>(.*?)</script>',h,re.S)):
 p=Path(f'/tmp/hadota-v111-{i}.js');p.write_text(src,encoding='utf-8')
 x=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
 if x.returncode: print(x.stderr);sys.exit(1)
print('PASS — embedded JavaScript syntax')
