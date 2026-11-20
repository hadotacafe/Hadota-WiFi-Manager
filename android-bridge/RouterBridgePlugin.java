package com.hadotacafe.wifimanager;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.JSObject;
import java.net.HttpURLConnection;
import java.net.URL;
@CapacitorPlugin(name="RouterBridge")
public class RouterBridgePlugin extends Plugin {
 @PluginMethod public void probe(PluginCall call) {
  String host=call.getString("host","192.168.1.1").trim().replaceFirst("^https?://","").replaceAll("/.*$","");
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
 private boolean isPrivate(String ip){String[] p=ip.split("\\.");if(p.length!=4)return false;int[] n=new int[4];try{for(int i=0;i<4;i++){n[i]=Integer.parseInt(p[i]);if(n[i]<0||n[i]>255)return false;}}catch(Exception e){return false;}return n[0]==10||(n[0]==192&&n[1]==168)||(n[0]==172&&n[1]>=16&&n[1]<=31);}
}