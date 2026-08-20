from pathlib import Path
import re

ROOT=Path('project')
manifest=ROOT/'app/src/main/AndroidManifest.xml'
java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=ROOT/'app/src/main/assets/www/FRAN-HABLA.html'
if not manifest.exists() or not java.exists() or not html.exists():
    raise SystemExit('STOP: faltan archivos de Fran Habla')

# La versión guiada no finge reconocimiento: no pide permiso de micrófono.
m=manifest.read_text(encoding='utf-8')
m=re.sub(r'\s*<uses-permission[^>]*android.permission.RECORD_AUDIO[^>]*/>','',m)
manifest.write_text(m,encoding='utf-8')

# TTS bilingüe + locución individual para que la teacher conduzca cada turno.
java.write_text(r'''package com.inglesconfran.habla;

import android.app.Activity;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import org.json.JSONObject;
import java.util.Locale;

public class MainActivity extends Activity {
    private WebView webView;
    private TextToSpeech ttsEn,ttsEs;
    private boolean readyEn=false,readyEs=false;
    private int token=0;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        webView=new WebView(this);setContentView(webView);
        webView.setWebViewClient(new WebViewClient());webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(),"AndroidVoice");
        WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setLoadWithOverviewMode(true);s.setUseWideViewPort(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        ttsEn=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEn.setLanguage(Locale.US);readyEn=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(readyEn){ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);}}});
        ttsEs=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEs.setLanguage(new Locale("es","AR"));readyEs=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(readyEs){ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);}}});
        webView.loadUrl("file:///android_asset/www/FRAN-HABLA.html");
    }

    public class VoiceBridge{
        @JavascriptInterface public void pair(String en,String es,String callbackId){speakPair(en,es,callbackId);}
        @JavascriptInterface public void single(String text,String lang,String callbackId){speakSingle(text,lang,callbackId);}
        @JavascriptInterface public void cancel(){cancelNow();}
        @JavascriptInterface public void exitApp(){runOnUiThread(()->{cancelNow();finish();});}
    }

    private void js(String s){if(webView!=null)webView.evaluateJavascript(s,null);}
    private void notifyDone(String id,boolean ok){if(id!=null)js("window.onAndroidAudioDone&&window.onAndroidAudioDone("+JSONObject.quote(id)+","+(ok?"true":"false")+")");}
    private void cancelNow(){token++;if(ttsEn!=null)ttsEn.stop();if(ttsEs!=null)ttsEs.stop();}

    private void speakPair(final String en,final String es,final String callbackId){
        runOnUiThread(()->{
            cancelNow();final int my=token;
            if(!readyEn||ttsEn==null||en==null){notifyDone(callbackId,false);return;}
            final String enId="pair_en_"+my,esId="pair_es_"+my;
            ttsEn.setLanguage(Locale.US);ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);
            ttsEn.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){}public void onError(String id){if(enId.equals(id))notifyDone(callbackId,false);}public void onDone(String id){if(!enId.equals(id))return;runOnUiThread(()->{if(my!=token){notifyDone(callbackId,false);return;}if(es==null||es.trim().isEmpty()||!readyEs||ttsEs==null){notifyDone(callbackId,true);return;}ttsEs.setLanguage(new Locale("es","AR"));ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);ttsEs.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){}public void onError(String id){if(esId.equals(id))notifyDone(callbackId,false);}public void onDone(String id){if(esId.equals(id)&&my==token)notifyDone(callbackId,true);}});ttsEs.speak(es,TextToSpeech.QUEUE_FLUSH,null,esId);});}});
            ttsEn.speak(en,TextToSpeech.QUEUE_FLUSH,null,enId);
        });
    }

    private void speakSingle(final String text,final String lang,final String callbackId){
        runOnUiThread(()->{
            cancelNow();final int my=token;
            final boolean english="en".equalsIgnoreCase(lang);
            final TextToSpeech t=english?ttsEn:ttsEs;
            final boolean ready=english?readyEn:readyEs;
            if(!ready||t==null||text==null){notifyDone(callbackId,false);return;}
            final String id="single_"+(english?"en_":"es_")+my;
            if(english){t.setLanguage(Locale.US);t.setSpeechRate(.92f);t.setPitch(1.03f);}else{t.setLanguage(new Locale("es","AR"));t.setSpeechRate(.96f);t.setPitch(1.01f);}
            t.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String x){}public void onError(String x){if(id.equals(x))notifyDone(callbackId,false);}public void onDone(String x){if(id.equals(x)&&my==token)notifyDone(callbackId,true);}});
            t.speak(text,TextToSpeech.QUEUE_FLUSH,null,id);
        });
    }

    @Override public void onBackPressed(){if(webView!=null)webView.evaluateJavascript("handleBack()",null);else super.onBackPressed();}
    @Override protected void onDestroy(){cancelNow();if(ttsEn!=null)ttsEn.shutdown();if(ttsEs!=null)ttsEs.shutdown();if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

h=html.read_text(encoding='utf-8')
h=h.replace('Dos intentos. Si no sale, seguimos y después volvemos.','La teacher te guía: escuchá, hablá dos veces y seguimos.')
start=h.find("let micPermissionReady=")
end=h.find("function handleBack()",start)
if start<0 or end<0:
    raise SystemExit('STOP: bloque de interacción anterior no encontrado')

new_block=r'''let coachToken=0,sessionVisits={},optionPage=0;
let TURN_WORD_MS=1700,TURN_PHRASE_MS=2400,TURN_END_MS=220;
function setCoach(text,cls=''){const d=$('micStatus');if(!d)return;d.textContent=text||'';d.className='micstatus'+(cls?' '+cls:'')}
function browserSingle(text,lang){return new Promise(resolve=>{if(!('speechSynthesis'in window)){resolve(true);return}speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang=lang==='en'?'en-US':'es-AR';u.rate=lang==='en'?.92:.96;u.onend=()=>resolve(true);u.onerror=()=>resolve(false);speechSynthesis.speak(u)})}
function sayOne(text,lang){cancelAudio();return new Promise(resolve=>{const id=String(++audioSeq);try{if(window.AndroidVoice&&AndroidVoice.single){audioWaiters.set(id,resolve);AndroidVoice.single(text,lang,id);return}}catch(e){audioWaiters.delete(id)}browserSingle(text,lang).then(resolve)})}
function pauseTurn(ms,token){return new Promise(resolve=>setTimeout(()=>resolve(token===coachToken),ms))}
function turnMillis(x){return (x.fEn||'').trim().split(/\s+/).length>2?TURN_PHRASE_MS:TURN_WORD_MS}
async function coachSequence(i,x,token){
  setCoach('👂 Escuchá…');$('turn').classList.add('hidden');
  await sayPair(x.fEn,x.fEs);if(token!==coachToken||currentOpt!==i)return;
  await sayOne('Ahora vos. Decí:','es');if(token!==coachToken||currentOpt!==i)return;
  await sayOne(x.fEn,'en');if(token!==coachToken||currentOpt!==i)return;
  $('turn').textContent='🗣️ AHORA VOS';$('turn').classList.remove('hidden');setCoach('🗣️ Tu turno','listening');
  if(!await pauseTurn(turnMillis(x),token))return;
  $('turn').classList.add('hidden');setCoach('🔁 Una vez más','near');
  await sayOne('Bien. Una vez más:','es');if(token!==coachToken||currentOpt!==i)return;
  await sayOne(x.fEn,'en');if(token!==coachToken||currentOpt!==i)return;
  $('turn').textContent='🗣️ OTRA VEZ';$('turn').classList.remove('hidden');setCoach('🗣️ Una vez más','listening');
  if(!await pauseTurn(turnMillis(x),token))return;
  $('turn').classList.add('hidden');setCoach('⭐ Muy bien por practicar. Seguimos.','good');
  await sayOne('Muy bien por practicar. Seguimos.','es');if(token!==coachToken||currentOpt!==i)return;
  if(!await pauseTurn(TURN_END_MS,token))return;
  advancePhrase();
}
function showOptionIndex(i){if(currentCat==null)return;optionPage=Math.floor(i/4);renderOptionPage();const b=document.querySelector('.option[data-idx="'+i+'"]');if(b)b.click()}
function advancePhrase(){if(currentCat==null)return;const n=CATS[currentCat].opts.length;for(let i=0;i<n;i++){if(!sessionVisits[i]){showOptionIndex(i);return}}setCoach('⭐ ¡Muy bien! Elegí otra familia cuando quieras.','good');sayOne('Muy bien. Terminamos este grupo.','es')}
function renderOptionPage(){if(currentCat==null)return;const c=CATS[currentCat],o=$('options');o.innerHTML='';const start=optionPage*4,end=Math.min(start+4,c.opts.length);for(let i=start;i<end;i++){const x=c.opts[i],b=document.createElement('button');b.className='option';b.dataset.idx=String(i);b.innerHTML=`<span class="ico">${x.i}</span><div class="en">${esc(x.en)}</div><div class="es">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)}const nav=$('pageNav'),pages=Math.ceil(c.opts.length/4);if(pages>1){nav.classList.remove('hidden');$('pageInfo').textContent=(optionPage+1)+' / '+pages}else nav.classList.add('hidden')}
function changeOptionPage(delta){coachToken++;cancelAudio();if(currentCat==null)return;const pages=Math.ceil(CATS[currentCat].opts.length/4);optionPage=Math.max(0,Math.min(pages-1,optionPage+delta));$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setCoach('');renderOptionPage()}
function openCategory(k){coachToken++;cancelAudio();currentCat=k;currentOpt=null;sessionVisits={};optionPage=0;const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class="en">${esc(c.enStart)}</div><div class="es">${esc(c.esStart)}</div>`;const plus=document.querySelector('.plus');if(plus)plus.style.display=c.wordMode?'none':'';$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setCoach('');renderOptionPage();show('builderScreen')}
function choosePhrase(i,btn){coachToken++;cancelAudio();const token=coachToken,c=CATS[currentCat],x=c.opts[i];currentOpt=i;sessionVisits[i]=1;[...document.querySelectorAll('.option')].forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');$('phrase').innerHTML=`<div class="bigico">${x.i}</div><div class="words"><div class="full-en">${esc(x.fEn)}</div><div class="full-es">${esc(x.fEs)}</div></div>`;$('phrase').classList.remove('hidden');coachSequence(i,x,token)}
function repeatPhrase(){if(currentCat==null||currentOpt==null)return;coachToken++;cancelAudio();const token=coachToken,x=CATS[currentCat].opts[currentOpt];coachSequence(currentOpt,x,token)}
function goHome(){coachToken++;cancelAudio();currentCat=null;currentOpt=null;show('home')}
function closeApp(){coachToken++;cancelAudio();try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}
'''
h=h[:start]+new_block+h[end:]
html.write_text(h,encoding='utf-8')
print('FRAN HABLA: teacher oral guía dos turnos cortos, sin reconocimiento ni permiso de micrófono, y avanza automáticamente.')
