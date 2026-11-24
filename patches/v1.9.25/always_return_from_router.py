from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

old = """                        if (devices == null || devices.length() == 0) {
                            String note = "لم يتم العثور على أجهزة في الصفحة الحالية. افتح WLAN Client Status أو LAN Client Status من قائمة الراوتر، ثم اضغط «رجوع إلى Hadota» بعد ظهور قائمة الأجهزة.";
                            router.evaluateJavascript("(function(){var n=document.getElementById('hadotaScanHint');if(!n){n=document.createElement('div');n.id='hadotaScanHint';n.style='position:fixed;z-index:2147483647;top:112px;right:8px;left:8px;padding:14px;background:#152536;color:#f4dfad;border:2px solid #d9b36a;border-radius:12px;font:bold 15px sans-serif;line-height:1.7;direction:rtl';document.body.appendChild(n)}n.textContent=" + org.json.JSONObject.quote(note) + ";return true})()", null);
                            return;
                        }"""
new = """                        if (devices == null) devices = new org.json.JSONArray();
                        if (devices.length() == 0) {
                            android.widget.Toast.makeText(RouterActivity.this,
                                "تم الرجوع للتطبيق. لم تُستخرج أجهزة من الصفحة الحالية.",
                                android.widget.Toast.LENGTH_LONG).show();
                        }"""
if old not in s:
    raise SystemExit("capture empty-device blocking branch not found")
s = s.replace(old, new, 1)

old_back = """    @Override public void onBackPressed() {
        if (router != null && router.canGoBack()) router.goBack();
        else { setResult(RESULT_CANCELED); finish(); }
    }"""
new_back = """    @Override public void onBackPressed() {
        // Back always exits the router panel and returns to Hadota.
        setResult(RESULT_CANCELED);
        finish();
    }"""
if old_back not in s:
    raise SystemExit("RouterActivity onBackPressed block not found")
s = s.replace(old_back, new_back, 1)
router.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\s+\d+", "versionCode 60", g, count=1)
g, b = re.subn(r"versionName\s+'[^']+'", "versionName '1.9.25'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Could not update app version to 1.9.25")
gradle.write_text(g, encoding="utf-8")
print("v1.9.25: return button always closes router panel, even with zero extracted clients; Android Back always returns to Hadota")
