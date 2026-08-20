from pathlib import Path
import re

ROOT=Path('project')
PACKAGE_OLD='com.inglesconfran.app'
PACKAGE_NEW='com.inglesconfran.habla'

for p in [ROOT/'app/build.gradle', ROOT/'app/build.gradle.kts']:
    if p.exists():
        s=p.read_text(encoding='utf-8')
        s=s.replace(PACKAGE_OLD,PACKAGE_NEW)
        p.write_text(s,encoding='utf-8')

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if not manifest.exists():
    raise SystemExit('STOP: AndroidManifest.xml no encontrado')
m=manifest.read_text(encoding='utf-8')
m=m.replace(PACKAGE_OLD,PACKAGE_NEW)
m=re.sub(r'\s*<uses-permission[^>]*android.permission.RECORD_AUDIO[^>]*/>','',m)
if re.search(r'android:label="[^"]+"',m):
    m=re.sub(r'android:label="[^"]+"','android:label="Fran Habla"',m,count=1)
else:
    m=m.replace('<application','<application android:label="Fran Habla"',1)
if re.search(r'android:icon="[^"]+"',m):
    m=re.sub(r'android:icon="[^"]+"','android:icon="@drawable/fran_habla_icon"',m,count=1)
else:
    m=m.replace('<application','<application android:icon="@drawable/fran_habla_icon"',1)
manifest.write_text(m,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.parent.mkdir(parents=True,exist_ok=True)
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
    private TextToSpeech ttsEn, ttsEs;
    private boolean readyEn=false, readyEs=false;
    private int token=0;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        webView=new WebView(this);
        setContentView(webView);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(),"AndroidVoice");
        WebSettings s=webView.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true);
        s.setLoadWithOverviewMode(true); s.setUseWideViewPort(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        ttsEn=new TextToSpeech(this,status->{
            if(status==TextToSpeech.SUCCESS){
                int r=ttsEn.setLanguage(Locale.US);
                readyEn=r!=TextToSpeech.LANG_MISSING_DATA && r!=TextToSpeech.LANG_NOT_SUPPORTED;
                if(readyEn){ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);}
            }
        });
        ttsEs=new TextToSpeech(this,status->{
            if(status==TextToSpeech.SUCCESS){
                int r=ttsEs.setLanguage(new Locale("es","AR"));
                readyEs=r!=TextToSpeech.LANG_MISSING_DATA && r!=TextToSpeech.LANG_NOT_SUPPORTED;
                if(readyEs){ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);}
            }
        });
        webView.loadUrl("file:///android_asset/www/FRAN-HABLA.html");
    }

    public class VoiceBridge {
        @JavascriptInterface public void pair(String en,String es,String callbackId){ speakPair(en,es,callbackId); }
        @JavascriptInterface public void cancel(){ cancelNow(); }
        @JavascriptInterface public void exitApp(){ runOnUiThread(()->{ cancelNow(); finish(); }); }
    }

    private void notifyDone(final String callbackId, final boolean ok){
        if(callbackId==null || webView==null) return;
        runOnUiThread(()->{
            if(webView!=null){
                String js="window.onAndroidAudioDone&&window.onAndroidAudioDone("+JSONObject.quote(callbackId)+","+(ok?"true":"false")+")";
                webView.evaluateJavascript(js,null);
            }
        });
    }

    private void cancelNow(){
        token++;
        if(ttsEn!=null) ttsEn.stop();
        if(ttsEs!=null) ttsEs.stop();
    }

    private void speakPair(final String en, final String es, final String callbackId){
        runOnUiThread(()->{
            cancelNow();
            final int my=token;
            if(!readyEn || ttsEn==null || en==null){ notifyDone(callbackId,false); return; }
            final String enId="habla_en_"+my;
            final String esId="habla_es_"+my;
            ttsEn.setLanguage(Locale.US); ttsEn.setSpeechRate(.92f); ttsEn.setPitch(1.03f);
            ttsEn.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                @Override public void onStart(String id){}
                @Override public void onError(String id){ if(enId.equals(id)) notifyDone(callbackId,false); }
                @Override public void onDone(String id){
                    if(!enId.equals(id)) return;
                    runOnUiThread(()->{
                        if(my!=token){notifyDone(callbackId,false);return;}
                        if(es==null || es.trim().isEmpty() || !readyEs || ttsEs==null){notifyDone(callbackId,true);return;}
                        ttsEs.setLanguage(new Locale("es","AR")); ttsEs.setSpeechRate(.96f); ttsEs.setPitch(1.01f);
                        ttsEs.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                            @Override public void onStart(String id){}
                            @Override public void onError(String id){ if(esId.equals(id)) notifyDone(callbackId,false); }
                            @Override public void onDone(String id){ if(esId.equals(id) && my==token) notifyDone(callbackId,true); }
                        });
                        ttsEs.speak(es,TextToSpeech.QUEUE_FLUSH,null,esId);
                    });
                }
            });
            ttsEn.speak(en,TextToSpeech.QUEUE_FLUSH,null,enId);
        });
    }

    @Override public void onBackPressed(){
        if(webView!=null) webView.evaluateJavascript("handleBack()",null); else super.onBackPressed();
    }

    @Override protected void onDestroy(){
        if(ttsEn!=null){ttsEn.stop();ttsEn.shutdown();}
        if(ttsEs!=null){ttsEs.stop();ttsEs.shutdown();}
        if(webView!=null) webView.destroy();
        super.onDestroy();
    }
}
''',encoding='utf-8')

draw=ROOT/'app/src/main/res/drawable'
draw.mkdir(parents=True,exist_ok=True)
(draw/'fran_habla_icon.xml').write_text(r'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#7A4FD8" android:pathData="M4,4h100v100h-100z"/>
    <path android:fillColor="#FFFFFFFF" android:pathData="M20,24h68c6,0 10,4 10,10v32c0,6 -4,10 -10,10H58L40,90v-14H20c-6,0 -10,-4 -10,-10V34c0,-6 4,-10 10,-10z"/>
    <path android:fillColor="#7A4FD8" android:pathData="M29,43h50v7H29z M29,56h38v7H29z"/>
</vector>
''',encoding='utf-8')

