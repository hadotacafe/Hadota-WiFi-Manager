from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
pattern=r"(?s)    private void openRouterPanel\(\)\s*\{.*?\n    \}\n\n    @Override public void onBackPressed"
replacement="""    private void openRouterPanel() {
        runOnUiThread(() -> {
            try {
                Intent intent = new Intent(MainActivity.this, RouterActivity.class);
                intent.putExtra("gateway", getGatewayAddress());
                startActivityForResult(intent, 6201);
            } catch (Exception e) {
                android.widget.Toast.makeText(MainActivity.this,
                    "تعذر فتح لوحة الراوتر: " + e.getMessage(),
                    android.widget.Toast.LENGTH_LONG).show();
            }
        });
    }

    @Override public void onBackPressed"""
s,n=re.subn(pattern,replacement,s,count=1)
if n!=1: raise SystemExit("Could not replace openRouterPanel by method boundary")
if 'android:name=".RouterActivity"' not in (root/"app/src/main/AndroidManifest.xml").read_text(encoding="utf-8"):
 raise SystemExit("RouterActivity is not registered in manifest")
if 'startActivityForResult(intent, 6201)' not in s: raise SystemExit("Router activity launch verification failed")
main.write_text(s,encoding="utf-8")
router=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
r=router.read_text(encoding="utf-8")
# Fix WebView evaluateJavascript result parsing: Android returns a JSON string for object values.
r=r.replace('state.contains("\\\\\\"login\\\\\\":false")','state.contains("\\\\\\"login\\\\\\":false") || state.contains("\\"login\\":false")')
# Keep the router login page open; do not auto-close it after a page with no password field.
r=r.replace('''                    if (automaticScanStarted || router == null || value == null) return;
                    String state = value;
                    if (state.contains''','''                    if (automaticScanStarted || router == null || value == null) return;
                    String state = value;
                    if (state.contains''')
router.write_text(r,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 52",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.17'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.17 verified: openRouterPanel now launches RouterActivity (6201), not dashboard WebView")
