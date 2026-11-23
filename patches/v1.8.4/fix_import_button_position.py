from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text(encoding="utf-8")
if "nativeImportButton" not in s:
    raise SystemExit("Native import button not found")
s = s.replace("Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL", "Gravity.TOP | Gravity.RIGHT", 1)
s = re.sub(r"importParams\\.setMargins\\([^;]+\\);", "importParams.setMargins(12, 24, 12, 12);", s, count=1)
s = s.replace("nativeImportButton.setText(\"استيراد الأجهزة\");", "nativeImportButton.setText(\"استيراد الأجهزة\");\n        nativeImportButton.setContentDescription(\"استيراد الأجهزة من صفحة الراوتر\");", 1)
main.write_text(s, encoding="utf-8")
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\\s+\\d+", "versionCode 34", g, count=1)
g, b = re.subn(r"versionName\\s+'[^']+'", "versionName '1.8.4'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Version update failed")
gradle.write_text(g, encoding="utf-8")
check = main.read_text(encoding="utf-8")
if "Gravity.TOP | Gravity.RIGHT" not in check:
    raise SystemExit("Import button top position verification failed")
print("v1.8.4: moved native import button to top-right, clear of Android navigation bar")
