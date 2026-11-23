from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
html=root/"app/src/main/assets/index.html"
s=html.read_text(encoding="utf-8")
old="function testRouter(){ $('testResult').textContent='جارٍ فحص الاتصال...';$('routerState').textContent='جارٍ الاختبار';if(window.AndroidBridge){AndroidBridge.testRouter()}else{$('testResult').textContent='ميزة الاختبار متاحة داخل تطبيق Android فقط.'}}"
new="""let routerTestTimer=null,routerTestSeq=0;
function testRouter(){
 const seq=++routerTestSeq;
 $('testResult').textContent='جارٍ فحص الاتصال...';
 $('routerState').textContent='جارٍ الاختبار';
 $('dot').style.background='#e6bd69';
 if(routerTestTimer)clearTimeout(routerTestTimer);
 routerTestTimer=setTimeout(function(){
  if(seq!==routerTestSeq)return;
  $('routerState').textContent='لم يصل رد الاختبار';
  $('dot').style.background='#ff7777';
  $('testResult').textContent='انتهت مهلة الاختبار داخل التطبيق دون استلام رد. لم يتم تغيير إعدادات الراوتر. أعد المحاولة أو افتح لوحة الراوتر.';
 },8000);
 try {
  if(window.AndroidBridge){AndroidBridge.testRouter();}
  else {
   clearTimeout(routerTestTimer);
   $('routerState').textContent='غير متاح';
   $('testResult').textContent='ميزة الاختبار متاحة داخل تطبيق Android فقط.';
  }
 } catch(e) {
  clearTimeout(routerTestTimer);
  $('routerState').textContent='فشل بدء الاختبار';
  $('dot').style.background='#ff7777';
  $('testResult').textContent='تعذر بدء الاختبار: '+(e&&e.message?e.message:String(e));
 }
}"""
if old not in s: raise SystemExit("testRouter JS function not found")
s=s.replace(old,new,1)
old2="function routerResult(ok,msg){$('routerState').textContent=ok?'الراوتر استجاب':'تعذر تأكيد الاتصال';$('dot').style.background=ok?'#51c99a':'#ff7777';$('testResult').innerHTML=(ok?'<span class=\"good\">نجح الوصول: </span>':'<span class=\"bad\">لم ينجح الوصول: </span>')+msg.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\n','<br>')}"
new2="""function routerResult(ok,msg){
 if(routerTestTimer){clearTimeout(routerTestTimer);routerTestTimer=null;}
 routerTestSeq++;
 $('routerState').textContent=ok?'الراوتر استجاب':'تعذر تأكيد الاتصال';
 $('dot').style.background=ok?'#51c99a':'#ff7777';
 $('testResult').innerHTML=(ok?'<span class="good">نجح الوصول: </span>':'<span class="bad">لم ينجح الوصول: </span>')+String(msg||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\n','<br>');
}"""
if old2 not in s: raise SystemExit("routerResult JS function not found")
s=s.replace(old2,new2,1)
html.write_text(s,encoding="utf-8")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
j=main.read_text(encoding="utf-8")
# Remove over-restrictive URL prefix test; still guard lifecycle and bridge availability.
j=j.replace('if (!isFinishing() && !isDestroyed() && web != null &&\n                                    web.getUrl() != null && web.getUrl().startsWith("file:///android_asset/index.html")) {',
'''if (!isFinishing() && !isDestroyed() && web != null &&
                                    web.getUrl() != null && web.getUrl().contains("android_asset/index.html")) {''',1)
main.write_text(j,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 49",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.14'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.14: 8-second JS watchdog guarantees visible completion; clearer callback guard; test result clears watchdog")
