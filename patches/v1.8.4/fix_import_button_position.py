from pathlib import Path
import re
root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text(encoding="utf-8")
if "nativeImportButton" not in s:
    raise SystemExit("Native import button not found")
s = s.replace("Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL", "Gravity.TOP | Gravity.RIGHT", 1)
s, n = re.subn(r"importParams\.setMargins\([^;]+\);", "importParams.setMargins(12, 64, 12, 12);", s, count=1)
if n != 1:
    raise SystemExit("Could not move import button margins")
main.write_text(s, encoding="utf-8")
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\s+\d+", "versionCode 37", g, count=1)
g, b = re.subn(r"versionName\s+'[^']+'", "versionName '1.9.2'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Version update failed")
gradle.write_text(g, encoding="utf-8")
check = main.read_text(encoding="utf-8")
if "Gravity.TOP | Gravity.RIGHT" not in check:
    raise SystemExit("Import button top position verification failed")
print("v1.8.4: moved native import button to top-right, below Android status bar without covering app title")
