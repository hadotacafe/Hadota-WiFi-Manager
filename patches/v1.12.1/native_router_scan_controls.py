from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

for imp in [
    "import android.widget.FrameLayout;",
    "import android.widget.LinearLayout;",
    "import android.widget.Button;",
    "import android.view.Gravity;",
    "import android.view.View;",
]:
    if imp not in s:
        s = s.replace("import android.view.ViewGroup;", "import android.view.ViewGroup;\n" + imp, 1)

old = """        setContentView(router);
        router.loadUrl("https://" + gateway + "/");"""
new = """        // Native controls stay visible even when the router firmware replaces its page DOM.
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.WHITE);
        root.addView(router, new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setGravity(Gravity.CENTER_VERTICAL);
        controls.setPadding(8, 8, 8, 8);
        controls.setBackgroundColor(Color.argb(220, 11, 16, 23));

        Button scanButton = new Button(this);
        scanButton.setText("فحص بيانات الراوتر");
        scanButton.setTextSize(14);
        scanButton.setAllCaps(false);
        scanButton.setOnClickListener(v -> {
            scanButton.setEnabled(false);
            scanButton.setText("جارٍ الفحص...");
            new RouterBridge().scanAll();
            scanButton.postDelayed(() -> {
                if (!isFinishing()) {
                    scanButton.setEnabled(true);
                    scanButton.setText("فحص بيانات الراوتر");
                }
            }, 18000);
        });

        Button backButton = new Button(this);
        backButton.setText("رجوع للتطبيق");
        backButton.setTextSize(14);
        backButton.setAllCaps(false);
        backButton.setOnClickListener(v -> {
            setResult(RESULT_CANCELED);
            finish();
        });

        LinearLayout.LayoutParams controlParams = new LinearLayout.LayoutParams(
            0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        controls.addView(scanButton, controlParams);
        controls.addView(backButton, controlParams);

        FrameLayout.LayoutParams overlayParams = new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT,
            Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        root.addView(controls, overlayParams);
        setContentView(root);
        router.loadUrl("https://" + gateway + "/");"""
if old not in s:
    raise SystemExit("setContentView insertion anchor not found")
s = s.replace(old, new, 1)
router.write_text(s, encoding="utf-8")
print("Native scan and return controls added above the router WebView.")

# Bump Android package version for this tested build.
import re
gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, code_count = re.subn(r"versionCode\\s+\\d+", "versionCode 70", g, count=1)
g, name_count = re.subn(r"versionName\\s+'[^']+'", "versionName '1.12.1'", g, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update Android version metadata")
gradle.write_text(g, encoding="utf-8")
