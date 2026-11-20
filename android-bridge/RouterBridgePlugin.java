package com.hadotacafe.wifimanager;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.JSObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
@CapacitorPlugin(name="RouterBridge")
public class RouterBridgePlugin extends Plugin {
 @PluginMethod public void probe(PluginCall call) {
  String host=cleanHost(call.getString("host","192.168.1.1"));
  if(!isPrivate(host)){call.reject("استخدم عنوان IPv4 محلي خاص مثل 192.168.1.1");return;}
  HttpURLConnection c=null;
  try {
   c=(HttpURLConnection)new URL("http://"+host+"/").openConnection();
   c.setRequestMethod("GET"); c.setConnectTimeout(5000); c.setReadTimeout(5000); c.setInstanceFollowRedirects(false);
   int status=c.getResponseCode(); String location=c.getHeaderField("Location");
   JSObject o=new JSObject(); o.put("reachable",true); o.put("httpStatus",status);
   if(location!=null)o.put("redirectLocation",location);
   o.put("message",status>=300&&status<400
    ? "الراوتر متاح، وأعاد توجيه الطلب إلى صفحة الدخول (HTTP "+status+"). لم يتم تسجيل الدخول أو تغيير الإعدادات."
    : "تم الوصول إلى الراوتر (HTTP "+status+"). هذا اختبار اتصال فقط؛ لم يتم تسجيل الدخول أو تغيير الإعدادات.");
   call.resolve(o);
  } catch(Exception e){JSObject o=new JSObject();o.put("reachable",false);o.put("message","تعذر الاتصال: "+e.getMessage());call.resolve(o);}
  finally{if(c!=null)c.disconnect();}
 }
 @PluginMethod public void inspectLogin(PluginCall call) {
  String host=cleanHost(call.getString("host","192.168.1.1"));
  if(!isPrivate(host)){call.reject("عنوان الراوتر المحلي غير صحيح");return;}
  HttpURLConnection c=null;
  try {
   c=(HttpURLConnection)new URL("http://"+host+"/").openConnection();
   c.setRequestMethod("GET"); c.setConnectTimeout(7000); c.setReadTimeout(7000); c.setInstanceFollowRedirects(true);
   int status=c.getResponseCode(); String finalUrl=c.getURL().toString();
   InputStream in=(status>=400?c.getErrorStream():c.getInputStream());
   String html=in==null?"":readLimited(in,180000);
   String title=match(html,"(?is)<title[^>]*>(.*?)</title>");
   Matcher forms=Pattern.compile("(?is)<form\\b([^>]*)>").matcher(html);
   String formInfo="لم يتم العثور على نموذج HTML مباشر؛ قد تكون صفحة الدخول مبنية بجافاسكريبت.";
   if(forms.find()){
    String attrs=forms.group(1);
    String action=attribute(attrs,"action");
    String method=attribute(attrs,"method");
    formInfo="نموذج الدخول: method="+(method.isEmpty()?"GET":method)+", action="+(action.isEmpty()?"(افتراضي)":action);
   }
   Matcher inputs=Pattern.compile("(?is)<input\\b([^>]*)>").matcher(html);
   StringBuilder names=new StringBuilder(); int count=0;
   while(inputs.find()&&count<20){String name=attribute(inputs.group(1),"name");String type=attribute(inputs.group(1),"type");if(!name.isEmpty()){if(count>0)names.append(", ");names.append(name).append(type.isEmpty()?"":" ["+type+"]");count++;}}
   Matcher scripts=Pattern.compile("(?is)<script\\b([^>]*)>").matcher(html);
   StringBuilder scriptPaths=new StringBuilder(); int scriptCount=0;
   while(scripts.find()&&scriptCount<12){String src=attribute(scripts.group(1),"src");if(!src.isEmpty()){if(scriptCount>0)scriptPaths.append(", ");scriptPaths.append(src);scriptCount++;}}
   JSObject o=new JSObject();o.put("httpStatus",status);o.put("finalUrl",finalUrl);o.put("title",title);o.put("form",formInfo);o.put("fields",names.toString());o.put("scriptPaths",scriptPaths.toString());o.put("bytesInspected",html.length());
   o.put("message","تم فحص صفحة الدخول قراءة فقط. "+formInfo+(names.length()>0?" الحقول: "+names:" لا توجد حقول إدخال ظاهرة.")+(scriptPaths.length()>0?" ملفات JavaScript: "+scriptPaths:""));
   call.resolve(o);
  } catch(Exception e){JSObject o=new JSObject();o.put("message","تعذر فحص صفحة الدخول: "+e.getMessage());call.resolve(o);}
  finally{if(c!=null)c.disconnect();}
 }
 @PluginMethod public void inspectScripts(PluginCall call) {
  String host=cleanHost(call.getString("host","192.168.1.1"));
  if(!isPrivate(host)){call.reject("عنوان الراوتر المحلي غير صحيح");return;}
  HttpURLConnection c=null;
  try {
   c=(HttpURLConnection)new URL("http://"+host+"/").openConnection();
   c.setConnectTimeout(7000); c.setReadTimeout(7000); c.setInstanceFollowRedirects(true);
   int status=c.getResponseCode(); InputStream in=status>=400?c.getErrorStream():c.getInputStream();
   String html=in==null?"":readLimited(in,180000); c.disconnect(); c=null;
   Matcher sm=Pattern.compile("(?is)<script\\b([^>]*)>").matcher(html);
   StringBuilder found=new StringBuilder(); int scanned=0, hits=0;
   while(sm.find()&&scanned<12){
    String src=attribute(sm.group(1),"src"); if(src.isEmpty())continue;
    URL scriptUrl=new URL(new URL("http://"+host+"/"),src);
    if(!scriptUrl.getHost().equals(host))continue;
    HttpURLConnection js=(HttpURLConnection)scriptUrl.openConnection();
    js.setConnectTimeout(5000);js.setReadTimeout(5000);js.setInstanceFollowRedirects(true);
    int jsStatus=js.getResponseCode(); InputStream ji=jsStatus>=400?js.getErrorStream():js.getInputStream();
    String body=ji==null?"":readLimited(ji,250000);js.disconnect();scanned++;
    Matcher strings=Pattern.compile("['\\\"]([^'\\\"]{1,180})['\\\"]").matcher(body);
    while(strings.find()&&hits<30){
     String v=strings.group(1);
     if(v.startsWith("/") && v.matches("(?i).*(arp|dhcp|device|wlan|wireless|host|mac|lan|client|login|status|network).*")){
      if(found.indexOf(v)<0){if(hits>0)found.append(", ");found.append(v);hits++;}
     }
    }
   }
   JSObject o=new JSObject();o.put("scriptsScanned",scanned);o.put("candidatePaths",found.toString());
   o.put("message",scanned==0?"لم أتمكن من قراءة ملفات JavaScript المحلية.":"تم فحص "+scanned+" ملفات محلية. مسارات محتملة لصفحات الأجهزة: "+(hits==0?"لم يظهر مسار واضح":found));
   call.resolve(o);
  } catch(Exception e){JSObject o=new JSObject();o.put("message","تعذر تحليل ملفات الراوتر: "+e.getMessage());call.resolve(o);}
  finally{if(c!=null)c.disconnect();}
 }
 private String cleanHost(String host){return host==null?"":host.trim().replaceFirst("^https?://","").replaceAll("/.*$","");}
 private String readLimited(InputStream in,int max)throws Exception{ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buf=new byte[4096];int n;while((n=in.read(buf))>0&&b.size()<max)b.write(buf,0,Math.min(n,max-b.size()));in.close();return new String(b.toByteArray(),StandardCharsets.UTF_8);}
 private String match(String s,String regex){Matcher m=Pattern.compile(regex).matcher(s);return m.find()?m.group(1).replaceAll("<[^>]+>","").trim():"";}
 private String attribute(String s,String key){Matcher m=Pattern.compile("(?is)\\b"+key+"\\s*=\\s*['\"]([^'\"]*)['\"]").matcher(s);return m.find()?m.group(1):"";}
 private boolean isPrivate(String ip){String[] p=ip.split("\\.");if(p.length!=4)return false;int[] n=new int[4];try{for(int i=0;i<4;i++){n[i]=Integer.parseInt(p[i]);if(n[i]<0||n[i]>255)return false;}}catch(Exception e){return false;}return n[0]==10||(n[0]==192&&n[1]==168)||(n[0]==172&&n[1]>=16&&n[1]<=31);}
}