from pathlib import Path

java=Path('project/app/src/main/java/com/inglesconfran/app/MainActivity.java')
if not java.exists():
    raise SystemExit('STOP: MainActivity.java no encontrado')
s=java.read_text(encoding='utf-8')
old='private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);}'
new='private void js(String s){runOnUiThread(()->{if(webView!=null)webView.evaluateJavascript(s,null);});}'
if old not in s:
    raise SystemExit('STOP: callback JS esperado no encontrado; no aplicar parche a ciegas')
s=s.replace(old,new,1)
java.write_text(s,encoding='utf-8')
print('FRAN HABLA: callbacks TTS -> WebView enviados siempre por UI thread; la secuencia oral puede continuar después de EN+ES.')
