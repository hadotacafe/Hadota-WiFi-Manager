from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
gradle = root / "app/build.gradle"

s = main.read_text()
old = """    private void openRouterPanel() {
        runOnUiThread(() -> {
            Intent intent = new Intent(MainActivity.this, RouterActivity.class);
            intent.putExtra("gateway", getGatewayAddress());
            startActivityForResult(intent, 6201);
        });
    }"""
new = """    // Open the router directly in the main app WebView.
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
    }

    @Override public void onBackPressed() {
        if (web != null) {
            String current = web.getUrl();
            if (current != null && !current.startsWith("file:///android_asset/index.html")) {
                web.loadUrl("file:///android_asset/index.html");
                return;
            }
        }
        super.onBackPressed();
    }"""
if old not in s:
    raise SystemExit("Expected openRouterPanel method not found; refusing unsafe patch")
s = s.replace(old, new)
main.write_text(s)

g = gradle.read_text()
if "versionName '1.6.8'" not in g:
    raise SystemExit("Expected base version 1.6.8 not found")
g = g.replace("versionCode 18", "versionCode 19").replace("versionName '1.6.8'", "versionName '1.6.9'")
gradle.write_text(g)
