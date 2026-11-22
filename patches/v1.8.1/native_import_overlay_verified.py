from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s = main.read_text(encoding="utf-8")

if "nativeImportButton" not in s:
    s = s.replace(
        "import android.webkit.WebViewClient;",
        "import android.webkit.WebViewClient;\nimport android.widget.Button;\nimport android.widget.FrameLayout;\nimport android.view.Gravity;"
    )
    s = s.replace(
        "    private WebView web;",
        "    private WebView web;\n    private Button nativeImportButton;\n    private FrameLayout mainFrame;"
    )
    anchor = '        web.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");'
    if anchor not in s:
        raise SystemExit("AndroidBridge setup anchor missing")
    addition = anchor + """
        mainFrame = new FrameLayout(this);
        mainFrame.addView(web, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        nativeImportButton = new Button(this);
        nativeImportButton.setText("استيراد الأجهزة");
        nativeImportButton.setTextColor(Color.rgb(23,18,10));
        nativeImportButton.setTextSize(14);
        nativeImportButton.setAllCaps(false);
        nativeImportButton.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(217,179,106)));
        nativeImportButton.setElevation(24f);
        nativeImportButton.setOnClickListener(v -> captureRouterPage());
        FrameLayout.LayoutParams importParams = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT,
            Gravity.TOP | Gravity.RIGHT);
        importParams.setMargins(12, 12, 12, 12);
        mainFrame.addView(nativeImportButton, importParams);
        nativeImportButton.setVisibility(android.view.View.GONE);"""
    s = s.replace(anchor, addition, 1)

    page_start = "            @Override public void onPageFinished(WebView view, String url) {"
    if page_start not in s:
        raise SystemExit("WebViewClient onPageFinished anchor missing")
    page_hook = """            @Override public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                boolean routerPage = false;
                try {
                    String host = android.net.Uri.parse(url).getHost();
                    routerPage = host != null && host.equalsIgnoreCase(getGatewayAddress());
                } catch (Exception ignored) {}
                if (nativeImportButton != null) {
                    nativeImportButton.setVisibility(routerPage ? android.view.View.VISIBLE : android.view.View.GONE);
                }
            }
"""
    s = s.replace(page_start, page_hook + page_start, 1)

    s = s.replace("        setContentView(web);", "        setContentView(mainFrame);", 1)

    # Ensure it appears immediately when opening the router, even before the first navigation callback.
    s = s.replace(
        '                web.loadUrl("http://" + getGatewayAddress() + "/");',
        '                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.VISIBLE);\n                web.loadUrl("http://" + getGatewayAddress() + "/");',
        1
    )
    main.write_text(s, encoding="utf-8")

# Version bump is deliberately checked; fail the build if it did not happen.
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, n1 = re.subn(r"versionCode\s+\d+", "versionCode 31", g, count=1)
g, n2 = re.subn(r"versionName\s+'[^']+'", "versionName '1.8.1'", g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("Could not update app versionCode/versionName")
gradle.write_text(g, encoding="utf-8")

check = main.read_text(encoding="utf-8")
if "nativeImportButton.setOnClickListener" not in check or "setContentView(mainFrame)" not in check:
    raise SystemExit("Native import overlay verification failed")
print("Verified native Android import overlay in MainActivity; version 1.8.1")
