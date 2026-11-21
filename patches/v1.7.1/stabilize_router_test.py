from pathlib import Path

root = Path("source/Hadota-WiFi-Manager-Android")
main = root / "app/src/main/java/com/hadota/wifimanager/MainActivity.java"
gradle = root / "app/build.gradle"

s = main.read_text()
start = s.index("        @JavascriptInterface public void testRouter() {")
end = s.index("        @JavascriptInterface public void inspectRouterLogin()", start)

replacement = """        @JavascriptInterface public void testRouter() {
            // Never let a diagnostic/network failure terminate the Android process.
            try {
                executor.execute(() -> {
                    HttpURLConnection connection = null;
                    boolean ok = false;
                    String message;
                    long started = System.currentTimeMillis();
                    try {
                        String gateway = getGatewayAddress();
                        URL url = new URL("http://" + gateway + "/");
                        connection = (HttpURLConnection) url.openConnection();
                        connection.setRequestMethod("GET");
                        connection.setConnectTimeout(4000);
                        connection.setReadTimeout(4000);
                        connection.setInstanceFollowRedirects(false);
                        connection.setUseCaches(false);
                        connection.setRequestProperty("Connection", "close");
                        connection.setRequestProperty("User-Agent", "HadotaWiFiManager/1.7.1");
                        int code = connection.getResponseCode();
                        long elapsed = System.currentTimeMillis() - started;
                        String server = connection.getHeaderField("Server");
                        String location = connection.getHeaderField("Location");
                        ok = code >= 200 && code < 500;
                        StringBuilder details = new StringBuilder();
                        details.append("عنوان البوابة: ").append(gateway)
                               .append("\\nاستجابة الراوتر: HTTP ").append(code)
                               .append("\\nزمن الاستجابة: ").append(elapsed).append(" ms");
                        if (server != null && !server.isEmpty()) details.append("\\nالخادم: ").append(server);
                        if (location != null && !location.isEmpty()) details.append("\\nإعادة توجيه إلى: ").append(location);
                        details.append("\\n\\nاختبار وصول وقراءة فقط؛ لم يتم تسجيل الدخول أو تغيير الإعدادات.");
                        message = details.toString();
                    } catch (Throwable e) {
                        message = "تعذر الوصول إلى بوابة الراوتر. تأكد من اتصال الهاتف بشبكة الكافيه.\\nالتفاصيل: " +
                            e.getClass().getSimpleName() + (e.getMessage() == null ? "" : " — " + e.getMessage());
                    } finally {
                        if (connection != null) {
                            try { connection.disconnect(); } catch (Throwable ignored) {}
                        }
                    }
                    final boolean result = ok;
                    final String text = message;
                    try {
                        runOnUiThread(() -> {
                            try {
                                if (!isFinishing() && !isDestroyed() && web != null) {
                                    web.evaluateJavascript("routerResult(" + result + "," +
                                        org.json.JSONObject.quote(text) + ")", null);
                                }
                            } catch (Throwable ignored) {}
                        });
                    } catch (Throwable ignored) {}
                });
            } catch (Throwable e) {
                try {
                    String text = "تعذر بدء الاختبار: " + e.getClass().getSimpleName();
                    if (web != null) web.evaluateJavascript("routerResult(false," +
                        org.json.JSONObject.quote(text) + ")", null);
                } catch (Throwable ignored) {}
            }
        }

"""
s = s[:start] + replacement + s[end:]
main.write_text(s)

g = gradle.read_text()
if "versionName '1.7.0'" not in g:
    raise SystemExit("Expected version 1.7.0 base not found")
g = g.replace("versionCode 20", "versionCode 21").replace("versionName '1.7.0'", "versionName '1.7.1'")
gradle.write_text(g)
