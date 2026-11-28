from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
html = root / "app/src/main/assets/index.html"
gradle = root / "app/build.gradle"

# Replace the unauthenticated HttpURLConnection script crawl. It cannot share
# Android WebView cookies and therefore only sees the router's HTTP 302 login.
s = main.read_text(encoding="utf-8")
start = s.find("        @JavascriptInterface public void inspectRouterScripts() {")
end = s.find("        private String readLimited(", start)
if start < 0 or end < 0:
    raise SystemExit("inspectRouterScripts block not found")
replacement = """        @JavascriptInterface public void inspectRouterScripts() {
            // Inspect router pages inside RouterActivity's authenticated WebView.
            MainActivity.this.openRouterPanel();
            runOnUiThread(() -> {
                if (web != null) web.evaluateJavascript(
                    "routerScriptsResult(" + org.json.JSONObject.quote(
                        "تم فتح لوحة الراوتر. سجّل الدخول أولًا، ثم اضغط «فحص بيانات الراوتر» داخل الصفحة. الفحص يستخدم جلسة WebView نفسها ولا يرسل بيانات الدخول إلى خدمة خارجية.") + ")", null);
            });
        }

"""
s = s[:start] + replacement + s[end:]
main.write_text(s, encoding="utf-8")

h = html.read_text(encoding="utf-8")
h = h.replace("تحليل ملفات الراوتر (قراءة فقط)", "فحص صفحات الراوتر بعد تسجيل الدخول")
h = h.replace("نسخة تطوير 1.11.0:", "نسخة 1.12.0:")
html.write_text(h, encoding="utf-8")

r = router.read_text(encoding="utf-8")
old_state = "currentPageAuthenticated:!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]'),visibleText"
new_state = "loginDetected:!!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]')||/login|logon|template_token_check/i.test(location.href),currentPageAuthenticated:!document.querySelector('input[type=password],input[name*=pass i],input[id*=pass i]')&&!/login|logon|template_token_check/i.test(location.href),visibleText"
if old_state not in r and new_state not in r:
    raise SystemExit("authentication state anchor not found")
r = r.replace(old_state, new_state)

old = '''                    String report = value == null ? "null" : value;
                    if (router == null) return;
                    router.evaluateJavascript("(function(){var x=document.getElementById('hadotaScanBtn');if(x){x.disabled=false;x.dataset.busy='0';x.textContent='فحص بيانات الراوتر'}return true})()", null);
                    router.evaluateJavascript("(function(){return document.body?document.body.innerText:''})()", bodyValue -> {'''
new = '''                    String report = value == null ? "null" : value;
                    if (router == null) return;
                    try {
                        String decoded = new org.json.JSONArray("[" + report + "]").optString(0, "{}");
                        org.json.JSONObject scanState = new org.json.JSONObject(decoded);
                        if (!scanState.optBoolean("currentPageAuthenticated", false)) {
                            router.evaluateJavascript("(function(){var x=document.getElementById('hadotaScanBtn');if(x){x.disabled=false;x.dataset.busy='0';x.textContent='أعد الفحص بعد تسجيل الدخول'}var n=document.getElementById('hadotaLoginHint');if(!n){n=document.createElement('div');n.id='hadotaLoginHint';n.style='position:fixed;z-index:2147483646;top:112px;right:8px;left:8px;padding:14px;background:#152536;color:#f4dfad;border:2px solid #d9b36a;border-radius:12px;font:bold 15px sans-serif;line-height:1.8;direction:rtl;box-shadow:0 4px 20px #000';document.body.appendChild(n)}n.textContent='الراوتر يعرض صفحة تسجيل الدخول أو لم تُثبت الجلسة بعد. سجّل الدخول من هذه الصفحة، وانتظر ظهور لوحة التحكم، ثم اضغط «أعد الفحص بعد تسجيل الدخول». لم يتم إرسال أي بيانات أو تغيير أي إعداد.';return true})()", null);
                            return;
                        }
                    } catch (Exception ignored) {}
                    router.evaluateJavascript("(function(){var x=document.getElementById('hadotaScanBtn');if(x){x.disabled=false;x.dataset.busy='0';x.textContent='فحص بيانات الراوتر'}var n=document.getElementById('hadotaLoginHint');if(n)n.remove();return true})()", null);
                    router.evaluateJavascript("(function(){return document.body?document.body.innerText:''})()", bodyValue -> {'''
if old not in r and new not in r:
    raise SystemExit("scan callback anchor not found")
r = r.replace(old, new)
router.write_text(r, encoding="utf-8")

g = gradle.read_text(encoding="utf-8")
if "versionCode 69" not in g or "versionName '1.11.0'" not in g:
    raise SystemExit("Unexpected base app version")
g = g.replace("versionCode 69", "versionCode 70").replace("versionName '1.11.0'", "versionName '1.12.0'")
gradle.write_text(g, encoding="utf-8")
print("Applied Hadota WiFi Manager v1.12.0 authenticated-router-session fix")
