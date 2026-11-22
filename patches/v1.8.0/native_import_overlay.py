from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
p=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=p.read_text(encoding="utf-8")
s=s.replace("import android.webkit.WebViewClient;","import android.webkit.WebViewClient;\nimport android.widget.Button;\nimport android.widget.FrameLayout;\nimport android.view.Gravity;")
s=s.replace("    private WebView web;","    private WebView web;\n    private Button nativeImportButton;\n    private FrameLayout mainFrame;")
s=s.replace("        web.addJavascriptInterface(new AndroidBridge(), \"AndroidBridge\");","        web.addJavascriptInterface(new AndroidBridge(), \"AndroidBridge\");\n        mainFrame = new FrameLayout(this);\n        mainFrame.addView(web, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));\n        nativeImportButton = new Button(this);\n        nativeImportButton.setText(\"استيراد الأجهزة\");\n        nativeImportButton.setTextColor(Color.rgb(23,18,10));\n        nativeImportButton.setTextSize(14);\n        nativeImportButton.setAllCaps(false);\n        nativeImportButton.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(217,179,106)));\n        nativeImportButton.setOnClickListener(v -> captureRouterPage());\n        FrameLayout.LayoutParams importParams = new FrameLayout.LayoutParams(FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT, Gravity.TOP | Gravity.LEFT);\n        importParams.setMargins(12, 12, 12, 12);\n        mainFrame.addView(nativeImportButton, importParams);\n        nativeImportButton.setVisibility(android.view.View.GONE);")
# Add page start to toggle native overlay; native Android control does not depend on page JS.
needle="            @Override public void onPageFinished(WebView view, String url) {"
insert="""            @Override public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                boolean routerPage = false;
                try { String host = android.net.Uri.parse(url).getHost(); routerPage = host != null && host.equalsIgnoreCase(getGatewayAddress()); } catch (Exception ignored) {}
                if (nativeImportButton != null) nativeImportButton.setVisibility(routerPage ? android.view.View.VISIBLE : android.view.View.GONE);
            }
"""
if needle not in s: raise SystemExit("onPageFinished anchor missing")
s=s.replace(needle,insert+needle,1)
s=s.replace("        setContentView(web);","        setContentView(mainFrame);",1)
s=s.replace('                web.loadUrl("http://" + getGatewayAddress() + "/");','                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.VISIBLE);\n                web.loadUrl("http://" + getGatewayAddress() + "/");',1)
s=s.replace('                web.loadUrl("file:///android_asset/index.html");\n                return;','                web.loadUrl("file:///android_asset/index.html");\n                if (nativeImportButton != null) nativeImportButton.setVisibility(android.view.View.GONE);\n                return;',1)
# Bump app version.
g=root/"app/build.gradle"
t=g.read_text(encoding="utf-8")
t=re.sub(r"versionCode\\s+\\d+","versionCode 30",t,count=1)
t=re.sub(r"versionName\\s+'[^']+'","versionName '1.8.0'",t,count=1)
g.write_text(t,encoding="utf-8")
p.write_text(s,encoding="utf-8")
print("Native Android import overlay added; version 1.8.0")
