from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
html = root / "app/src/main/assets/index.html"
gradle = root / "app/build.gradle"

s = main.read_text()
# Keep every router URL inside the app WebView; never hand it to Android's
# external intent resolver (which can show unrelated file/browser pickers).
old = """                if (u.startsWith("hadota://capture")) { captureRouterPage(); return true; }
                return false;"""
new = """                android.net.Uri uri = request.getUrl();
                String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(java.util.Locale.ROOT);
                if ("hadota".equals(scheme) && u.startsWith("hadota://capture")) { captureRouterPage(); return true; }
                if ("http".equals(scheme) || "https".equals(scheme)) {
                    String host = uri.getHost();
                    if (host != null && host.equalsIgnoreCase(getGatewayAddress())) return false;
                }
                // Block file/content/intent and unknown schemes from leaving the app.
                return true;"""
if old not in s:
    raise SystemExit("WebView URL handler anchor not found")
s = s.replace(old, new, 1)
# Legacy callback for WebView versions that use the string overload.
anchor = """            @Override public void onPageFinished(WebView view, String url) {"""
insert = """            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url == null) return true;
                if (url.startsWith("hadota://capture")) { captureRouterPage(); return true; }
                android.net.Uri uri = android.net.Uri.parse(url);
                String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(java.util.Locale.ROOT);
                return !("http".equals(scheme) || "https".equals(scheme));
            }
"""
if anchor not in s:
    raise SystemExit("WebView page-finished anchor not found")
s = s.replace(anchor, insert + anchor, 1)
# Ensure the entry point has a single unambiguous router-open button.
h = html.read_text()
h = re.sub(r'<button class="btn" onclick="openRouterPanel\(\)">.*?</button>', '<button class="btn" onclick="openRouterPanel()">فتح لوحة الراوتر وتسجيل الدخول</button>', h, count=1)
h = re.sub(r'<button class="btn alt" onclick="inspectRouterLogin\(\)">.*?</button>', '', h, count=1)
h = re.sub(r'function inspectRouterLogin\(\)\{.*?\}\n', '', h, count=1)
html.write_text(h)

g = gradle.read_text()
if "versionName '1.6.9'" not in g:
    raise SystemExit("Expected base version 1.6.9 not found")
g = g.replace("versionCode 19", "versionCode 20").replace("versionName '1.6.9'", "versionName '1.7.0'")
gradle.write_text(g)
