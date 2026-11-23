from pathlib import Path
import re
root=Path("source/Hadota-WiFi-Manager-Android")
p=root/"app/src/main/assets/index.html"
s=p.read_text(encoding="utf-8")
css="""<style>
:root{color-scheme:dark;--gold:#e1bd75;--txt:#f7f3e9;--muted:#9eacbd;--line:#29394d;--green:#55d6a5;--red:#ff7777;--amber:#f1c46c}
body{background:radial-gradient(ellipse at 85% -10%,rgba(206,164,91,.16),transparent 34%),linear-gradient(160deg,#111d2b 0,#090e16 55%,#0b111b 100%);padding:18px 14px 42px}
.head{gap:13px;margin:5px 2px 18px}.logo{width:58px;height:58px;flex:0 0 58px;border-radius:19px;background:linear-gradient(145deg,#f4d99a,#9f7132);box-shadow:0 7px 22px rgba(216,179,107,.2);display:grid;place-items:center}.logo svg{width:48px;height:48px}
.card{background:linear-gradient(145deg,rgba(22,34,49,.97),rgba(15,24,36,.98));border:1px solid rgba(117,139,165,.2);border-radius:20px;padding:17px;box-shadow:0 14px 34px rgba(0,0,0,.24)}
.btn{border-radius:13px;min-height:48px;font-weight:800;background:linear-gradient(135deg,#f3d99e,#c99c51);box-shadow:0 6px 16px rgba(201,156,81,.13)}.btn.alt{background:linear-gradient(145deg,#26394f,#1a2a3d);border-color:#3a5069}
.tabs{padding:5px;background:#0d1723;border:1px solid var(--line);border-radius:15px}.tabs button{border-radius:11px}.tabs button.active{background:linear-gradient(135deg,#f3d99e,#c99c51);color:#21180b}
.pill{font-weight:750;background:rgba(225,189,117,.08);border-color:rgba(225,189,117,.42);color:#f3d99e}.device{background:linear-gradient(145deg,#101b29,#0d1621);border:1px solid #2a3b50;border-radius:14px;padding:13px}
.section-kicker{color:var(--gold);font-size:10px;font-weight:850;letter-spacing:1.5px;margin-bottom:7px}.hero-top,.card-head{display:flex;justify-content:space-between;align-items:center;gap:10px}.hero-copy{margin:12px 0 2px}.hero-copy p{margin:8px 0 0}.hero-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}.mini-stat{border:1px solid rgba(110,132,157,.2);background:rgba(7,14,23,.42);border-radius:13px;padding:11px}.mini-stat b{display:block;font-size:17px;color:#f3d99e}.mini-stat span{font-size:10px;color:var(--muted)}.icon-title{display:flex;align-items:center;gap:9px}.section-icon{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;background:rgba(225,189,117,.12);color:#f3d99e}
@media(max-width:390px){.hero-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>"""
s=s.replace("</style>", "</style>"+css,1)
s=s.replace('<div class="logo">H</div>','''<div class="logo"><svg viewBox="0 0 64 64" fill="none"><path d="M9 23C22 11 42 11 55 23M17 31C26 23 38 23 47 31M25 39C29 35 35 35 39 39" stroke="#241707" stroke-width="5" stroke-linecap="round"/><circle cx="32" cy="45" r="3.5" fill="#241707"/><path d="M32 48L18 54V43C18 36 24 33 32 30C40 33 46 36 46 43V54L32 60L18 54" stroke="#241707" stroke-width="2.5" stroke-linejoin="round"/></svg></div>''')
s=s.replace('<section class="card"><div class="status">','<section class="card"><div class="section-kicker">NETWORK CONTROL CENTER</div><div class="hero-top"><div class="status">',1)
s=s.replace('<span id="routerState">لم يتم اختبار الراوتر بعد</span></div><p class="muted">','<span id="routerState">لم يتم اختبار الراوتر بعد</span></div><span class="pill">HADOTA · WIFI</span></div><div class="hero-copy"><p class="muted">',1)
s=s.replace('اكتشاف بوابة الشبكة تلقائيًا وفحص الوصول ومعلومات الخادم العامة — دون تسجيل دخول أو تغيير إعدادات.</p><button class="btn"','مراقبة الاتصال وإدارة أجهزة شبكة الكافيه من مكان واحد.</p></div><div class="hero-grid"><div class="mini-stat"><b>14</b><span>حد أجهزة الموظفين</span></div><div class="mini-stat"><b>ZTE</b><span>بوابة الشبكة</span></div><div class="mini-stat"><b>محلي</b><span>حفظ الإعدادات</span></div></div><button class="btn"',1)
s=s.replace('<div class="row"><h2>جرد أجهزة الشبكة</h2><span class="pill">لقطة 21-11-2026</span></div>','<div class="card-head"><div class="icon-title"><span class="section-icon">⌘</span><h2>جرد أجهزة الشبكة</h2></div><span class="pill">لقطة 21-11-2026</span></div>')
s=s.replace('<div class="row"><h2>سياسة الموظفين</h2><span class="pill">حتى 14 جهازًا</span></div>','<div class="card-head"><div class="icon-title"><span class="section-icon">♙</span><h2>سياسة الموظفين</h2></div><span class="pill">حتى 14 جهازًا</span></div>')
s=s.replace('<div class="card"><h2>سياسة الزبائن</h2>','<div class="card"><div class="card-head"><div class="icon-title"><span class="section-icon">◉</span><h2>سياسة الزبائن</h2></div></div>')
s=s.replace('<section class="card"><h2>ما الذي يعمل حاليًا؟</h2>','<section class="card"><div class="card-head"><div class="icon-title"><span class="section-icon">✓</span><h2>ما الذي يعمل حاليًا؟</h2></div></div>')
s=s.replace('نسخة تطوير 1.7.7:','نسخة تطوير 1.9.0:')
p.write_text(s,encoding="utf-8")
res=root/"app/src/main/res";(res/"drawable").mkdir(parents=True,exist_ok=True);(res/"mipmap-anydpi-v26").mkdir(parents=True,exist_ok=True)
fg='''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"><path android:strokeColor="#E7BC68" android:strokeWidth="4" android:strokeLineCap="round" android:fillColor="#00000000" android:pathData="M20,34 C38,17 70,17 88,34"/><path android:strokeColor="#F5D58F" android:strokeWidth="4.5" android:strokeLineCap="round" android:fillColor="#00000000" android:pathData="M29,45 C42,33 66,33 79,45"/><path android:strokeColor="#E7BC68" android:strokeWidth="4.5" android:strokeLineCap="round" android:fillColor="#00000000" android:pathData="M40,56 C47,49 61,49 68,56"/><path android:fillColor="#F5D58F" android:pathData="M54,61a3.5,3.5 0,1 0,0.1 0"/><path android:fillColor="#241306" android:strokeColor="#E7BC68" android:strokeWidth="3.5" android:strokeLineJoin="round" android:pathData="M54,68 L78,77 L78,89 C78,100 67,106 54,112 C41,106 30,100 30,89 L30,77 Z"/><path android:strokeColor="#F5D58F" android:strokeWidth="4.5" android:strokeLineCap="round" android:strokeLineJoin="round" android:fillColor="#00000000" android:pathData="M43,88 L51,96 L66,80"/></vector>'''
bg='''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"><path android:fillColor="#241306" android:pathData="M0,0h108v108h-108z"/></vector>'''
(res/"drawable/ic_launcher_foreground.xml").write_text(fg,encoding="utf-8");(res/"drawable/ic_launcher_background.xml").write_text(bg,encoding="utf-8")
ad='''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@drawable/ic_launcher_background"/><foreground android:drawable="@drawable/ic_launcher_foreground"/></adaptive-icon>'''
for n in ("ic_launcher.xml","ic_launcher_round.xml"):(res/"mipmap-anydpi-v26"/n).write_text(ad,encoding="utf-8")
mp=root/"app/src/main/AndroidManifest.xml";m=mp.read_text(encoding="utf-8").replace('android:label="Hadota WiFi Manager"','android:label="Hadota WiFi Manager" android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher_round"');mp.write_text(m,encoding="utf-8")
gp=root/"app/build.gradle";g=gp.read_text(encoding="utf-8");g,a=re.subn(r"versionCode\s+\d+","versionCode 35",g,count=1);g,b=re.subn(r"versionName\s+'[^']+'","versionName '1.9.0'",g,count=1)
if a!=1 or b!=1:raise SystemExit("Version update failed")
gp.write_text(g,encoding="utf-8")
print("Applied premium responsive UI and new Wi-Fi shield launcher icon, version 1.9.0")
