from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
old='nativeImportButton.setOnClickListener(v -> captureRouterPage());'
new='''nativeImportButton.setOnClickListener(v -> {
            String currentHost = "";
            try {
                String currentUrl = web == null ? "" : web.getUrl();
                String host = currentUrl == null ? null : android.net.Uri.parse(currentUrl).getHost();
                currentHost = host == null ? "" : host;
            } catch (Exception ignored) {}
            if (!getGatewayAddress().equalsIgnoreCase(currentHost)) {
                openRouterPanel();
                android.widget.Toast.makeText(this,
                    "تم فتح لوحة الراوتر. سجّل الدخول ثم اضغط استيراد الأجهزة.",
                    android.widget.Toast.LENGTH_LONG).show();
                return;
            }
            captureRouterPage();
        });'''
if old not in s:
    raise SystemExit("Import button click handler anchor missing")
s=s.replace(old,new,1)
if "تم فتح لوحة الراوتر. سجّل الدخول ثم اضغط استيراد الأجهزة." not in s or "captureRouterPage();" not in s:
    raise SystemExit("Import button action verification failed")
main.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 38",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.3'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Could not update version")
gradle.write_text(g,encoding="utf-8")
print("v1.9.3: import action now opens router panel first; on router page it captures authenticated page data")