www=ROOT/'app/src/main/assets/www'
www.mkdir(parents=True,exist_ok=True)
html=www/'FRAN-HABLA.html'
html.write_text(r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Fran Habla</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;font-family:Arial,sans-serif;background:linear-gradient(145deg,#f7f1ff,#edf8ff);color:#20324a;overflow:hidden}.screen{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px}.hidden{display:none!important}button{font:inherit;cursor:pointer}.hero{font-size:clamp(60px,8vw,110px);line-height:1}.title{font-size:clamp(34px,5vw,62px);font-weight:900;margin:4px 0}.sub{font-size:clamp(16px,2vw,24px);font-weight:800;margin:0 0 16px}.game-menu{width:min(94vw,960px);display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.tile{border:0;border-radius:24px;background:white;box-shadow:0 7px 0 #d7c9ef;padding:14px 8px;min-height:132px;font-weight:900;color:#20324a}.tile .ico{font-size:clamp(42px,6vw,72px);display:block;line-height:1}.tile .txt{display:block;font-size:clamp(16px,2vw,24px);margin-top:6px}.exit{border:0;border-radius:16px;background:#e85c63;color:white;font-weight:900;padding:9px 18px;margin-top:14px;box-shadow:0 4px 0 #c84a50}
.top{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:44px}.top button{border:0;border-radius:14px;background:white;box-shadow:0 4px 0 #d7c9ef;padding:8px 14px;font-weight:900;color:#20324a}.family{font-size:clamp(18px,2.4vw,30px);font-weight:900}.builder{width:min(96vw,1050px);flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:6px}.starter-row{display:flex;align-items:center;justify-content:center;gap:10px;margin:3px 0 8px}.starter{background:#7A4FD8;color:white;border-radius:22px;padding:12px 20px;box-shadow:0 6px 0 #5d38b3;text-align:center;min-width:210px}.starter .en{font-size:clamp(24px,3.2vw,40px);font-weight:900;line-height:1}.starter .es{font-size:clamp(13px,1.7vw,19px);font-weight:800;margin-top:4px}.plus{font-size:clamp(28px,4vw,46px);font-weight:900}.options{width:min(94vw,980px);display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.option{border:0;border-radius:22px;background:white;box-shadow:0 6px 0 #ccdcea;padding:10px 6px;min-height:150px}.option .ico{font-size:clamp(48px,7vw,82px);display:block;line-height:1}.option .en{font-size:clamp(14px,1.8vw,20px);font-weight:900;margin-top:7px}.option .es{font-size:clamp(11px,1.4vw,16px);font-weight:700;color:#61758a;margin-top:2px}.phrase{width:min(94vw,920px);background:white;border-radius:24px;padding:10px 18px;margin-top:10px;box-shadow:0 6px 0 #d8e2eb;text-align:center;min-height:92px;display:flex;align-items:center;justify-content:center;gap:12px}.phrase .bigico{font-size:clamp(44px,6vw,70px)}.phrase .words{text-align:left}.phrase .full-en{font-size:clamp(23px,3vw,38px);font-weight:900;line-height:1}.phrase .full-es{font-size:clamp(14px,1.8vw,20px);font-weight:800;color:#5b7084;margin-top:5px}.turn{margin-top:8px;border-radius:18px;background:#fff1a8;padding:8px 18px;font-size:clamp(20px,2.7vw,34px);font-weight:900;box-shadow:0 5px 0 #dbc963;animation:pulse .7s ease-in-out infinite alternate}.hint{font-size:13px;font-weight:700;color:#687b8f;margin-top:5px}.selected{outline:6px solid #7A4FD8;transform:translateY(3px);box-shadow:0 3px 0 #ccdcea}@keyframes pulse{from{transform:scale(.98)}to{transform:scale(1.03)}}
@media(max-height:500px){.screen{padding:5px 8px}.hero{font-size:42px}.title{font-size:27px;margin:1px 0}.sub{font-size:13px;margin:1px 0 6px}.game-menu{width:min(96vw,860px);gap:6px}.tile{min-height:78px;border-radius:14px;padding:5px;box-shadow:0 3px 0 #d7c9ef}.tile .ico{font-size:30px}.tile .txt{font-size:12px;margin-top:3px}.exit{padding:5px 11px;font-size:12px;margin-top:6px}.top{min-height:32px}.top button{padding:5px 8px;font-size:12px;border-radius:10px;box-shadow:0 3px 0 #d7c9ef}.family{font-size:16px}.builder{padding-top:1px}.starter-row{margin:1px 0 4px;gap:6px}.starter{padding:6px 10px;border-radius:13px;min-width:160px;box-shadow:0 3px 0 #5d38b3}.starter .en{font-size:20px}.starter .es{font-size:11px;margin-top:2px}.plus{font-size:23px}.options{gap:6px;width:min(96vw,900px)}.option{min-height:88px;border-radius:13px;padding:4px;box-shadow:0 3px 0 #ccdcea}.option .ico{font-size:36px}.option .en{font-size:11px;margin-top:3px}.option .es{font-size:9px;margin-top:1px}.phrase{margin-top:5px;min-height:62px;padding:5px 10px;border-radius:14px;box-shadow:0 3px 0 #d8e2eb}.phrase .bigico{font-size:36px}.phrase .full-en{font-size:20px}.phrase .full-es{font-size:11px;margin-top:2px}.turn{margin-top:4px;padding:4px 11px;font-size:17px;border-radius:11px;box-shadow:0 3px 0 #dbc963}.hint{display:none}}
</style></head><body>
<section id="home" class="screen"><div class="hero">🗣️💬</div><div class="title">Fran Habla</div><div class="sub">Armá una frase. Escuchala. Decila vos.</div><div id="menu" class="game-menu"></div><button class="exit" onclick="closeApp()">✕ CERRAR APP</button></section>
<section id="builderScreen" class="screen hidden"><div class="top"><button onclick="goHome()">⬅ MENÚ</button><div id="family" class="family"></div><button onclick="repeatPhrase()">🔊 OTRA VEZ</button></div><div class="builder"><div class="starter-row"><div id="starter" class="starter"></div><div class="plus">＋</div></div><div id="options" class="options"></div><div id="phrase" class="phrase hidden"></div><div id="turn" class="turn hidden">🗣️ AHORA VOS</div><div class="hint">Podés elegir otra imagen y armar otra frase.</div></div></section>
<script>
const CATS={
 want:{icon:'💬',label:'QUIERO',enStart:'I want…',esStart:'Quiero…',opts:[
  {i:'💧',en:'water',es:'agua',fEn:'I want water',fEs:'Quiero agua'},
  {i:'🍎',en:'an apple',es:'una manzana',fEn:'I want an apple',fEs:'Quiero una manzana'},
  {i:'🎮',en:'to play',es:'jugar',fEn:'I want to play',fEs:'Quiero jugar'},
  {i:'😴',en:'to sleep',es:'dormir',fEn:'I want to sleep',fEs:'Quiero dormir'}]},
 like:{icon:'❤️',label:'ME GUSTA',enStart:'I like…',esStart:'Me gusta…',opts:[
  {i:'🐱',en:'cats',es:'los gatos',fEn:'I like cats',fEs:'Me gustan los gatos'},
  {i:'🦖',en:'dinosaurs',es:'los dinosaurios',fEn:'I like dinosaurs',fEs:'Me gustan los dinosaurios'},
  {i:'🚀',en:'space',es:'el espacio',fEn:'I like space',fEs:'Me gusta el espacio'},
  {i:'🎵',en:'music',es:'la música',fEn:'I like music',fEs:'Me gusta la música'}]},
 am:{icon:'🙂',label:'ESTOY',enStart:'I am…',esStart:'Estoy…',opts:[
  {i:'😊',en:'happy',es:'contento',fEn:'I am happy',fEs:'Estoy contento'},
  {i:'🍽️',en:'hungry',es:'con hambre',fEn:'I am hungry',fEs:'Tengo hambre'},
  {i:'🥱',en:'tired',es:'cansado',fEn:'I am tired',fEs:'Estoy cansado'},
  {i:'👍',en:'fine',es:'bien',fEn:'I am fine',fEs:'Estoy bien'}]},
 need:{icon:'🙋',label:'NECESITO',enStart:'I need…',esStart:'Necesito…',opts:[
  {i:'🆘',en:'help',es:'ayuda',fEn:'I need help',fEs:'Necesito ayuda'},
  {i:'💧',en:'water',es:'agua',fEn:'I need water',fEs:'Necesito agua'},
  {i:'⏸️',en:'a break',es:'un descanso',fEn:'I need a break',fEs:'Necesito un descanso'},
  {i:'🚻',en:'the bathroom',es:'ir al baño',fEn:'I need the bathroom',fEs:'Necesito ir al baño'}]},
 can:{icon:'✋',label:'¿PUEDO?',enStart:'Can I…?',esStart:'¿Puedo…?',opts:[
  {i:'🎮',en:'play?',es:'jugar?',fEn:'Can I play?',fEs:'¿Puedo jugar?'},
  {i:'🌳',en:'go outside?',es:'salir?',fEn:'Can I go outside?',fEs:'¿Puedo salir?'},
  {i:'📺',en:'watch TV?',es:'ver la tele?',fEn:'Can I watch TV?',fEs:'¿Puedo ver la tele?'},
  {i:'🥤',en:'have water?',es:'tomar agua?',fEn:'Can I have water?',fEs:'¿Puedo tomar agua?'}]},
 daily:{icon:'☀️',label:'TODOS LOS DÍAS',enStart:'Everyday',esStart:'Todos los días',opts:[
  {i:'🌞',en:'Good morning',es:'Buen día',fEn:'Good morning',fEs:'Buen día'},
  {i:'🙏',en:'Thank you',es:'Gracias',fEn:'Thank you',fEs:'Gracias'},
  {i:'🤲',en:'Please',es:'Por favor',fEn:'Please',fEs:'Por favor'},
  {i:'💛',en:"I'm sorry",es:'Perdón',fEn:"I'm sorry",fEs:'Perdón'}]}
};
const $=id=>document.getElementById(id);let currentCat=null,currentOpt=null,audioSeq=0,audioWaiters=new Map();
function renderMenu(){const m=$('menu');m.innerHTML='';Object.entries(CATS).forEach(([k,c])=>{const b=document.createElement('button');b.className='tile';b.innerHTML=`<span class="ico">${c.icon}</span><span class="txt">${c.label}</span>`;b.onclick=()=>openCategory(k);m.appendChild(b)})}
function show(id){['home','builderScreen'].forEach(x=>$(x).classList.toggle('hidden',x!==id))}
function esc(t){return String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function cancelAudio(){try{if(window.AndroidVoice&&AndroidVoice.cancel)AndroidVoice.cancel()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel();for(const r of audioWaiters.values())r(false);audioWaiters.clear()}
function onAndroidAudioDone(id,ok){const r=audioWaiters.get(String(id));if(r){audioWaiters.delete(String(id));r(!!ok)}}
function browserPair(en,es){return new Promise(resolve=>{if(!('speechSynthesis'in window)){resolve(true);return}speechSynthesis.cancel();const a=new SpeechSynthesisUtterance(en);a.lang='en-US';a.rate=.92;a.onend=()=>{const b=new SpeechSynthesisUtterance(es);b.lang='es-AR';b.rate=.96;b.onend=()=>resolve(true);b.onerror=()=>resolve(false);speechSynthesis.speak(b)};a.onerror=()=>resolve(false);speechSynthesis.speak(a)})}
function sayPair(en,es){cancelAudio();return new Promise(resolve=>{const id=String(++audioSeq);try{if(window.AndroidVoice&&AndroidVoice.pair){audioWaiters.set(id,resolve);AndroidVoice.pair(en,es,id);return}}catch(e){audioWaiters.delete(id)}browserPair(en,es).then(resolve)})}
function openCategory(k){cancelAudio();currentCat=k;currentOpt=null;const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class="en">${esc(c.enStart)}</div><div class="es">${esc(c.esStart)}</div>`;$('phrase').classList.add('hidden');$('turn').classList.add('hidden');const o=$('options');o.innerHTML='';c.opts.forEach((x,i)=>{const b=document.createElement('button');b.className='option';b.innerHTML=`<span class="ico">${x.i}</span><div class="en">${esc(x.en)}</div><div class="es">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)});show('builderScreen')}
function choosePhrase(i,btn){const c=CATS[currentCat],x=c.opts[i];currentOpt=i;[...document.querySelectorAll('.option')].forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');$('phrase').innerHTML=`<div class="bigico">${x.i}</div><div class="words"><div class="full-en">${esc(x.fEn)}</div><div class="full-es">${esc(x.fEs)}</div></div>`;$('phrase').classList.remove('hidden');$('turn').classList.add('hidden');sayPair(x.fEn,x.fEs).then(ok=>{if(ok&&currentCat&&currentOpt===i)$('turn').classList.remove('hidden')})}
function repeatPhrase(){if(currentCat==null||currentOpt==null)return;const x=CATS[currentCat].opts[currentOpt];$('turn').classList.add('hidden');sayPair(x.fEn,x.fEs).then(ok=>{if(ok)$('turn').classList.remove('hidden')})}
function goHome(){cancelAudio();currentCat=null;currentOpt=null;show('home')}
function closeApp(){cancelAudio();try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}
function handleBack(){if(!$('builderScreen').classList.contains('hidden'))goHome();else closeApp()}
renderMenu();
</script></body></html>''',encoding='utf-8')

print('FRAN HABLA generado: 6 familias, 24 frases cotidianas, construcción visual, audio EN->ES rápido y turno oral sin micrófono.')
