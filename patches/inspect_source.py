from pathlib import Path
import shutil

root = Path("source/Hadota-WiFi-Manager-Android")
out = Path("source-inspection")
targets = [
    root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java",
    root / "app/src/main/AndroidManifest.xml",
    root / "app/src/main/assets/index.html",
    root / "app/build.gradle",
]
out.mkdir(exist_ok=True)
for src in targets:
    if src.exists():
        dest = out / src.name
        shutil.copy2(src, dest)
        print(f"INSPECTED {src} -> {dest} ({src.stat().st_size} bytes)")
    else:
        print(f"MISSING {src}")
if not any(out.iterdir()):
    raise SystemExit("No source files were extracted")
