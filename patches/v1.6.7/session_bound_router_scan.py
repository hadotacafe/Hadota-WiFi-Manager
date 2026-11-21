from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
assets = root / "app/src/main/assets/index.html"
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
gradle = root / "app/build.gradle"

# The old "inspect login page" action made a separate unauthenticated HTTP request.
# Route it into the same in-app WebView where the user signs in.
h = assets.read_text()
old_label = "فحص صفحة دخول الراوتر (قراءة فقط)"
if old_label not in h:
    raise SystemExit("Router entry button label not found")
h = h.replace(old_label, "فتح الراوتر وتسجيل الدخول")
old_fn = """function inspectRouterLogin(){ $('inspectResult').textContent='جارٍ فحص صفحة الدخول محليًا دون تسجيل دخول...'; if(window.AndroidBridge){AndroidBridge.inspectRouterLogin()}else{$('inspectResult').textContent='ميزة الفحص متاحة داخل تطبيق Android فقط.'}}"""
new_fn = """function inspectRouterLogin(){ $('inspectResult').textContent='جارٍ فتح جلسة الراوتر داخل التطبيق. سجّل الدخول مرة واحدة، وسيتم فحص الأجهزة من الصفحة نفسها.'; if(window.AndroidBridge){AndroidBridge.openRouterPanel()}else{$('inspectResult').textContent='الميزة متاحة داخل تطبيق Android فقط.'}}"""
if old_fn not in h:
    raise SystemExit("inspectRouterLogin function not found")
h = h.replace(old_fn, new_fn)
assets.write_text(h)

# Return both the scan report and the actual authenticated page text from the
# exact same WebView DOM. MainActivity already parses router_text into devices.
s = router.read_text()
start = s.find("        @JavascriptInterface public void scanAll() {")
end = s.find("        @JavascriptInterface public void capture() {", start)
if start < 0 or end < 0:
    raise SystemExit("scanAll/capture methods not found")
block = s[start:end]
call = block.find("router.evaluateJavascript(")
comma = block.find(", value -> {", call)
if call < 0 or comma < 0:
    raise SystemExit("Could not isolate scan JavaScript expression")
js_expr = block[call + len("router.evaluateJavascript("):comma]
new_block = """        @JavascriptInterface public void scanAll() {
            runOnUiThread(() -> {
                if (router == null) return;
                router.evaluateJavascript(""" + js_expr + """, value -> {
                    String report = value == null ? "null" : value;
                    if (router == null) return;
                    router.evaluateJavascript("(function(){return document.body?document.body.innerText:''})()", bodyValue -> {
                        String pageText = bodyValue == null ? "" : bodyValue;
                        try { pageText = new org.json.JSONArray("[" + pageText + "]").optString(0, ""); } catch (Exception ignored) {}
                        Intent result = new Intent();
                        result.putExtra("router_report", report);
                        result.putExtra("router_text", pageText);
                        setResult(RESULT_OK, result);
                        finish();
                    });
                });
            });
        }
"""
s = s[:start] + new_block + s[end:]
router.write_text(s)

g = gradle.read_text()
if "versionName '1.6.6'" not in g:
    raise SystemExit("Expected base version 1.6.6 not found")
g = g.replace("versionCode 16", "versionCode 17").replace("versionName '1.6.6'", "versionName '1.6.7'")
gradle.write_text(g)
