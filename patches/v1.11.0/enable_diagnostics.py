from pathlib import Path
import re
root=Path('source/Hadota-WiFi-Manager-Android')
html=root/'app/src/main/assets/index.html'
h=html.read_text(encoding='utf-8')
bs=chr(92); dollar=chr(36)
h=h.replace(bs+dollar+"{d.connectionStatus",dollar+"{d.connectionStatus")
h=h.replace(bs+dollar+"{d.lastSeenAt",dollar+"{d.lastSeenAt")
h=h.replace("'No device is excluded by a hardcoded IP/MAC. Device groups follow the user's classification.'",'"No device is excluded by a hardcoded IP/MAC. Device groups follow the user\\'s classification."')
old='<section class="card"><div class="card-head"><div class="icon-title"><span class="section-icon">✓</span><h2>ما الذي يعمل حاليًا؟</h2></div></div><div class="row"><span>حفظ الإعدادات محليًا</span><b class="good">جاهز</b></div><div class="row"><span>اختبار الوصول للراوتر</span><b class="warn">بانتظار التجربة على الشبكة</b></div><div class="row"><span>قراءة الأجهزة والتحكم بالسرعة والحظر</span><b class="warn">غير مفعّل بعد</b></div><p class="small">منع كل أنواع التنزيل مع السماح بالبث ليس مضمونًا من هذا الموديل قبل فحص إصدار البرنامج الثابت وإمكانات التحكم. إذا لم يدعم الراوتر ذلك، سنحتاج جهاز تحكم شبكي إضافي. لا تغيّر هذه النسخة إعدادات الراوتر.</p></section>'
new='<section class="card" id="capabilityCard"><div class="card-head"><div class="icon-title"><span class="section-icon">✓</span><h2>اختبار خصائص الراوتر</h2></div><span class="pill">فحص فعلي</span></div><div class="row"><span>حفظ الإعدادات محليًا</span><b class="good">جاهز</b></div><div class="row"><span>اختبار الاتصال بالراوتر</span><b class="warn" id="capReach">لم يُختبر</b></div><div class="row"><span>قراءة الأجهزة المتصلة</span><b class="warn" id="capClients">بانتظار فحص الراوتر</b></div><div class="row"><span>واجهة MAC Filter</span><b class="warn" id="capMac">لم يتم التحقق</b></div><div class="row"><span>واجهة QoS / Bandwidth</span><b class="warn" id="capQos">لم يتم التحقق</b></div><div class="result muted" id="capabilityReport">افتح لوحة الراوتر وسجّل الدخول ثم شغّل «فحص بيانات الراوتر». لن نعتبر أي خاصية فعالة قبل ظهور دليل من واجهة الراوتر.</div><p class="small">وجود QoS في مواصفات H188A لا يثبت أن إصدار البرنامج الثابت يتيح تحديد سرعة مستقلة لكل جهاز. الفحص يحدد ما تعرضه واجهة جهازك، ولا يغيّر أي إعداد دون تأكيد.</p></section>'
if old in h: h=h.replace(old,new)
elif 'id="capabilityCard"' not in h: raise SystemExit('status card anchor missing')
h=h.replace('نسخة تطوير 1.9.0:', 'نسخة تطوير 1.11.0:')
h=h.replace('الفحص الحالي للقراءة فقط؛ تسجيل الدخول وقراءة الأجهزة وتطبيق حدود السرعة غير مفعّلة حتى التحقق من واجهة الإدارة وصلاحيات الراوتر.', 'تسجل الدخول يدويًا داخل لوحة الراوتر، ثم تفحص الصفحات والخصائص المتاحة وتستورد الأجهزة المكتشفة. لا تُطبّق حدود السرعة أو الحظر إلا بعد التحقق من دعمها في إصدار البرنامج الثابت.')
anchor="function routerInspectResult(msg){$('inspectResult').textContent=msg}\n"
insert="""function routerInspectResult(msg){$('inspectResult').textContent=msg}
function routerReportResult(raw){
 try{
  const r=typeof raw==='string'?JSON.parse(raw):raw||{}, pages=Array.isArray(r.pages)?r.pages:[], devices=Array.isArray(r.devices)?r.devices:[];
  const evidence=pages.map(p=>[p.url,p.title,p.text,JSON.stringify(p.forms||[]),JSON.stringify(p.fields||[]),JSON.stringify(p.buttons||[])].join(' ')).join(' ');
  const mac=/mac.?filter|access.?control.?rule|black.?list|white.?list/i.test(evidence);
  const qos=/\\bqos\\b|bandwidth|traffic.?management|queue.?config|rate.?limit/i.test(evidence);
  $('capReach').textContent=r.currentPageAuthenticated?'واجهة الراوتر متاحة':'صفحة تسجيل الدخول';$('capReach').className=r.currentPageAuthenticated?'good':'warn';
  $('capClients').textContent=devices.length?devices.length+' جهاز مكتشف':'لم تُكتشف أجهزة';$('capClients').className=devices.length?'good':'warn';
  $('capMac').textContent=mac?'تم العثور على صفحة/حقول محتملة':'لم يُعثر على دليل';$('capMac').className=mac?'good':'warn';
  $('capQos').textContent=qos?'تم العثور على صفحة/حقول محتملة':'لم يُعثر على دليل';$('capQos').className=qos?'good':'warn';
  const titles=pages.map(p=>p.title||p.url||'صفحة غير معنونة').filter(Boolean).slice(0,12);
  $('capabilityReport').textContent='نتيجة الفحص: '+pages.length+' صفحة، '+devices.length+' جهاز. '+(r.currentTitle||'')+'\\n'+(titles.length?'الصفحات: '+titles.join(' • '):'لم تُجمع أسماء صفحات.')+'\\n'+(mac?'تم رصد مؤشرات MAC Filter. ':'لا يوجد إثبات كافٍ لـ MAC Filter. ')+(qos?'تم رصد مؤشرات QoS/Bandwidth. ':'لا يوجد إثبات كافٍ لـ QoS/Bandwidth. ')+'هذه مؤشرات اكتشاف وليست إثباتًا لتطبيق التغيير.';
 }catch(e){$('capabilityReport').textContent='تعذر تحليل تقرير الراوتر: '+e.message}
}
"""
if anchor in h: h=h.replace(anchor,insert)
elif 'function routerReportResult(raw)' not in h: raise SystemExit('report parser anchor missing')
html.write_text(h,encoding='utf-8')
router=root/'app/src/main/java/com/hadota/wifimanager/RouterActivity.java'
s=router.read_text(encoding='utf-8')
if 'automaticScanStarted' in s:
 start=s.index('                view.evaluateJavascript("(function(){if(!document.getElementById(\'hadotaScanBtn\'))')
 end=s.index('\n            }\n            @Override public void onReceivedSslError',start)
 newblock='''                view.evaluateJavascript("(function(){if(!document.getElementById('hadotaScanBtn')){var x=document.createElement('button');x.id='hadotaScanBtn';x.textContent='فحص بيانات الراوتر';x.style='position:fixed;z-index:2147483647;top:8px;right:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';x.onclick=function(){if(x.dataset.busy==='1')return;x.dataset.busy='1';x.textContent='جارٍ فحص الصفحات...';x.disabled=true;RouterBridge.scanAll()};document.body.appendChild(x)}if(!document.getElementById('hadotaReturnBtn')){var b=document.createElement('button');b.id='hadotaReturnBtn';b.textContent='رجوع للتطبيق';b.style='position:fixed;z-index:2147483647;top:58px;right:8px;padding:12px;background:#d9b36a;color:#17120a;border:2px solid white;border-radius:10px;font-weight:bold';b.onclick=function(){b.disabled=true;b.textContent='جارٍ الرجوع...';RouterBridge.exitToApp()};document.body.appendChild(b)}return true})()", null);'''
 s=s[:start]+newblock+s[end:]
s=s.replace('    private boolean automaticScanStarted = false;','    private boolean triedHttpFallback = false;')
if 'import android.webkit.WebResourceRequest;' not in s:
 s=s.replace('import android.webkit.WebViewClient;','import android.webkit.WebViewClient;\nimport android.webkit.WebResourceRequest;\nimport android.webkit.WebResourceError;')
needle='            @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {'
replacement='''            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request != null && request.isForMainFrame() && !triedHttpFallback &&
                    request.getUrl() != null && "https".equalsIgnoreCase(request.getUrl().getScheme())) {
                    triedHttpFallback = true;
                    view.loadUrl("http://" + gateway + "/");
                    return;
                }
                super.onReceivedError(view, request, error);
            }
'''+needle
if needle in s and 'onReceivedError(WebView view, WebResourceRequest request' not in s: s=s.replace(needle,replacement,1)
old="pages.push({url,status,title:d.title,forms:[...d.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)}))});"
new="pages.push({url,status,title:d.title,text:(d.body?.innerText||'').slice(0,5000),forms:[...d.forms].map(f=>({action:f.action,method:f.method,fields:[...f.elements].map(e=>e.name||e.id).filter(Boolean)})),fields:[...d.querySelectorAll('input,select,textarea')].map(e=>({tag:e.tagName,type:e.type||'',name:e.name||e.id||'',label:(e.labels&&[...e.labels].map(x=>x.innerText).join(' '))||e.getAttribute('aria-label')||e.placeholder||'',options:e.tagName==='SELECT'?[...e.options].map(o=>o.text).slice(0,30):[]})),buttons:[...d.querySelectorAll('button,input[type=button],input[type=submit]')].map(e=>(e.innerText||e.value||'').trim()).filter(Boolean).slice(0,50)});"
if old in s: s=s.replace(old,new)
elif "fields:[...d.querySelectorAll('input,select,textarea')]" not in s: raise SystemExit('page inspection anchor missing')
old='''                            if (found == null || found.length() == 0) {
                                org.json.JSONArray scannedPages = scan.optJSONArray("pages");
                                int pageCount = scannedPages == null ? 0 : scannedPages.length();
                                String note = "لم يتم العثور على أجهزة في الصفحة الحالية. افتح من قائمة الراوتر صفحة WLAN Client Status أو LAN Client Status، ثم اضغط «فحص بيانات الراوتر». تم فحص " + pageCount + " صفحة دون تغيير إعدادات الراوتر.";
                                router.evaluateJavascript("(function(){var id='hadotaScanHint',n=document.getElementById(id);if(!n){n=document.createElement('div');n.id=id;n.style='position:fixed;z-index:2147483647;top:112px;right:8px;left:8px;padding:14px;background:#152536;color:#f4dfad;border:2px solid #d9b36a;border-radius:12px;font:bold 15px sans-serif;line-height:1.7;direction:rtl;box-shadow:0 4px 20px #000';document.body.appendChild(n)}n.textContent=" + org.json.JSONObject.quote(note) + ";return true})()", null);
                                return;
                            }
                        } catch (Exception ignored) { result.putExtra("router_devices", "[]"); }
                        setResult(RESULT_OK, result);
                        finish();'''
new='''                            if (found == null) result.putExtra("router_devices", "[]");
                            if (found == null || found.length() == 0) {
                                org.json.JSONArray scannedPages = scan.optJSONArray("pages");
                                int pageCount = scannedPages == null ? 0 : scannedPages.length();
                                result.putExtra("router_scan_note", "لم تُكتشف أجهزة في الفحص الحالي. تم فحص " + pageCount + " صفحة. افتح WLAN Client Status أو LAN Client Status ثم أعد الفحص.");
                            }
                        } catch (Exception ignored) { result.putExtra("router_devices", "[]"); }
                        setResult(RESULT_OK, result);
                        finish();'''
if old in s: s=s.replace(old,new)
elif 'router_scan_note' not in s: raise SystemExit('empty scan handling anchor missing')
router.write_text(s,encoding='utf-8')
main=root/'app/src/main/java/com/hadota/wifimanager/MainActivity.java'
m=main.read_text(encoding='utf-8')
old='''            if (report != null && web != null) {
                web.evaluateJavascript("routerInspectResult(" + org.json.JSONObject.quote("تقرير فحص الراوتر: " + report) + ")", null);
            }'''
new='''            if (report != null && web != null) {
                web.evaluateJavascript("routerReportResult(" + org.json.JSONObject.quote(report) + ")", null);
                String note = data.getStringExtra("router_scan_note");
                if (note != null) web.evaluateJavascript("routerInspectResult(" + org.json.JSONObject.quote(note) + ")", null);
            }'''
if old in m: m=m.replace(old,new)
elif 'routerReportResult(' not in m: raise SystemExit('main report handler anchor missing')
m=m.replace('''            if (devices.length() == 0) devices = parseRouterClients(text == null ? "" : text);
            web.evaluateJavascript("showLiveDevices(" + devices.toString() + ")", null);''','''            if (devices.length() == 0) devices = parseRouterClients(text == null ? "" : text);
            if (devices.length() > 0) web.evaluateJavascript("showLiveDevices(" + devices.toString() + ")", null);''',1)
main.write_text(m,encoding='utf-8')
g=root/'app/build.gradle'
v=g.read_text(encoding='utf-8')
v,n1=re.subn(r'versionCode\s+\d+','versionCode 69',v,count=1)
v,n2=re.subn(r"versionName\s+'[^']+'", "versionName '1.11.0'",v,count=1)
if n1!=1 or n2!=1: raise SystemExit('version metadata update failed')
g.write_text(v,encoding='utf-8')
print('v1.11.0 diagnostic and router-scan fixes applied')
