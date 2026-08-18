from pathlib import Path
import wave, math
from array import array

ROOT=Path('project')
manifest=ROOT/'app/src/main/AndroidManifest.xml'
m=manifest.read_text(encoding='utf-8')
needle='<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
if 'android.permission.RECORD_AUDIO' not in m:
    m=m.replace(needle,needle+'\n    <uses-permission android:name="android.permission.RECORD_AUDIO" />',1)
manifest.write_text(m,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.write_text(r'''package com.inglesconfran.app;
import android.Manifest; import android.app.Activity; import android.content.Intent; import android.content.pm.PackageManager; import android.os.Build; import android.os.Bundle; import android.speech.RecognitionListener; import android.speech.RecognizerIntent; import android.speech.SpeechRecognizer; import android.view.View; import android.webkit.JavascriptInterface; import android.webkit.WebChromeClient; import android.webkit.WebSettings; import android.webkit.WebView; import android.webkit.WebViewClient; import org.json.JSONObject; import java.util.ArrayList;
public class MainActivity extends Activity {
 private static final int REQ_MIC=41; private WebView webView; private SpeechRecognizer recognizer; private String expected=""; private boolean usingLocal=false; private boolean retriedNormal=false;
 @Override protected void onCreate(Bundle b){super.onCreate(b);webView=new WebView(this);setContentView(webView);webView.setWebViewClient(new WebViewClient());webView.setWebChromeClient(new WebChromeClient());webView.addJavascriptInterface(new Bridge(),"AndroidSpeech");WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setMediaPlaybackRequiresUserGesture(true);s.setBuiltInZoomControls(false);s.setDisplayZoomControls(false);s.setLoadWithOverviewMode(true);s.setUseWideViewPort(true);webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);webView.loadUrl("file:///android_asset/www/ABRIR-INGLES-CON-FRAN.html");}
 public class Bridge{@JavascriptInterface public void startListening(String e){runOnUiThread(()->begin(e==null?"":e));}}
 private void diag(String stage){js("window.onAndroidSpeechDiag&&window.onAndroidSpeechDiag("+JSONObject.quote(stage)+")");}
 private void begin(String e){expected=e;retriedNormal=false;if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},REQ_MIC);return;}startRecognizer(true);}
 private void startRecognizer(boolean preferLocal){destroyRecognizer();if(!SpeechRecognizer.isRecognitionAvailable(this)){err(100,"No hay servicio de reconocimiento disponible.");return;}usingLocal=false;try{if(preferLocal&&Build.VERSION.SDK_INT>=Build.VERSION_CODES.S&&SpeechRecognizer.isOnDeviceRecognitionAvailable(this)){recognizer=SpeechRecognizer.createOnDeviceSpeechRecognizer(this);usingLocal=true;}else recognizer=SpeechRecognizer.createSpeechRecognizer(this);}catch(Exception e){try{recognizer=SpeechRecognizer.createSpeechRecognizer(this);usingLocal=false;}catch(Exception ex){err(102,"No se pudo crear el reconocedor.");return;}}
 recognizer.setRecognitionListener(new RecognitionListener(){public void onReadyForSpeech(Bundle b){diag("LISTO · Android está escuchando");js("window.onAndroidMicReady&&window.onAndroidMicReady()");}public void onBeginningOfSpeech(){diag("Voz detectada");}public void onRmsChanged(float f){}public void onBufferReceived(byte[] b){}public void onEndOfSpeech(){diag("Procesando...");}public void onError(int e){if(e==SpeechRecognizer.ERROR_LANGUAGE_UNAVAILABLE&&usingLocal&&!retriedNormal){retriedNormal=true;diag("Cambiando al reconocedor normal...");startRecognizer(false);return;}String msg=(e==SpeechRecognizer.ERROR_NO_MATCH||e==SpeechRecognizer.ERROR_SPEECH_TIMEOUT)?"No alcancé a entender. Probemos otra vez.":(e==SpeechRecognizer.ERROR_NETWORK||e==SpeechRecognizer.ERROR_NETWORK_TIMEOUT)?"El reconocimiento necesita conexión en este dispositivo.":"Código Android "+e;err(e,msg);destroyRecognizer();}public void onResults(Bundle b){ArrayList<String> r=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);String joined="";if(r!=null)for(int k=0;k<r.size();k++){if(k>0)joined+="|||";joined+=r.get(k);}js("window.onAndroidSpeechResult&&window.onAndroidSpeechResult("+JSONObject.quote(joined)+","+JSONObject.quote(expected)+")");destroyRecognizer();}public void onPartialResults(Bundle b){}public void onEvent(int e,Bundle b){}});
 Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"en-US");i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,"en-US");i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,5);i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);if(Build.VERSION.SDK_INT>=33){ArrayList<String> bias=new ArrayList<>();bias.add(expected);i.putStringArrayListExtra(RecognizerIntent.EXTRA_BIASING_STRINGS,bias);}try{recognizer.startListening(i);}catch(Exception e){err(103,"No pude abrir el micrófono.");destroyRecognizer();}}
 private void err(int c,String m){js("window.onAndroidSpeechError&&window.onAndroidSpeechError("+c+","+JSONObject.quote(m)+")");}private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);}private void destroyRecognizer(){if(recognizer!=null){try{recognizer.cancel();}catch(Exception ignored){}try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}}
 @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_MIC){if(g.length>0&&g[0]==PackageManager.PERMISSION_GRANTED)js("window.onAndroidPermissionGranted&&window.onAndroidPermissionGranted()");else err(101,"Necesito permiso de micrófono.");}}
 @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}@Override protected void onDestroy(){destroyRecognizer();if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

htmlp=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
h=htmlp.read_text(encoding='utf-8')
css=".miccue{display:none;margin:12px auto 18px;text-align:center}.miccue.on{display:block}.miccircle{width:112px;height:112px;margin:auto;border-radius:50%;background:#e83472;color:white;display:flex;align-items:center;justify-content:center;font-size:58px;box-shadow:0 10px 30px #e8347245}.miccue.listening .miccircle{animation:micpulse 1s ease-in-out infinite}.miccaption{font-size:19px;font-weight:900;margin-top:8px;color:#e83472}.micdiag{display:none;max-width:520px;margin:10px auto;padding:12px 14px;border-radius:14px;background:#fff3c4;color:#3a2b00;font-size:15px;font-weight:800;line-height:1.35}.micdiag.on{display:block}@keyframes micpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}"
if '.miccue{' not in h:h=h.replace('</style>',css+'</style>',1)
old='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="content"></div>'
new='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="micCue" class="miccue"><div class="miccircle">🎙️</div><div class="miccaption">TU TURNO</div></div><div id="micDiag" class="micdiag"></div><div id="content"></div>'
if old not in h:raise SystemExit('No se encontró contenedor base esperado; STOP técnico')
h=h.replace(old,new,1)
oldfun="async function playContent(file,label,askRepeat=true){document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(askRepeat){await new Promise(r=>setTimeout(r,180));await playFile('187.wav');document.getElementById('status').textContent='🗣️ Ahora vos: '+label}}catch(e){}}"
newfun="""function micCue(show,listening=false){const m=document.getElementById('micCue');if(!m)return;m.className=show?('miccue on'+(listening?' listening':'')):'miccue'}
function micDiag(text){const d=document.getElementById('micDiag');if(!d)return;d.textContent=text||'';d.className=text?'micdiag on':'micdiag'}
function normSpeech(s){return(s||'').toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^A-Z0-9 ]/g,'').trim()}
function requestListen(label,delay=700){micCue(true,false);micDiag('Preparado para escucharte...');setTimeout(()=>{if(window.AndroidSpeech&&AndroidSpeech.startListening)AndroidSpeech.startListening(label)},delay)}
async function startRedMic(label){micCue(false);micDiag('');await playFile('prompt_ahora_vos.wav');document.getElementById('status').textContent='🎙️ Tu turno: '+label;requestListen(label,900)}
function onAndroidPermissionGranted(){micCue(true,false);document.getElementById('status').textContent='🎙️ Micrófono autorizado. Tocá RED otra vez.';micDiag('Permiso concedido.')}
function onAndroidSpeechDiag(stage){micCue(true,stage.includes('LISTO'));micDiag(stage)}
function onAndroidMicReady(){micCue(true,true);document.getElementById('status').textContent='🎙️ Te escucho...'}
function onAndroidSpeechResult(all,expected){const opts=(all||'').split('|||').map(normSpeech);const want=normSpeech(expected);const ok=opts.some(x=>x===want||x.split(' ').includes(want));const heard=(all||'').split('|||')[0]||'';if(ok){micCue(false);micDiag('');document.getElementById('status').textContent='✅ ¡Muy bien! Te escuché: '+expected}else{micCue(true,false);document.getElementById('status').textContent='👂 Te escuché: '+heard+' · Probemos otra vez';micDiag('No pasa nada. Decilo otra vez.');requestListen(expected,1100)}}
function onAndroidSpeechError(code,message){micCue(true,false);document.getElementById('status').textContent='🎙️ '+message;micDiag(message);requestListen('RED',1200)}
async function playContent(file,label,askRepeat=true){micCue(false);micDiag('');document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(askRepeat){await new Promise(r=>setTimeout(r,180));if(file==='001.wav')await startRedMic(label);else{await playFile('187.wav');document.getElementById('status').textContent='🗣️ Ahora vos: '+label}}}catch(e){}}"""
if oldfun not in h:raise SystemExit('No se encontró playContent base; STOP técnico')
h=h.replace(oldfun,newfun,1)
h=h.replace("function goHome(){\n  stopAudio();show('home')}","function goHome(){\n  stopAudio();micCue(false);micDiag('');show('home')}",1)
htmlp.write_text(h,encoding='utf-8')

# Extraer "Ahora vos" y reducir el zumbido grave sin tocar 187.wav.
src=ROOT/'app/src/main/assets/www/audio/187.wav';dst=ROOT/'app/src/main/assets/www/audio/prompt_ahora_vos.wav'
with wave.open(str(src),'rb') as w:
    params=w.getparams();rate=w.getframerate();sw=w.getsampwidth();ch=w.getnchannels();raw=w.readframes(w.getnframes())
if sw!=2:raise SystemExit('Formato 187.wav inesperado; STOP técnico')
samples=array('h');samples.frombytes(raw)
start=int(1.00*rate)*ch;end=min(len(samples),int(2.46*rate)*ch);out=samples[start:end]
# Filtro pasa-altos de 120 Hz por canal para atacar el ruido tipo motor.
cut=120.0;dt=1.0/rate;rc=1.0/(2*math.pi*cut);alpha=rc/(rc+dt)
for c in range(ch):
    xp=0.0;yp=0.0
    for i in range(c,len(out),ch):
        x=float(out[i]);y=alpha*(yp+x-xp);xp=x;yp=y;out[i]=max(-32768,min(32767,int(y)))
# Fade y normalización moderada.
peak=max(1,max(abs(x) for x in out));gain=min(1.8,24000.0/peak)
for i in range(len(out)):out[i]=max(-32768,min(32767,int(out[i]*gain)))
fade=int(.035*rate)*ch
for i in range(min(fade,len(out))):out[i]=int(out[i]*(i/max(1,fade)))
for i in range(min(fade,len(out))):out[-1-i]=int(out[-1-i]*(i/max(1,fade)))
with wave.open(str(dst),'wb') as w:w.setparams(params);w.writeframes(out.tobytes())
print('LAB RED: reintento automático, sesgo de reconocimiento a RED, revisión de 5 hipótesis y prompt con filtrado grave; 187 preservado.')
