from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
# Keep the native import action available only while the authenticated router page is open.
# The home screen already has its own visible router/import workflow; a floating overlay there
# obscures the content, especially after the user scrolls.
s=s.replace("        nativeImportButton.setVisibility(android.view.View.VISIBLE);","        nativeImportButton.setVisibility(android.view.View.GONE);",1)
old="""                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.VISIBLE);"""
new="""                if (nativeImportButton != null) {
                    boolean isRouter = false;
                    try {
                        String host = android.net.Uri.parse(url).getHost();
                        isRouter = host != null && host.equalsIgnoreCase(getGatewayAddress());
                    } catch (Exception ignored) {}
                    nativeImportButton.setVisibility(isRouter ? android.view.View.VISIBLE : android.view.View.GONE);
                }"""
if old not in s: raise SystemExit("Always-visible navigation callback missing")
s=s.replace(old,new,1)
# Do not force the floating overlay visible before loading the router. onPageStarted owns visibility.
s=s.replace('                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.VISIBLE);\n                web.loadUrl("http://" + getGatewayAddress() + "/");','                web.loadUrl("http://" + getGatewayAddress() + "/");',1)
# Also verify the final listener still handles the current host and authenticated capture.
if "nativeImportButton.setOnClickListener" not in s or "captureRouterPage();" not in s or "setVisibility(isRouter ? android.view.View.VISIBLE : android.view.View.GONE)" not in s:
    raise SystemExit("Conditional import overlay verification failed")
main.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 40",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.5'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
print("v1.9.5: native floating import control is hidden on local app screens and shown only on router pages")
