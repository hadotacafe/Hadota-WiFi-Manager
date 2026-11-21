from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
gradle = root / "app/build.gradle"

s = router.read_text()
needle = "settings.setJavaScriptEnabled(true);"
if needle not in s:
    raise SystemExit("Router WebView settings block not found")
fit = """settings.setJavaScriptEnabled(true);
        // Fit legacy ZTE desktop pages to the phone screen; allow pinch zoom when needed.
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(90);"""
if "settings.setLoadWithOverviewMode(true);" not in s:
    s = s.replace(needle, fit)
router.write_text(s)

g = gradle.read_text()
if "versionName '1.6.7'" not in g:
    raise SystemExit("Expected base version 1.6.7 not found")
g = g.replace("versionCode 17", "versionCode 18").replace("versionName '1.6.7'", "versionName '1.6.8'")
gradle.write_text(g)
