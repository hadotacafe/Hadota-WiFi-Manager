from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
main=root/"app/src/main/java/com/hadota/wifimanager/MainActivity.java"
s=main.read_text(encoding="utf-8")
s=s.replace("private final ExecutorService executor = Executors.newSingleThreadExecutor();",
"""private final ExecutorService executor = Executors.newSingleThreadExecutor();
    // Keep the quick gateway test independent from longer router page/script inspections.
    private final ExecutorService routerTestExecutor = Executors.newSingleThreadExecutor();""",1)
start=s.index("@JavascriptInterface public void testRouter()")
end=s.index("@JavascriptInterface public void inspectRouterLogin()",start)
block=s[start:end]
if "executor.execute(() ->" not in block: raise SystemExit("testRouter executor call not found")
block=block.replace("executor.execute(() ->","routerTestExecutor.execute(() ->",1)
block=block.replace("connection.setConnectTimeout(4000);","connection.setConnectTimeout(2500);")
block=block.replace("connection.setReadTimeout(4000);","connection.setReadTimeout(2500);")
block=block.replace('"HadotaWiFiManager/1.7.1"','"HadotaWiFiManager/1.9.13"')
# Ensure a result is sent even if the activity is returning from a different page.
block=block.replace('if (!isFinishing() && !isDestroyed() && web != null) {',
'''if (!isFinishing() && !isDestroyed() && web != null &&
                                    web.getUrl() != null && web.getUrl().startsWith("file:///android_asset/index.html")) {''')
s=s[:start]+block+s[end:]
s=s.replace("executor.shutdownNow();","executor.shutdownNow();\n        routerTestExecutor.shutdownNow();",1)
main.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
g,a=re.subn(r"versionCode\s+\d+","versionCode 48",g,count=1)
g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.13'",g,count=1)
if a!=1 or b!=1: raise SystemExit("Version update failed")
gradle.write_text(g,encoding="utf-8")
# Static checks: test method must use isolated executor, not shared inspection executor.
check=main.read_text(encoding="utf-8")
tb=check[check.index("@JavascriptInterface public void testRouter()"):check.index("@JavascriptInterface public void inspectRouterLogin()")]
if "routerTestExecutor.execute" not in tb or "executor.execute" in tb: raise SystemExit("Dedicated executor verification failed")
print("v1.9.13: isolated gateway test executor; 2.5s connect/read timeouts; prevents inspection queue from blocking test")
