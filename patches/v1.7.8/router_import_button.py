from pathlib import Path
p=Path('source/Hadota-WiFi-Manager-Android/app/src/main/java/com/hadota/wifimanager/MainActivity.java')
s=p.read_text()
start=s.index('            @Override public void onPageFinished(WebView view, String url) {')
end=s.index('            @Override public void onReceivedSslError', start)
new='''            @Override public void onPageFinished(WebView view, String url) {
                if (isRouterUrl(url)) {
                    // ZTE may redirect through login/status URLs; inject after each final DOM load.
                    view.postDelayed(() -> injectRouterControls(view), 250);
                    view.postDelayed(() -> injectRouterControls(view), 900);
                    view.postDelayed(() -> injectRouterControls(view), 1800);
                }
            }
'''
s=s[:start]+new+s[end:]
marker='    // Open the router directly in the main app WebView.\n'
helper='''    private boolean isRouterUrl(String url) {
        try {
            String host = android.net.Uri.parse(url).getHost();
            return host != null && host.equalsIgnoreCase(getGatewayAddress());
        } catch (Exception ignored) { return false; }
    }

    private void injectRouterControls(WebView view) {
        if (view == null || web != view) return;
        String js = "(function(){try{if(!document.body)return false;"
          + "var b=document.getElementById('hadotaCaptureBtn');"
          + "if(!b){b=document.createElement('button');b.id='hadotaCaptureBtn';"
          + "b.textContent='استيراد الأجهزة';"
          + "b.style.cssText='position:fixed!important;top:12px!important;left:12px!important;z-index:2147483647!important;padding:13px 16px!important;background:#d9b36a!important;color:#17120a!important;border:2px solid #fff!important;border-radius:12px!important;font-weight:bold!important;font-size:15px!important;box-shadow:0 2px 12px #000!important;opacity:1!important;display:block!important;visibility:visible!important';"
          + "b.onclick=function(){location.href='hadota://capture'};document.body.appendChild(b);"
          + "}else if(b.parentNode!==document.body){document.body.appendChild(b)}"
          + "return true}catch(e){return false}})()";
        view.evaluateJavascript(js, null);
    }

'''
s=s.replace(marker,helper+marker)
p.write_text(s)
h=Path('source/Hadota-WiFi-Manager-Android/app/src/main/assets/index.html')
t=h.read_text()
t=t.replace('لتحديث الأجهزة الحية افتح لوحة الراوتر وسجّل الدخول، ثم اضغط زر استيراد الأجهزة أعلى الصفحة.', 'لتحديث الأجهزة الحية افتح لوحة الراوتر وسجّل الدخول، ثم اضغط زر «استيراد الأجهزة» الذي يظهر داخل صفحة الراوتر.')
t=t.replace('لقطة 21-11-2026', 'قائمة محفوظة محليًا')
h.write_text(t)
b=Path('source/Hadota-WiFi-Manager-Android/app/build.gradle')
x=b.read_text().replace('versionCode 27', 'versionCode 28').replace("versionName '1.7.7'", "versionName '1.7.8'")
b.write_text(x)
print('patched 1.7.8')
