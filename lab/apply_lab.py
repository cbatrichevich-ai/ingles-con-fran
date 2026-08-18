from pathlib import Path

ROOT=Path('project')
manifest=ROOT/'app/src/main/AndroidManifest.xml'
m=manifest.read_text(encoding='utf-8')
needle='<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
if 'android.permission.RECORD_AUDIO' not in m:
    m=m.replace(needle,needle+'\n    <uses-permission android:name="android.permission.RECORD_AUDIO" />',1)
manifest.write_text(m,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.write_text(r'''package com.inglesconfran.app;
import android.Manifest; import android.app.Activity; import android.content.Intent; import android.content.pm.PackageManager; import android.os.Bundle; import android.speech.RecognitionListener; import android.speech.RecognizerIntent; import android.speech.SpeechRecognizer; import android.view.View; import android.webkit.JavascriptInterface; import android.webkit.WebChromeClient; import android.webkit.WebSettings; import android.webkit.WebView; import android.webkit.WebViewClient; import org.json.JSONObject; import java.util.ArrayList;
public class MainActivity extends Activity {
 private static final int REQ_MIC=41; private WebView webView; private SpeechRecognizer recognizer; private String expected=""; private int listenGeneration=0;
 @Override protected void onCreate(Bundle b){super.onCreate(b);webView=new WebView(this);setContentView(webView);webView.setWebViewClient(new WebViewClient());webView.setWebChromeClient(new WebChromeClient());webView.addJavascriptInterface(new Bridge(),"AndroidSpeech");WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setMediaPlaybackRequiresUserGesture(true);s.setBuiltInZoomControls(false);s.setDisplayZoomControls(false);s.setLoadWithOverviewMode(true);s.setUseWideViewPort(true);webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);webView.loadUrl("file:///android_asset/www/ABRIR-INGLES-CON-FRAN.html");webView.postDelayed(()->ensureMicPermission(),700);}
 private void ensureMicPermission(){if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},REQ_MIC);else js("window.onAndroidPermissionReady&&window.onAndroidPermissionReady()");}
 public class Bridge{
  @JavascriptInterface public void startListening(String e){runOnUiThread(()->begin(e==null?"":e));}
  @JavascriptInterface public void cancelListening(){runOnUiThread(()->cancelCurrent());}
 }
 private void cancelCurrent(){listenGeneration++; if(recognizer!=null){try{recognizer.cancel();}catch(Exception ignored){} try{recognizer.destroy();}catch(Exception ignored){} recognizer=null;}}
 private void begin(String e){expected=e;final int myGen=++listenGeneration;if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){ensureMicPermission();return;}cancelRecognizerOnly();webView.postDelayed(()->{if(myGen==listenGeneration)startRecognizer(myGen);},220);}
 private void cancelRecognizerOnly(){if(recognizer!=null){try{recognizer.cancel();}catch(Exception ignored){} try{recognizer.destroy();}catch(Exception ignored){} recognizer=null;}}
 private void startRecognizer(final int myGen){if(myGen!=listenGeneration)return;if(!SpeechRecognizer.isRecognitionAvailable(this)){err(100,"No hay reconocimiento de voz disponible en este teléfono.");return;}try{recognizer=SpeechRecognizer.createSpeechRecognizer(this);}catch(Exception ex){err(102,"No pude iniciar el reconocimiento de voz.");return;}
 recognizer.setRecognitionListener(new RecognitionListener(){public void onReadyForSpeech(Bundle b){if(myGen==listenGeneration)js("window.onAndroidMicReady&&window.onAndroidMicReady()");}public void onBeginningOfSpeech(){if(myGen==listenGeneration)js("window.onAndroidSpeechStage&&window.onAndroidSpeechStage('Voz detectada')");}public void onRmsChanged(float f){}public void onBufferReceived(byte[] b){}public void onEndOfSpeech(){if(myGen==listenGeneration)js("window.onAndroidSpeechStage&&window.onAndroidSpeechStage('Procesando...')");}public void onError(int e){if(myGen!=listenGeneration)return;String msg=(e==SpeechRecognizer.ERROR_NO_MATCH||e==SpeechRecognizer.ERROR_SPEECH_TIMEOUT)?"No alcancé a entender. Probemos otra vez.":(e==SpeechRecognizer.ERROR_NETWORK||e==SpeechRecognizer.ERROR_NETWORK_TIMEOUT)?"Este teléfono necesita conexión para reconocer la voz.":"No pude escuchar bien. Código Android "+e;err(e,msg);cancelRecognizerOnly();}public void onResults(Bundle b){if(myGen!=listenGeneration)return;ArrayList<String> r=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);float[] c=b.getFloatArray(SpeechRecognizer.CONFIDENCE_SCORES);String joined="";String conf="";if(r!=null)for(int k=0;k<r.size();k++){if(k>0){joined+="|||";conf+="|||";}joined+=r.get(k);conf+=(c!=null&&k<c.length)?String.valueOf(c[k]):"-1";}js("window.onAndroidSpeechResult&&window.onAndroidSpeechResult("+JSONObject.quote(joined)+","+JSONObject.quote(conf)+","+JSONObject.quote(expected)+")");cancelRecognizerOnly();}public void onPartialResults(Bundle b){}public void onEvent(int e,Bundle b){}});
 Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"en-US");i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,7);i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);ArrayList<String> bias=new ArrayList<>();bias.add(expected);i.putStringArrayListExtra(RecognizerIntent.EXTRA_BIASING_STRINGS,bias);try{recognizer.startListening(i);}catch(Exception e){err(103,"No pude abrir el micrófono.");cancelRecognizerOnly();}}
 private void err(int c,String m){js("window.onAndroidSpeechError&&window.onAndroidSpeechError("+c+","+JSONObject.quote(m)+")");}private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);}
 @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_MIC){if(g.length>0&&g[0]==PackageManager.PERMISSION_GRANTED)js("window.onAndroidPermissionReady&&window.onAndroidPermissionReady()");else err(101,"Necesito permiso de micrófono para escucharte.");}}
 @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}@Override protected void onDestroy(){cancelCurrent();if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

htmlp=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
h=htmlp.read_text(encoding='utf-8')
css=".miccue{display:none;margin:12px auto 18px;text-align:center}.miccue.on{display:block}.miccircle{width:128px;height:128px;margin:auto;border-radius:50%;background:#e83472;color:white;display:flex;align-items:center;justify-content:center;font-size:66px;box-shadow:0 10px 30px #e8347245}.miccue.listening .miccircle{animation:micpulse .85s ease-in-out infinite}.miccaption{font-size:20px;font-weight:900;margin-top:8px;color:#e83472}.micdiag{display:none;max-width:520px;margin:10px auto;padding:10px 14px;border-radius:14px;background:#eef7ff;color:#17324d;font-size:15px;font-weight:800}.micdiag.on{display:block}@keyframes micpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}"
if '.miccue{' not in h:h=h.replace('</style>',css+'</style>',1)
old='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="content"></div>'
new='<div id="status" class="status">Elegí un parlante para escuchar.</div><div id="micCue" class="miccue"><div class="miccircle">🎙️</div><div class="miccaption">TU TURNO</div></div><div id="micDiag" class="micdiag"></div><div id="content"></div>'
if old not in h:raise SystemExit('No se encontró contenedor base esperado; STOP técnico')
h=h.replace(old,new,1)
oldfun="async function playContent(file,label,askRepeat=true){document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(askRepeat){await new Promise(r=>setTimeout(r,180));await playFile('187.wav');document.getElementById('status').textContent='🗣️ Ahora vos: '+label}}catch(e){}}"
newfun="""let micPermissionReady=false,currentExpected='',listenTimer=null,listenToken=0;
const ENGLISH_AUDIO_FILES=new Set(Object.values(DATA).flatMap(d=>(d.items||[]).map(it=>it.enAudio)).filter(Boolean));
function micCue(show,listening=false){const m=document.getElementById('micCue');if(!m)return;m.className=show?('miccue on'+(listening?' listening':'')):'miccue'}
function micDiag(text){const d=document.getElementById('micDiag');if(!d)return;d.textContent=text||'';d.className=text?'micdiag on':'micdiag'}
function cancelListen(){listenToken++;if(listenTimer){clearTimeout(listenTimer);listenTimer=null}if(window.AndroidSpeech&&AndroidSpeech.cancelListening)AndroidSpeech.cancelListening();currentExpected='';micCue(false)}
const NUMWORDS={1:'ONE',2:'TWO',3:'THREE',4:'FOUR',5:'FIVE',6:'SIX',7:'SEVEN',8:'EIGHT',9:'NINE',10:'TEN',11:'ELEVEN',12:'TWELVE',13:'THIRTEEN',14:'FOURTEEN',15:'FIFTEEN',16:'SIXTEEN',17:'SEVENTEEN',18:'EIGHTEEN',19:'NINETEEN',20:'TWENTY'};
function expandNumbers(s){return (s||'').replace(/\\b(20|1[0-9]|[1-9])\\b/g,m=>NUMWORDS[Number(m)]||m)}
function normSpeech(s){return expandNumbers(s).toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^A-Z0-9 ]/g,' ').replace(/\\s+/g,' ').trim()}
function compact(s){return normSpeech(s).replace(/ /g,'')}
function editDistance(a,b){a=compact(a);b=compact(b);const dp=Array(b.length+1).fill(0).map((_,j)=>j);for(let i=1;i<=a.length;i++){let prev=dp[0];dp[0]=i;for(let j=1;j<=b.length;j++){const t=dp[j];dp[j]=Math.min(dp[j]+1,dp[j-1]+1,prev+(a[i-1]===b[j-1]?0:1));prev=t}}return dp[b.length]}
function closeEnough(candidate,expected){const c=normSpeech(candidate),w=normSpeech(expected);if(!c||!w)return false;if(c===w)return true;const cc=c.replace(/ /g,''),ww=w.replace(/ /g,'');if(ww==='RED'&&['READ','BREAD'].includes(cc))return true;if(w.split(' ').length===1){const allowance=ww.length<=4?1:(ww.length<=8?2:3);return Math.abs(cc.length-ww.length)<=allowance&&editDistance(c,w)<=allowance}const stop=new Set(['IT','ITS','IS','THE','A','AN','OCLOCK']);const wt=w.split(' ').filter(x=>!stop.has(x));const ct=new Set(c.split(' ').filter(x=>!stop.has(x)));const hits=wt.filter(x=>ct.has(x)).length;if(wt.length&&hits/Math.max(1,wt.length)>=0.6)return true;const maxLen=Math.max(cc.length,ww.length);return maxLen>0&&(1-editDistance(c,w)/maxLen)>=0.62}
function onAndroidPermissionReady(){micPermissionReady=true;micDiag('')}
function requestListen(label,delay=550){const token=++listenToken;currentExpected=label;micCue(true,false);document.getElementById('status').textContent='🎙️ Tu turno: '+label;listenTimer=setTimeout(()=>{listenTimer=null;if(token===listenToken&&window.AndroidSpeech&&AndroidSpeech.startListening)AndroidSpeech.startListening(label)},delay)}
function onAndroidMicReady(){micCue(true,true);document.getElementById('status').textContent='🎙️ Te escucho...';micDiag('')}
function onAndroidSpeechStage(stage){micCue(true,false);micDiag(stage)}
function onAndroidSpeechResult(all,conf,expected){const raw=(all||'').split('|||');const ok=raw.some(x=>closeEnough(x,expected));const heard=raw[0]||'';if(ok){listenToken++;currentExpected='';micCue(false);micDiag('');document.getElementById('status').textContent='✅ ¡Muy bien!'}else{micCue(true,false);document.getElementById('status').textContent='👂 Probemos otra vez';micDiag(heard?('Escuché: '+heard):'No alcancé a entender');requestListen(expected,850)}}
function onAndroidSpeechError(code,message){micCue(true,false);document.getElementById('status').textContent='👂 Probemos otra vez';micDiag(message);if(currentExpected)requestListen(currentExpected,900)}
async function playContent(file,label,askRepeat=true){cancelListen();micDiag('');document.getElementById('status').textContent='👂 Escuchá: '+label;try{await playFile(file);if(ENGLISH_AUDIO_FILES.has(file)){await new Promise(r=>setTimeout(r,300));requestListen(label,450)}}catch(e){}}
"""
if oldfun not in h:raise SystemExit('No se encontró playContent base; STOP técnico')
h=h.replace(oldfun,newfun,1)
h=h.replace("function goHome(){\n  stopAudio();show('home')}","function goHome(){\n  stopAudio();cancelListen();micDiag('');show('home')}",1)
htmlp.write_text(h,encoding='utf-8')
print('REPARACIÓN COMPLETA: cada enAudio real abre micrófono; Hora incluida; escuchas/reintentos anteriores se cancelan; reconocimiento tolerante para números, palabras y frases; español no abre micrófono; 187 preservado.')
