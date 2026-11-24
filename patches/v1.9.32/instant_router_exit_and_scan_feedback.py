from pathlib import Path
import re

root=Path("source/Hadota-WiFi-Manager-Android")
router=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s=router.read_text(encoding="utf-8")

# Add a dedicated immediate exit action; never make the Back control wait for DOM parsing.
if "public void exitToApp()" not in s:
    anchor='''        @JavascriptInterface public void capture() {'''
    if anchor not in s: raise SystemExit("capture method anchor missing")
    s=s.replace(anchor,'''        @JavascriptInterface public void exitToApp() {
            runOnUiThread(() -> {
                setResult(RESULT_CANCELED);
                finish();
            });
        }

        @JavascriptInterface public void capture() {''',1)

old="b.textContent='رجوع إلى Hadota WiFi Manager';"
new="b.textContent='رجوع للتطبيق';"
if old not in s: raise SystemExit("return button label missing")
s=s.replace(old,new,1)
old="b.onclick=function(){RouterBridge.capture()};"
new="b.onclick=function(){b.disabled=true;b.textContent='جارٍ الرجوع...';RouterBridge.exitToApp()};"
if old not in s: raise SystemExit("return button action missing")
s=s.replace(old,new,1)

# Make scan button show immediate progress and prevent repeated long scans.
old="x.onclick=function(){RouterBridge.scanAll()};"
new="x.onclick=function(){if(x.dataset.busy==='1')return;x.dataset.busy='1';x.textContent='جارٍ فحص الصفحات...';x.disabled=true;RouterBridge.scanAll()};"
if old not in s: raise SystemExit("scan button action missing")
s=s.replace(old,new,1)

# Ensure scan failures do not leave a disabled button forever; callback is handled on the page.
# Inject a safe JS helper and invoke it for the returned report path.
anchor='''                    String report = value == null ? "null" : value;
                    if (router == null) return;'''
replace='''                    String report = value == null ? "null" : value;
                    if (router == null) return;
                    router.evaluateJavascript("(function(){var x=document.getElementById('hadotaScanBtn');if(x){x.disabled=false;x.dataset.busy='0';x.textContent='فحص بيانات الراوتر'}return true})()", null);'''
if anchor not in s: raise SystemExit("scan callback anchor missing")
s=s.replace(anchor,replace,1)

router.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 67",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.32'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.32: dedicated instant return-to-app action; scan button progress/anti-double-tap and re-enable")
