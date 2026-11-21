from pathlib import Path
root = Path("source/Hadota-WiFi-Manager-Android")
p = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = p.read_text()

# Preserve the Android bridge while navigating to the router and remove only
# the second, delayed registration in the capture callback.
needle = 'web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");'
first = s.find(needle)
second = s.find(needle, first + len(needle)) if first >= 0 else -1
if second >= 0:
    line_start = s.rfind("\n", 0, second) + 1
    line_end = s.find("\n", second)
    s = s[:line_start] + s[line_end + 1:]
s = s.replace('web.removeJavascriptInterface("AndroidBridge");', '')

# Make the embedded legacy ZTE page more compatible and less crash-prone.
s = s.replace(
    "        settings.setDomStorageEnabled(true);",
    "        settings.setDomStorageEnabled(true);\n"
    "        settings.setDatabaseEnabled(true);\n"
    "        settings.setSupportMultipleWindows(false);\n"
    "        settings.setJavaScriptCanOpenWindowsAutomatically(false);\n"
    "        settings.setAllowContentAccess(false);\n"
    "        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);"
)

# Rebuild the WebView if Android's renderer process dies instead of closing the app.
ssl_block = """            @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                String host = error.getUrl() == null ? "" : android.net.Uri.parse(error.getUrl()).getHost();
                if (host != null && host.equals(getGatewayAddress())) handler.proceed(); else handler.cancel();
            }
        });"""
replacement = """            @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                String host = error.getUrl() == null ? "" : android.net.Uri.parse(error.getUrl()).getHost();
                if (host != null && host.equalsIgnoreCase(getGatewayAddress())) handler.proceed(); else handler.cancel();
            }
            @Override public boolean onRenderProcessGone(WebView view, android.webkit.RenderProcessGoneDetail detail) {
                if (web == view) {
                    android.view.ViewParent parent = view.getParent();
                    if (parent instanceof android.view.ViewGroup) ((android.view.ViewGroup) parent).removeView(view);
                    view.destroy();
                    web = null;
                    createMainWebView();
                }
                return true;
            }
        });"""
if ssl_block in s:
    s = s.replace(ssl_block, replacement, 1)
else:
    raise SystemExit("Expected WebView SSL handler block not found; refusing unsafe patch")

# Extract WebView setup into a method used both at startup and after renderer recovery.
marker = "        web = new WebView(this);"
if marker in s and "private void createMainWebView()" not in s:
    start = s.index(marker)
    end_marker = '        web.loadUrl("file:///android_asset/index.html");'
    end = s.index(end_marker, start) + len(end_marker)
    setup = s[start:end]
    s = s[:start] + "        createMainWebView();\n    }\n\n    private void createMainWebView() {\n" + setup + s[end:]
    # The original onCreate closing brace now closes createMainWebView.
p.write_text(s)

g = root / "app/build.gradle"
gradle = g.read_text().replace("versionCode 10", "versionCode 11").replace("versionName '1.6.0'", "versionName '1.6.1'")
g.write_text(gradle)
