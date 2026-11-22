from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
p=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=p.read_text(encoding="utf-8")
# Keep the native control visible independently of URL redirects, host parsing, and page JavaScript.
s=s.replace("        nativeImportButton.setVisibility(android.view.View.GONE);","        nativeImportButton.setVisibility(android.view.View.VISIBLE);",1)
s=s.replace("            Gravity.TOP | Gravity.RIGHT);","            Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);",1)
s=s.replace("        importParams.setMargins(12, 12, 12, 12);","        importParams.setMargins(12, 12, 12, 28);",1)
# Do not let navigation callbacks hide the control after ZTE redirects.
old="""                if (nativeImportButton != null) {
                    nativeImportButton.setVisibility(routerPage ? android.view.View.VISIBLE : android.view.View.GONE);
                }"""
s=s.replace(old,"                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.VISIBLE);",1)
# Remove accidental state where app home can cover it: visible but disabled on local home is not needed; leave it visible to prove it is a real overlay.
g=root/"app/build.gradle"
t=g.read_text(encoding="utf-8")
t,n1=re.subn(r"versionCode\s+\\d+","versionCode 32",t,count=1)
t,n2=re.subn(r"versionName\s+'[^']+'","versionName '1.8.2'",t,count=1)
if n1!=1 or n2!=1: raise SystemExit("Version bump failed")
g.write_text(t,encoding="utf-8")
p.write_text(s,encoding="utf-8")
if "Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL" not in s or "nativeImportButton.setVisibility(android.view.View.VISIBLE);" not in s:
    raise SystemExit("Overlay verification failed")
print("v1.8.2 native import button forced visible at bottom-center, independent of router URL")
