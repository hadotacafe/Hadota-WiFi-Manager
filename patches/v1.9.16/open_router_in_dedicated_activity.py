from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
old="""    // Open the router directly in the main app WebView.
    // This avoids launching an Android picker/activity and keeps the app bridge alive.
    private void openRouterPanel() {
        runOnUiThread(() -> {
            if (web == null) {
                createMainWebView();
            }
            if (web != null) {
                web.loadUrl("http://" + getGatewayAddress() + "/");
            }
        });
    }"""
new="""    // Open the router in its dedicated WebView so the login/session is isolated
    // from the dashboard and returning to the app is explicit and reliable.
    private void openRouterPanel() {
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
    }"""
if old not in s: raise SystemExit("direct openRouterPanel block not found")
s=s.replace(old,new,1)
# Confirm the dedicated activity is registered and its source exists.
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text(encoding="utf-8")
if 'android:name=".RouterActivity"' not in m:
    needle='<activity android:name=".MainActivity"'
    if needle not in m: raise SystemExit("MainActivity manifest entry not found")
    m=m.replace(needle,'<activity android:name=".RouterActivity" android:exported="false" />\n        '+needle,1)
    manifest.write_text(m,encoding="utf-8")
router=root/"app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
if not router.exists(): raise SystemExit("RouterActivity source missing")
# Keep the dashboard bridge available when the router activity returns.
if "onActivityResult(int requestCode" not in s: raise SystemExit("Activity result handler missing")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
a=re.subn(r"versionCode\s+\d+","versionCode 51",g,count=1)
b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.16'",a[0],count=1)
if a[1]!=1 or b[1]!=1: raise SystemExit("Version update failed")
gradle.write_text(b[0],encoding="utf-8")
print("v1.9.16: launch dedicated RouterActivity via ActivityResult; explicit router login screen and return flow")
