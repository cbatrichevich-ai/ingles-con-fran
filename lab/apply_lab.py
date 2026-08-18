from pathlib import Path
import wave
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
 private static final int REQ_MIC=41; private WebView webView; private SpeechRecognizer recognizer; private String expected="";
 @Override protected void onCreate(Bundle b){super.onCreate(b);webView=new WebView(this);setContentView(webView);webView.setWebViewClient(new WebViewClient());webView.setWebChromeClient(new WebChromeClient());webView.addJavascriptInterface(new Bridge(),"AndroidSpeech");WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setMediaPlaybackRequiresUserGesture(true);s.setBuiltInZoomControls(false);s.setDisplayZoomControls(false);s.setLoadWithOverviewMode(true);s.setUseWideViewPort(true);webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);webView.loadUrl("file:///android_asset/www/ABRIR-INGLES-CON-FRAN.html");}
 public class Bridge{@JavascriptInterface public void startListening(String e){runOnUiThread(()->begin(e==null?"":e));}}
 private void diag(String stage){js("window.onAndroidSpeechDiag&&window.onAndroidSpeechDiag("+JSONObject.quote(stage)+")");}
 private void begin(String e){expected=e;diag("1 · Pedido de escucha recibido por Android");if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){diag("2 · Falta permiso: Android abre autorización");requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},REQ_MIC);return;}diag("2 · Permiso de micrófono concedido");startRecognizer();}
 private void startRecognizer(){destroyRecognizer();diag("3 · Comprobando servicio de reconocimiento");if(!SpeechRecognizer.isRecognitionAvailable(this)){err(100,"No hay servicio de reconocimiento de voz disponible.");return;}diag("4 · Servicio de reconocimiento disponible");try{if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.S&&SpeechRecognizer.isOnDeviceRecognitionAvailable(this)){diag("5 · Intentando reconocedor local");recognizer=SpeechRecognizer.createOnDeviceSpeechRecognizer(this);}else{diag("5 · Usando reconocedor del dispositivo");recognizer=SpeechRecognizer.createSpeechRecognizer(this);}}catch(Exception e){diag("5B · Falló reconocedor local; usando reconocedor normal");try{recognizer=SpeechRecognizer.createSpeechRecognizer(this);}catch(Exception ex){err(102,"No se pudo crear el reconocedor: "+ex.getClass().getSimpleName());return;}}
 recognizer.setRecognitionListener(new RecognitionListener(){public void onReadyForSpeech(Bundle b){diag("7 · LISTO: Android está escuchando");js("window.onAndroidMicReady&&window.onAndroidMicReady()");}public void onBeginningOfSpeech(){diag("8 · Voz detectada");}public void onRmsChanged(float f){}public void onBufferReceived(byte[] b){}public void onEndOfSpeech(){diag("9 · Fin de voz detectado");}public void onError(int e){String m=(e==SpeechRecognizer.ERROR_NO_MATCH)?"No alcancé a entender. Probemos otra vez.":(e==SpeechRecognizer.ERROR_SPEECH_TIMEOUT)?"No escuché tu voz. Probemos otra vez.":(e==SpeechRecognizer.ERROR_NETWORK||e==SpeechRecognizer.ERROR_NETWORK_TIMEOUT)?"El reconocimiento de voz necesita conexión en este dispositivo.":"Falló el reconocimiento de voz. Código Android "+e;err(e,m);destroyRecognizer();}public void onResults(Bundle b){ArrayList<String> r=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);String h=(r!=null&&!r.isEmpty())?r.get(0):"";diag("10 · Resultado recibido: "+h);js("window.onAndroidSpeechResult&&window.onAndroidSpeechResult("+JSONObject.quote(h)+","+JSONObject.quote(expected)+")");destroyRecognizer();}public void onPartialResults(Bundle b){}public void onEvent(int e,Bundle b){}});
 Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"en-US");i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,"en-US");i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,5);i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);diag("6 · Ejecutando startListening");try{recognizer.startListening(i);}catch(Exception e){err(103,"startListening falló: "+e.getClass().getSimpleName());destroyRecognizer();}}
 private void err(int c,String m){diag("ERROR "+c+" · "+m);js("window.onAndroidSpeechError&&window.onAndroidSpeechError("+c+","+JSONObject.quote(m)+")");} private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);} private void destroyRecognizer(){if(recognizer!=null){try{recognizer.cancel();}catch(Exception ignored){}try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}}
 @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_MIC){if(g.length>0&&g[0]==PackageManager.PERMISSION_GRANTED){diag("2A · Permiso concedido. Volvé a tocar RED para iniciar escucha.");js("window.onAndroidPermissionGranted&&window.onAndroidPermissionGranted()");}else err(101,"Permiso de micrófono rechazado.");}}
 @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();} @Override protected void onDestroy(){destroyRecognizer();if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

htmlp=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
h=htmlp.read_text(encoding='utf-8')
css=".miccue{display:none;margin:12px auto 18px;text-align:center}.miccue.on{display:block}.miccircle{width:112px;height:112px;margin:auto;border-radius:50%;background:#e83472;color:white;display:flex;align-items:center;justify-content:center;font-size:58px;box-shadow:0 10px 30px #e8347245}.miccue.listening .miccircle{animation:micpulse 1s ease-in-out infinite}.miccaption{font-size:19px;font-weight:900;margin-top:8px;color:#e83472}.micdiag{display:none;max-width:520px;margin:10px auto;padding:12px 14px;border-radius:14px;background:#fff3c4;color:#3a2b00;font-size:15px;font-weight:800;line-height:1.35}.micdiag.on{display:block}@keyframes micpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}"
if '.miccue{' not in h: h=h.replace('</style>',css+'</style>',1)
elif '.micdiag{' not in h: h=h.replace('</style>',".micdiag{display:none;max-width:520px;margin:10px auto;padding:12px 14px;border-radius:14px;background:#fff3c4;color:#3a2b00;font-size:15px;font-weight:800;line-height:1.35}.micdiag.on{display:block}</style>",1)
old='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="content"></div>'
new='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="micCue" class="miccue"><div class="miccircle">🎙️</div><div class="miccaption">TU TURNO</div></div><div id="micDiag" class="micdiag"></div><div id="content"></div>'
if 'id="micCue"' not in h: h=h.replace(old,new,1)
elif 'id="micDiag"' not in h: h=h.replace('<div id="micCue" class="miccue"><div class="miccircle">🎙️</div><div class="miccaption">TU TURNO</div></div>','<div id="micCue" class="miccue"><div class="miccircle">🎙️</div><div class="miccaption">TU TURNO</div></div><div id="micDiag" class="micdiag"></div>',1)
prior="""function micCue(show,listening=false){const m=document.getElementById('micCue');if(!m)return;m.className=show?('miccue on'+(listening?' listening':'')):'miccue';}
function normSpeech(s){return (s||'').toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^A-Z0-9 ]/g,'').trim()}
async function startRedMic(label){micCue(false);await playFile('prompt_ahora_vos.wav');micCue(true,false);document.getElementById('status').textContent='🎙️ Tu turno: '+label;await new Promise(r=>setTimeout(r,1200));if(window.AndroidSpeech&&AndroidSpeech.startListening){AndroidSpeech.startListening(label)}else{document.getElementById('status').textContent='🎙️ Prueba de micrófono disponible en Android'}}
function onAndroidPermissionGranted(){micCue(true,false);document.getElementById('status').textContent='🎙️ Micrófono autorizado. Tocá RED otra vez para probar.'}
function onAndroidMicReady(){micCue(true,true);document.getElementById('status').textContent='🎙️ Te escucho...'}
function onAndroidSpeechResult(text,expected){micCue(false);const heard=normSpeech(text),want=normSpeech(expected);if(heard===want||heard.split(' ').includes(want))document.getElementById('status').textContent='✅ ¡Muy bien! Te escuché: '+text;else document.getElementById('status').textContent='👂 Te escuché: '+text+' · Probemos otra vez'}
function onAndroidSpeechError(code,message){micCue(true,false);document.getElementById('status').textContent='🎙️ '+message}
async function playContent(file,label,askRepeat=true){micCue(false);document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(askRepeat){await new Promise(r=>setTimeout(r,180));if(file==='001.wav'){await startRedMic(label)}else{await playFile('187.wav');document.getElementById('status').textContent='🗣️ Ahora vos: '+label}}}catch(e){}}"""
newfun="""function micCue(show,listening=false){const m=document.getElementById('micCue');if(!m)return;m.className=show?('miccue on'+(listening?' listening':'')):'miccue';}
function micDiag(text){const d=document.getElementById('micDiag');if(!d)return;d.textContent=text||'';d.className=text?'micdiag on':'micdiag'}
function normSpeech(s){return (s||'').toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^A-Z0-9 ]/g,'').trim()}
async function startRedMic(label){micCue(false);micDiag('Audio de indicación...');await playFile('prompt_ahora_vos.wav');micCue(true,false);micDiag('Esperando antes de abrir el reconocimiento...');document.getElementById('status').textContent='🎙️ Tu turno: '+label;await new Promise(r=>setTimeout(r,1200));if(window.AndroidSpeech&&AndroidSpeech.startListening){micDiag('Enviando pedido de escucha a Android...');AndroidSpeech.startListening(label)}else{micDiag('ERROR · No existe el puente AndroidSpeech');document.getElementById('status').textContent='🎙️ No se encontró el puente Android'}}
function onAndroidSpeechDiag(stage){micCue(true,stage.includes('LISTO'));micDiag(stage)}
function onAndroidPermissionGranted(){micCue(true,false);micDiag('Permiso concedido. Tocá RED otra vez.');document.getElementById('status').textContent='🎙️ Micrófono autorizado. Tocá RED otra vez.'}
function onAndroidMicReady(){micCue(true,true);document.getElementById('status').textContent='🎙️ Te escucho...'}
function onAndroidSpeechResult(text,expected){micCue(false);const heard=normSpeech(text),want=normSpeech(expected);if(heard===want||heard.split(' ').includes(want))document.getElementById('status').textContent='✅ ¡Muy bien! Te escuché: '+text;else document.getElementById('status').textContent='👂 Te escuché: '+text+' · Probemos otra vez'}
function onAndroidSpeechError(code,message){micCue(true,false);micDiag('ERROR '+code+' · '+message);document.getElementById('status').textContent='🎙️ '+message}
async function playContent(file,label,askRepeat=true){micCue(false);micDiag('');document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(askRepeat){await new Promise(r=>setTimeout(r,180));if(file==='001.wav'){await startRedMic(label)}else{await playFile('187.wav');document.getElementById('status').textContent='🗣️ Ahora vos: '+label}}}catch(e){micDiag('ERROR de audio · '+e)}}"""
if prior not in h: raise SystemExit('No se encontró bloque de laboratorio esperado; STOP técnico')
h=h.replace(prior,newfun,1)
h=h.replace("function goHome(){\n  stopAudio();micCue(false);show('home')}","function goHome(){\n  stopAudio();micCue(false);micDiag('');show('home')}",1)
htmlp.write_text(h,encoding='utf-8')

src=ROOT/'app/src/main/assets/www/audio/187.wav'; dst=ROOT/'app/src/main/assets/www/audio/prompt_ahora_vos.wav'
with wave.open(str(src),'rb') as w:
    params=w.getparams(); rate=w.getframerate(); sw=w.getsampwidth(); ch=w.getnchannels(); raw=w.readframes(w.getnframes())
if sw!=2: raise SystemExit('Formato 187.wav inesperado; STOP técnico')
samples=array('h'); samples.frombytes(raw)
start=int(1.00*rate)*ch; end=min(len(samples),int(2.46*rate)*ch); out=samples[start:end]
fade=int(.025*rate)*ch
for i in range(min(fade,len(out))): out[i]=int(out[i]*(i/max(1,fade)))
for i in range(min(fade,len(out))): out[-1-i]=int(out[-1-i]*(i/max(1,fade)))
with wave.open(str(dst),'wb') as w: w.setparams(params); w.writeframes(out.tobytes())
print('LAB diagnóstico aplicado: RED muestra cada etapa real del SpeechRecognizer; 187 original preservado.')
