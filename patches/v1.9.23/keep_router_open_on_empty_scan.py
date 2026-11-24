from pathlib import Path
import re

root = Path("source/Hadota-WiFi-Manager-Android")
router = root / "app/src/main/java/com/hadota/wifimanager/RouterActivity.java"
s = router.read_text(encoding="utf-8")

old = """                            org.json.JSONArray found = scan.optJSONArray("devices");
                            result.putExtra("router_devices", found == null ? "[]" : found.toString());
                        } catch (Exception ignored) { result.putExtra("router_devices", "[]"); }
                        setResult(RESULT_OK, result);
                        finish();"""
new = """                            org.json.JSONArray found = scan.optJSONArray("devices");
                            result.putExtra("router_devices", found == null ? "[]" : found.toString());
                            if (found == null || found.length() == 0) {
                                org.json.JSONArray scannedPages = scan.optJSONArray("pages");
                                int pageCount = scannedPages == null ? 0 : scannedPages.length();
                                String note = "لم يتم العثور على أجهزة في الصفحة الحالية. افتح من قائمة الراوتر صفحة WLAN Client Status أو LAN Client Status، ثم اضغط «فحص بيانات الراوتر». تم فحص " + pageCount + " صفحة دون تغيير إعدادات الراوتر.";
                                router.evaluateJavascript("(function(){var id='hadotaScanHint',n=document.getElementById(id);if(!n){n=document.createElement('div');n.id=id;n.style='position:fixed;z-index:2147483647;top:112px;right:8px;left:8px;padding:14px;background:#152536;color:#f4dfad;border:2px solid #d9b36a;border-radius:12px;font:bold 15px sans-serif;line-height:1.7;direction:rtl;box-shadow:0 4px 20px #000';document.body.appendChild(n)}n.textContent=" + org.json.JSONObject.quote(note) + ";return true})()", null);
                                return;
                            }
                        } catch (Exception ignored) { result.putExtra("router_devices", "[]"); }
                        setResult(RESULT_OK, result);
                        finish();"""
if old not in s:
    raise SystemExit("Could not find empty-scan return block in RouterActivity.java")
s = s.replace(old, new, 1)
router.write_text(s, encoding="utf-8")

gradle = root / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g, a = re.subn(r"versionCode\s+\d+", "versionCode 58", g, count=1)
g, b = re.subn(r"versionName\s+'[^']+'", "versionName '1.9.23'", g, count=1)
if a != 1 or b != 1:
    raise SystemExit("Could not update app version to 1.9.23")
gradle.write_text(g, encoding="utf-8")
print("v1.9.23: keep router panel open when scan finds no clients; show manual WLAN/LAN status-page guidance")
