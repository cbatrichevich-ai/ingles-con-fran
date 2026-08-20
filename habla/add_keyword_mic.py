from pathlib import Path
import re

ROOT=Path('project')
manifest=ROOT/'app/src/main/AndroidManifest.xml'
m=manifest.read_text(encoding='utf-8')
needle='<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
if 'android.permission.RECORD_AUDIO' not in m:
    m=m.replace(needle,needle+'\n    <uses-permission android:name="android.permission.RECORD_AUDIO" />',1)
manifest.write_text(m,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.write_text(r'''package com.inglesconfran.habla;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int REQ_MIC=41;
    private WebView webView;
    private TextToSpeech ttsEn,ttsEs;
    private boolean readyEn=false,readyEs=false;
    private int audioToken=0,listenGeneration=0;
    private SpeechRecognizer recognizer;
    private String expectedKeyword="";

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        webView=new WebView(this);setContentView(webView);
        webView.setWebViewClient(new WebViewClient());webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(),"AndroidVoice");
        webView.addJavascriptInterface(new SpeechBridge(),"AndroidSpeech");
        WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setLoadWithOverviewMode(true);s.setUseWideViewPort(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        ttsEn=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEn.setLanguage(Locale.US);readyEn=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(readyEn){ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);}}});
        ttsEs=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEs.setLanguage(new Locale("es","AR"));readyEs=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(readyEs){ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);}}});
        webView.loadUrl("file:///android_asset/www/FRAN-HABLA.html");
        webView.postDelayed(()->ensureMicPermission(),650);
    }

    public class VoiceBridge{
        @JavascriptInterface public void pair(String en,String es,String callbackId){speakPair(en,es,callbackId);}
        @JavascriptInterface public void cancel(){cancelAudio();}
        @JavascriptInterface public void exitApp(){runOnUiThread(()->{cancelAll();finish();});}
    }
    public class SpeechBridge{
        @JavascriptInterface public void startListening(String keyword){runOnUiThread(()->beginListening(keyword==null?"":keyword));}
        @JavascriptInterface public void cancelListening(){runOnUiThread(()->cancelRecognizer());}
    }

    private void ensureMicPermission(){if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},REQ_MIC);else js("window.onAndroidPermissionReady&&window.onAndroidPermissionReady()");}
    private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);}
    private void notifyAudio(String id,boolean ok){if(id==null)return;js("window.onAndroidAudioDone&&window.onAndroidAudioDone("+JSONObject.quote(id)+","+(ok?"true":"false")+")");}
    private void cancelAudio(){audioToken++;if(ttsEn!=null)ttsEn.stop();if(ttsEs!=null)ttsEs.stop();}
    private void cancelRecognizer(){listenGeneration++;if(recognizer!=null){try{recognizer.cancel();}catch(Exception ignored){}try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}}
    private void cancelAll(){cancelAudio();cancelRecognizer();}

    private void speakPair(final String en,final String es,final String callbackId){
        runOnUiThread(()->{
            cancelAudio();cancelRecognizer();final int my=audioToken;
            if(!readyEn||ttsEn==null||en==null){notifyAudio(callbackId,false);return;}
            final String enId="habla_en_"+my,esId="habla_es_"+my;
            ttsEn.setLanguage(Locale.US);ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);
            ttsEn.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){}public void onError(String id){if(enId.equals(id))notifyAudio(callbackId,false);}public void onDone(String id){if(!enId.equals(id))return;runOnUiThread(()->{if(my!=audioToken){notifyAudio(callbackId,false);return;}if(es==null||es.trim().isEmpty()||!readyEs||ttsEs==null){notifyAudio(callbackId,true);return;}ttsEs.setLanguage(new Locale("es","AR"));ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);ttsEs.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){}public void onError(String id){if(esId.equals(id))notifyAudio(callbackId,false);}public void onDone(String id){if(esId.equals(id)&&my==audioToken)notifyAudio(callbackId,true);}});ttsEs.speak(es,TextToSpeech.QUEUE_FLUSH,null,esId);});}});
            ttsEn.speak(en,TextToSpeech.QUEUE_FLUSH,null,enId);
        });
    }

    private void beginListening(String keyword){
        expectedKeyword=keyword;final int my=++listenGeneration;
        if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){ensureMicPermission();return;}
        if(!SpeechRecognizer.isRecognitionAvailable(this)){speechError(100,"No hay reconocimiento de voz disponible.");return;}
        if(recognizer!=null){try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}
        recognizer=SpeechRecognizer.createSpeechRecognizer(this);
        recognizer.setRecognitionListener(new RecognitionListener(){
            public void onReadyForSpeech(Bundle b){if(my==listenGeneration)js("window.onAndroidMicReady&&window.onAndroidMicReady()");}
            public void onBeginningOfSpeech(){if(my==listenGeneration)js("window.onAndroidSpeechStage&&window.onAndroidSpeechStage('Te escucho')");}
            public void onRmsChanged(float r){}public void onBufferReceived(byte[] b){}
            public void onEndOfSpeech(){if(my==listenGeneration)js("window.onAndroidSpeechStage&&window.onAndroidSpeechStage('Procesando...')");}
            public void onError(int e){if(my!=listenGeneration)return;String msg=(e==SpeechRecognizer.ERROR_NO_MATCH||e==SpeechRecognizer.ERROR_SPEECH_TIMEOUT)?"No alcancé a entender.":"No pude escuchar bien.";speechError(e,msg);destroyOnly();}
            public void onResults(Bundle b){if(my!=listenGeneration)return;ArrayList<String> r=b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);String joined="";if(r!=null)for(int k=0;k<r.size();k++){if(k>0)joined+="|||";joined+=r.get(k);}js("window.onAndroidSpeechResult&&window.onAndroidSpeechResult("+JSONObject.quote(joined)+","+JSONObject.quote(expectedKeyword)+")");destroyOnly();}
            public void onPartialResults(Bundle b){}public void onEvent(int e,Bundle b){}
        });
        Intent i=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);i.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"en-US");i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,7);i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS,650L);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS,500L);ArrayList<String> bias=new ArrayList<>();bias.add(expectedKeyword);i.putStringArrayListExtra(RecognizerIntent.EXTRA_BIASING_STRINGS,bias);
        try{recognizer.startListening(i);}catch(Exception e){speechError(103,"No pude abrir el micrófono.");destroyOnly();}
    }
    private void destroyOnly(){if(recognizer!=null){try{recognizer.destroy();}catch(Exception ignored){}recognizer=null;}}
    private void speechError(int c,String m){js("window.onAndroidSpeechError&&window.onAndroidSpeechError("+c+","+JSONObject.quote(m)+")");}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_MIC){if(g.length>0&&g[0]==PackageManager.PERMISSION_GRANTED)js("window.onAndroidPermissionReady&&window.onAndroidPermissionReady()");else speechError(101,"Necesito permiso de micrófono para escucharte.");}}
    @Override public void onBackPressed(){if(webView!=null)webView.evaluateJavascript("handleBack()",null);else super.onBackPressed();}
    @Override protected void onDestroy(){cancelAll();if(ttsEn!=null)ttsEn.shutdown();if(ttsEs!=null)ttsEs.shutdown();if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

html=ROOT/'app/src/main/assets/www/FRAN-HABLA.html'
h=html.read_text(encoding='utf-8')
css='''.micstatus{min-height:38px;margin-top:6px;padding:6px 14px;border-radius:14px;font-size:clamp(15px,2vw,22px);font-weight:900;text-align:center}.micstatus.listening{background:#efe7ff;color:#633ab8}.micstatus.good{background:#dff7e4;color:#18733a}.micstatus.near{background:#fff1b8;color:#7a5a00}.micstatus.later{background:#e8f2ff;color:#245d93}@media(max-height:500px){.micstatus{min-height:28px;margin-top:3px;padding:3px 8px;font-size:13px;border-radius:9px}}'''
if '.micstatus{' not in h:h=h.replace('</style>',css+'</style>',1)
old='<div id="turn" class="turn hidden">🗣️ AHORA VOS</div><div class="hint">Podés elegir otra imagen y armar otra frase.</div>'
new='<div id="turn" class="turn hidden">🗣️ AHORA VOS</div><div id="micStatus" class="micstatus"></div><div class="hint">Dos intentos. Si no sale, seguimos y después volvemos.</div>'
if old not in h:raise SystemExit('STOP: no se encontró bloque de turno oral')
h=h.replace(old,new,1)
old_funcs="""function openCategory(k){cancelAudio();currentCat=k;currentOpt=null;const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class=\"en\">${esc(c.enStart)}</div><div class=\"es\">${esc(c.esStart)}</div>`;$('phrase').classList.add('hidden');$('turn').classList.add('hidden');const o=$('options');o.innerHTML='';c.opts.forEach((x,i)=>{const b=document.createElement('button');b.className='option';b.innerHTML=`<span class=\"ico\">${x.i}</span><div class=\"en\">${esc(x.en)}</div><div class=\"es\">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)});show('builderScreen')}
function choosePhrase(i,btn){const c=CATS[currentCat],x=c.opts[i];currentOpt=i;[...document.querySelectorAll('.option')].forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');$('phrase').innerHTML=`<div class=\"bigico\">${x.i}</div><div class=\"words\"><div class=\"full-en\">${esc(x.fEn)}</div><div class=\"full-es\">${esc(x.fEs)}</div></div>`;$('phrase').classList.remove('hidden');$('turn').classList.add('hidden');sayPair(x.fEn,x.fEs).then(ok=>{if(ok&&currentCat&&currentOpt===i)$('turn').classList.remove('hidden')})}
function repeatPhrase(){if(currentCat==null||currentOpt==null)return;const x=CATS[currentCat].opts[currentOpt];$('turn').classList.add('hidden');sayPair(x.fEn,x.fEs).then(ok=>{if(ok)$('turn').classList.remove('hidden')})}
function goHome(){cancelAudio();currentCat=null;currentOpt=null;show('home')}
function closeApp(){cancelAudio();try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}
"""
new_funcs="""let micPermissionReady=false,practiceAttempt=0,currentKeyword='',sessionVisits={},retryQueue=[];
function cancelMic(){try{if(window.AndroidSpeech&&AndroidSpeech.cancelListening)AndroidSpeech.cancelListening()}catch(e){}currentKeyword=''}
function setMic(text,cls=''){const d=$('micStatus');if(!d)return;d.textContent=text||'';d.className='micstatus'+(cls?' '+cls:'')}
function keywordOf(x){let s=(x.en||x.fEn||'').toLowerCase().replace(/[^a-z ]/g,' '),t=s.split(/\\s+/).filter(Boolean);const stop=new Set(['i','m','am','want','an','a','to','the','can','have','go','watch','good','need','like']);t=t.filter(w=>!stop.has(w));return (t[t.length-1]||'').replace(/s$/,'')||'word'}
function normSpeech(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^a-z0-9 ]/g,' ').replace(/\\s+/g,' ').trim()}
function dist(a,b){a=normSpeech(a).replace(/ /g,'');b=normSpeech(b).replace(/ /g,'');const d=Array(b.length+1).fill(0).map((_,j)=>j);for(let i=1;i<=a.length;i++){let p=d[0];d[0]=i;for(let j=1;j<=b.length;j++){const q=d[j];d[j]=Math.min(d[j]+1,d[j-1]+1,p+(a[i-1]===b[j-1]?0:1));p=q}}return d[b.length]}
function gradeSpeech(all,key){const aliases={tv:['tv','television'],bathroom:['bathroom','restroom'],water:['water'],outside:['outside'],sorry:['sorry']};const targets=aliases[key]||[key];const heard=(all||'').split('|||').map(normSpeech).filter(Boolean);for(const h of heard)for(const t of targets){if(h.split(' ').includes(t)||h===t||dist(h,t)<=Math.max(1,Math.floor(t.length*.25)))return 'good'}for(const h of heard)for(const t of targets){if(dist(h,t)<=Math.max(2,Math.floor(t.length*.45)))return 'near'}return 'miss'}
function onAndroidPermissionReady(){micPermissionReady=true;if(currentKeyword)requestListen(currentKeyword)}
function requestListen(key){currentKeyword=key;$('turn').classList.remove('hidden');setMic('🎙️ Te escucho…','listening');try{if(window.AndroidSpeech&&AndroidSpeech.startListening)AndroidSpeech.startListening(key)}catch(e){}}
function onAndroidMicReady(){setMic('🎙️ Te escucho…','listening')}
function onAndroidSpeechStage(s){setMic('🎙️ '+s,'listening')}
function practiceFailed(){const v=sessionVisits[currentOpt]||1;if(v<2&&!retryQueue.includes(currentOpt))retryQueue.push(currentOpt);setMic('La seguimos practicando. Ahora vamos con otra.','later');setTimeout(advancePhrase,650)}
function onAndroidSpeechResult(all,key){const g=gradeSpeech(all,key);if(g==='good'){setMic('✅ ¡Muy bien!','good');currentKeyword='';setTimeout(advancePhrase,600);return}if(practiceAttempt<2){practiceAttempt++;setMic('Casi. Escuchá otra vez: '+key,'near');currentKeyword='';sayPair(key,'').then(()=>requestListen(key));return}currentKeyword='';practiceFailed()}
function onAndroidSpeechError(code,msg){if(!currentKeyword)return;if(practiceAttempt<2){practiceAttempt++;setMic('Probemos una vez más.','near');const k=currentKeyword;currentKeyword='';sayPair(k,'').then(()=>requestListen(k));return}currentKeyword='';practiceFailed()}
function beginPractice(x){practiceAttempt=1;currentKeyword=keywordOf(x);$('turn').classList.remove('hidden');setMic('🎙️ Decí la frase. Voy a escuchar: '+currentKeyword,'listening');requestListen(currentKeyword)}
function advancePhrase(){cancelMic();if(currentCat==null)return;const n=CATS[currentCat].opts.length;for(let i=0;i<n;i++){if(!sessionVisits[i]){document.querySelectorAll('.option')[i].click();return}}while(retryQueue.length){const i=retryQueue.shift();if((sessionVisits[i]||0)<2){document.querySelectorAll('.option')[i].click();return}}setMic('⭐ Muy bien. Elegí otra familia cuando quieras.','good')}
function openCategory(k){cancelAudio();cancelMic();currentCat=k;currentOpt=null;sessionVisits={};retryQueue=[];const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class=\"en\">${esc(c.enStart)}</div><div class=\"es\">${esc(c.esStart)}</div>`;$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setMic('');const o=$('options');o.innerHTML='';c.opts.forEach((x,i)=>{const b=document.createElement('button');b.className='option';b.innerHTML=`<span class=\"ico\">${x.i}</span><div class=\"en\">${esc(x.en)}</div><div class=\"es\">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)});show('builderScreen')}
function choosePhrase(i,btn){cancelMic();const c=CATS[currentCat],x=c.opts[i];currentOpt=i;sessionVisits[i]=(sessionVisits[i]||0)+1;[...document.querySelectorAll('.option')].forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');$('phrase').innerHTML=`<div class=\"bigico\">${x.i}</div><div class=\"words\"><div class=\"full-en\">${esc(x.fEn)}</div><div class=\"full-es\">${esc(x.fEs)}</div></div>`;$('phrase').classList.remove('hidden');$('turn').classList.add('hidden');setMic('👂 Escuchá…');sayPair(x.fEn,x.fEs).then(ok=>{if(ok&&currentCat&&currentOpt===i)beginPractice(x)})}
function repeatPhrase(){if(currentCat==null||currentOpt==null)return;cancelMic();const x=CATS[currentCat].opts[currentOpt];$('turn').classList.add('hidden');setMic('👂 Escuchá…');sayPair(x.fEn,x.fEs).then(ok=>{if(ok)beginPractice(x)})}
function goHome(){cancelAudio();cancelMic();currentCat=null;currentOpt=null;show('home')}
function closeApp(){cancelAudio();cancelMic();try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}
"""
if old_funcs not in h:raise SystemExit('STOP: no se encontró bloque funcional esperado')
h=h.replace(old_funcs,new_funcs,1)
html.write_text(h,encoding='utf-8')
print('FRAN HABLA: micrófono por palabra clave, máximo dos intentos por visita, reintento diferido una sola vez y avance automático.')
