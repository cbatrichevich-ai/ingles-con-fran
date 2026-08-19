from pathlib import Path
import re

ROOT=Path('project')

# Identidad independiente: no reemplaza ni toca la APK original publicada.
for p in [ROOT/'app/build.gradle', ROOT/'app/build.gradle.kts']:
    if p.exists():
        s=p.read_text(encoding='utf-8')
        s=s.replace('com.inglesconfran.app','com.inglesconfran.jugamos')
        p.write_text(s,encoding='utf-8')

strings=ROOT/'app/src/main/res/values/strings.xml'
if strings.exists():
    s=strings.read_text(encoding='utf-8')
    s=re.sub(r'(<string name="app_name">).*?(</string>)',r'\1Inglés con Fran - Jugamos\2',s,flags=re.S)
    strings.write_text(s,encoding='utf-8')

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if manifest.exists():
    s=manifest.read_text(encoding='utf-8')
    s=s.replace('com.inglesconfran.app','com.inglesconfran.jugamos')
    manifest.write_text(s,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.parent.mkdir(parents=True,exist_ok=True)
java.write_text(r'''package com.inglesconfran.jugamos;

import android.app.Activity;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.util.Locale;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private WebView webView;
    private TextToSpeech tts;
    private boolean ttsReady=false;

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
        tts=new TextToSpeech(this,this);
        webView.loadUrl("file:///android_asset/www/JUGAMOS.html");
    }

    @Override public void onInit(int status){
        if(status==TextToSpeech.SUCCESS){
            int r=tts.setLanguage(Locale.US);
            ttsReady=(r!=TextToSpeech.LANG_MISSING_DATA && r!=TextToSpeech.LANG_NOT_SUPPORTED);
            if(ttsReady){ tts.setSpeechRate(0.82f); tts.setPitch(1.04f); }
        }
    }

    public class VoiceBridge {
        @JavascriptInterface public void speak(String text){ speakNow(text,1.04f,0.82f); }
        @JavascriptInterface public void praise(String text){ speakNow(text,1.12f,0.90f); }
        @JavascriptInterface public void stop(){ runOnUiThread(()->{ if(tts!=null) tts.stop(); }); }
    }

    private void speakNow(final String text, final float pitch, final float rate){
        runOnUiThread(()->{
            if(tts==null || !ttsReady || text==null) return;
            tts.setPitch(pitch); tts.setSpeechRate(rate);
            tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"jugamos");
        });
    }

    @Override public void onBackPressed(){ if(webView!=null && webView.canGoBack()) webView.goBack(); else super.onBackPressed(); }
    @Override protected void onDestroy(){ if(tts!=null){tts.stop();tts.shutdown();} if(webView!=null) webView.destroy(); super.onDestroy(); }
}
''',encoding='utf-8')

www=ROOT/'app/src/main/assets/www'
www.mkdir(parents=True,exist_ok=True)
html=www/'JUGAMOS.html'
html.write_text(r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Inglés con Fran - Jugamos</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;font-family:Arial,sans-serif;background:#f4fbff;color:#17324d;overflow:hidden}.screen{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:22px}.hidden{display:none!important}
.logo{font-size:clamp(34px,5vw,64px);font-weight:900;margin:0 0 6px}.sub{font-size:clamp(18px,2.2vw,28px);font-weight:700;margin-bottom:26px}.hero{font-size:clamp(72px,10vw,132px);margin:2px}.bigbtn{border:0;border-radius:28px;padding:18px 42px;font-size:clamp(24px,3vw,38px);font-weight:900;box-shadow:0 9px 0 #b4c8d7;background:white;color:#17324d;cursor:pointer}.bigbtn:active{transform:translateY(5px);box-shadow:0 4px 0 #b4c8d7}
.top{width:100%;display:flex;align-items:center;justify-content:space-between;gap:14px}.round{font-size:clamp(18px,2vw,26px);font-weight:900}.stars{font-size:clamp(22px,2.7vw,34px);letter-spacing:4px}.prompt{font-size:clamp(28px,4vw,52px);font-weight:900;margin:8px 0 16px;text-align:center}.listen{border:0;border-radius:22px;background:white;padding:10px 22px;font-size:clamp(18px,2.2vw,28px);font-weight:900;box-shadow:0 5px 0 #b4c8d7}
.grid{width:min(94vw,1050px);height:min(62vh,520px);display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:18px}.card{border:0;border-radius:30px;background:white;box-shadow:0 9px 0 #c7dce8;font-size:clamp(64px,9vw,125px);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.15s transform}.card:active{transform:scale(.96)}.card.good{outline:8px solid #55c878;animation:pop .55s ease}.card.bad{animation:shake .32s ease}.feedback{height:54px;font-size:clamp(22px,3vw,38px);font-weight:900;margin-top:10px}.finish .hero{animation:pop 1s ease infinite alternate}.small{font-size:clamp(17px,2vw,25px);font-weight:700;margin:10px 0 22px;text-align:center}
@keyframes pop{0%{transform:scale(.9)}70%{transform:scale(1.08)}100%{transform:scale(1)}}@keyframes shake{0%,100%{transform:translateX(0)}30%{transform:translateX(-14px)}70%{transform:translateX(14px)}}
</style></head><body>
<section id="home" class="screen"><div class="hero">🎮🦖</div><h1 class="logo">Inglés con Fran</h1><div class="sub">¡Jugamos!</div><button class="bigbtn" onclick="startGame()">JUGAR</button><div class="small">Escuchá y encontrá la imagen.</div></section>
<section id="game" class="screen hidden"><div class="top"><div id="round" class="round"></div><button class="listen" onclick="sayPrompt()">🔊 OTRA VEZ</button><div id="stars" class="stars"></div></div><div id="prompt" class="prompt">Escuchá…</div><div id="grid" class="grid"></div><div id="feedback" class="feedback"></div></section>
<section id="finish" class="screen finish hidden"><div class="hero">🏆⭐</div><h1 class="logo">¡Muy bien!</h1><div id="finalText" class="sub"></div><button class="bigbtn" onclick="startGame()">OTRA PARTIDA</button></section>
<script>
const ITEMS=[
 {w:'cat',e:'🐱'},{w:'dog',e:'🐶'},{w:'lion',e:'🦁'},{w:'fish',e:'🐟'},
 {w:'red',e:'🔴'},{w:'blue',e:'🔵'},{w:'green',e:'🟢'},{w:'yellow',e:'🟡'},
 {w:'one',e:'1️⃣'},{w:'two',e:'2️⃣'},{w:'three',e:'3️⃣'},{w:'four',e:'4️⃣'},
 {w:'apple',e:'🍎'},{w:'car',e:'🚗'},{w:'house',e:'🏠'},{w:'book',e:'📘'},
 {w:'hand',e:'✋'},{w:'eye',e:'👁️'},{w:'nose',e:'👃'},{w:'foot',e:'🦶'},
 {w:'sun',e:'☀️'},{w:'moon',e:'🌙'},{w:'star',e:'⭐'},{w:'rocket',e:'🚀'}];
let deck=[],index=0,score=0,locked=false,current=null;
const $=id=>document.getElementById(id);
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function voice(text,praise=false){try{if(window.AndroidVoice){praise?AndroidVoice.praise(text):AndroidVoice.speak(text);return}}catch(e){} if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='en-US';u.rate=.82;u.pitch=praise?1.12:1.04;speechSynthesis.speak(u)}}
function show(id){['home','game','finish'].forEach(x=>$(x).classList.toggle('hidden',x!==id))}
function startGame(){deck=shuffle([...ITEMS]).slice(0,10);index=0;score=0;locked=false;show('game');nextRound()}
function nextRound(){if(index>=deck.length){finish();return}locked=false;current=deck[index];$('round').textContent=`Desafío ${index+1} de ${deck.length}`;$('stars').textContent='⭐'.repeat(score);$('feedback').textContent='';$('prompt').textContent='Escuchá…';const others=shuffle(ITEMS.filter(x=>x.w!==current.w)).slice(0,3);const options=shuffle([current,...others]);$('grid').innerHTML='';options.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;b.setAttribute('aria-label',o.w);b.onclick=()=>choose(b,o);$('grid').appendChild(b)});setTimeout(sayPrompt,350)}
function sayPrompt(){if(!current)return;$('prompt').textContent='🔊 Find the '+current.w+'!';voice('Find the '+current.w)}
function choose(btn,item){if(locked)return;if(item.w===current.w){locked=true;btn.classList.add('good');score++;$('feedback').textContent='⭐ ¡MUY BIEN!';$('stars').textContent='⭐'.repeat(score);voice('Great job!',true);index++;setTimeout(nextRound,900)}else{btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';voice('Try again',true)}}
function finish(){show('finish');$('finalText').textContent=`Conseguiste ${score} estrellas` ;voice('Fantastic! Great job!',true)}
</script></body></html>''',encoding='utf-8')
print('JUGAMOS preparado: APK independiente, juego de 10 rondas, TTS inglés nativo, sin micrófono y sin nuevas grabaciones.')
