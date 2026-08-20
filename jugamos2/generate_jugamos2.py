from pathlib import Path
import re

ROOT=Path('project')
PKG='com.inglesconfran.jugamos2'

for p in [ROOT/'app/build.gradle',ROOT/'app/build.gradle.kts']:
    if p.exists():
        s=p.read_text(encoding='utf-8')
        s=s.replace('com.inglesconfran.app',PKG)
        p.write_text(s,encoding='utf-8')

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if manifest.exists():
    s=manifest.read_text(encoding='utf-8').replace('com.inglesconfran.app',PKG)
    manifest.write_text(s,encoding='utf-8')

strings=ROOT/'app/src/main/res/values/strings.xml'
if strings.exists():
    s=strings.read_text(encoding='utf-8')
    s=re.sub(r'(<string name="app_name">).*?(</string>)',r'\1Inglés con Fran - Más Juegos\2',s,flags=re.S)
    strings.write_text(s,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
java.parent.mkdir(parents=True,exist_ok=True)
java.write_text(r'''package com.inglesconfran.jugamos2;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.util.Locale;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private WebView webView; private TextToSpeech tts; private boolean ready=false; private int token=0;
    @Override public void onCreate(Bundle b){
        super.onCreate(b); webView=new WebView(this); setContentView(webView);
        webView.setWebViewClient(new WebViewClient()); webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(),"AndroidVoice");
        WebSettings s=webView.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true); s.setLoadWithOverviewMode(true); s.setUseWideViewPort(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        tts=new TextToSpeech(this,this); webView.loadUrl("file:///android_asset/www/JUGAMOS2.html");
    }
    @Override public void onInit(int status){if(status==TextToSpeech.SUCCESS){int r=tts.setLanguage(Locale.US);ready=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(ready){tts.setSpeechRate(.70f);tts.setPitch(1.03f);}}}
    public class VoiceBridge{
        @JavascriptInterface public void pair(String en,String es){speakPair(en,es);}
        @JavascriptInterface public void english(String text){speakEnglish(text);}
        @JavascriptInterface public void englishList(String joined){speakEnglishList(joined);}
        @JavascriptInterface public void praise(String text){speakPraise(text);}
        @JavascriptInterface public void cancel(){cancelNow();}
    }
    private void cancelNow(){runOnUiThread(()->{token++;if(tts!=null)tts.stop();});}
    private void speakEnglish(final String text){runOnUiThread(()->{if(!ready||tts==null||text==null)return;token++;tts.stop();tts.setLanguage(Locale.US);tts.setSpeechRate(.70f);tts.setPitch(1.03f);tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"eng_"+token);});}
    private void speakPraise(final String text){runOnUiThread(()->{if(!ready||tts==null||text==null)return;token++;tts.stop();tts.setLanguage(Locale.US);tts.setSpeechRate(.78f);tts.setPitch(1.10f);tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"praise_"+token);});}
    private void speakEnglishList(final String joined){runOnUiThread(()->{if(!ready||tts==null||joined==null)return;final int my=++token;tts.stop();tts.setLanguage(Locale.US);tts.setSpeechRate(.68f);tts.setPitch(1.03f);String[] xs=joined.split("\\|");for(int i=0;i<xs.length;i++){if(my!=token)return;tts.speak(xs[i],i==0?TextToSpeech.QUEUE_FLUSH:TextToSpeech.QUEUE_ADD,null,"list_"+my+"_"+i);}});}
    private void speakPair(final String en,final String es){runOnUiThread(()->{if(!ready||tts==null||en==null)return;final int my=++token;final String id="pair_"+my;tts.stop();tts.setLanguage(Locale.US);tts.setSpeechRate(.68f);tts.setPitch(1.03f);tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){@Override public void onStart(String x){}@Override public void onError(String x){}@Override public void onDone(String x){if(!id.equals(x))return;runOnUiThread(()->{if(my!=token||tts==null||es==null)return;new Handler(Looper.getMainLooper()).postDelayed(()->{if(my!=token||tts==null)return;tts.setLanguage(new Locale("es","AR"));tts.setSpeechRate(.72f);tts.setPitch(1.01f);tts.speak(es,TextToSpeech.QUEUE_FLUSH,null,"es_"+my);},170);});}});tts.speak(en,TextToSpeech.QUEUE_FLUSH,null,id);});}
    @Override public void onBackPressed(){if(webView!=null)webView.evaluateJavascript("exitToHome()",null);else super.onBackPressed();}
    @Override protected void onDestroy(){if(tts!=null){tts.stop();tts.shutdown();}if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

www=ROOT/'app/src/main/assets/www';www.mkdir(parents=True,exist_ok=True)
html=www/'JUGAMOS2.html'
html.write_text(r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>Inglés con Fran - Más Juegos</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:Arial,sans-serif;color:#17324d;background:#eef8ff}.screen{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px}.hidden{display:none!important}button{font-family:inherit}.home{position:relative;overflow:hidden;background:radial-gradient(circle at 14% 22%,#ffe36e 0 7%,transparent 7.5%),radial-gradient(circle at 85% 17%,#86dcff 0 9%,transparent 9.5%),radial-gradient(circle at 80% 83%,#c8a8ff 0 11%,transparent 11.5%),linear-gradient(145deg,#f7fdff,#e8f6ff)}.home:before,.home:after{content:'◆';position:absolute;font-size:90px;color:rgba(255,255,255,.5);transform:rotate(25deg)}.home:before{left:6%;bottom:4%}.home:after{right:5%;top:35%}.mascot{font-size:clamp(62px,8vw,108px);filter:drop-shadow(0 8px 5px rgba(23,50,77,.15));animation:float 2.2s ease-in-out infinite alternate}.title{font-size:clamp(30px,4.2vw,54px);font-weight:1000;margin:2px 0 10px;text-align:center}.game-menu{width:min(92vw,1050px);display:grid;grid-template-columns:repeat(3,1fr);gap:18px;z-index:2}.game-tile{min-height:190px;border:0;border-radius:28px;background:white;box-shadow:0 10px 0 #b9d0df;padding:16px 12px;font-weight:1000;color:#17324d;cursor:pointer}.game-tile:active{transform:translateY(5px);box-shadow:0 5px 0 #b9d0df}.game-icon{font-size:clamp(58px,7vw,92px);display:block}.game-name{font-size:clamp(20px,2.4vw,31px);display:block;margin-top:6px}.top{width:100%;height:52px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex:0 0 52px}.top button{border:0;border-radius:16px;background:white;box-shadow:0 4px 0 #b9d0df;padding:8px 14px;font-size:clamp(15px,1.8vw,22px);font-weight:900}.status{font-size:clamp(17px,2vw,25px);font-weight:900}.prompt{font-size:clamp(24px,3.6vw,44px);font-weight:1000;text-align:center;margin:4px 0 10px;min-height:50px}.feedback{height:34px;font-size:clamp(18px,2.3vw,28px);font-weight:1000;text-align:center;margin-top:5px}
/* Bingo */.bingo{width:min(86vw,760px);height:min(68vh,540px);display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:10px}.bingo-cell{border:0;border-radius:20px;background:white;box-shadow:0 6px 0 #c7dce8;font-size:clamp(40px,6vw,74px);position:relative}.bingo-cell.marked{background:#dff7e6;outline:5px solid #60c97d}.bingo-cell.marked:after{content:'✓';position:absolute;right:8px;top:2px;font-size:.42em;color:#258f48;font-weight:1000}
/* Secuencia */.sequence-stage{width:min(90vw,900px);height:min(40vh,250px);display:flex;align-items:center;justify-content:center;gap:14px}.sequence-flash{width:170px;height:170px;border-radius:28px;background:white;box-shadow:0 7px 0 #c7dce8;display:flex;align-items:center;justify-content:center;font-size:95px;animation:pop .35s ease}.sequence-options{width:min(92vw,900px);display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.sequence-choice{height:120px;border:0;border-radius:20px;background:white;box-shadow:0 5px 0 #c7dce8;font-size:64px}.sequence-slots{display:flex;gap:8px;min-height:48px;align-items:center;justify-content:center}.seq-dot{width:36px;height:36px;border-radius:50%;background:#d5e5ef}.seq-dot.done{background:#6ed28a}
/* Atrápalo */.arena{position:relative;width:min(92vw,980px);height:min(66vh,500px);border-radius:28px;background:linear-gradient(180deg,#dff6ff,#f5fbff);overflow:hidden;box-shadow:inset 0 0 0 4px rgba(124,180,214,.25)}.mover{position:absolute;width:100px;height:100px;border:0;border-radius:50%;background:white;box-shadow:0 6px 0 #c7dce8;font-size:58px;display:flex;align-items:center;justify-content:center;animation:drift var(--dur) ease-in-out infinite alternate}.mover:nth-child(2n){animation-direction:alternate-reverse}.good{outline:6px solid #58c979}.bad{animation:shake .28s ease!important}
.finish-icon{font-size:90px}.finish-title{font-size:44px;font-weight:1000;margin:5px}.homebtn{border:0;border-radius:20px;background:white;box-shadow:0 6px 0 #b9d0df;padding:12px 26px;font-size:24px;font-weight:1000;margin:5px}
@keyframes float{from{transform:translateY(-4px) rotate(-1deg)}to{transform:translateY(6px) rotate(1deg)}}@keyframes pop{0%{transform:scale(.8)}80%{transform:scale(1.08)}100%{transform:scale(1)}}@keyframes shake{0%,100%{transform:translateX(0)}35%{transform:translateX(-10px)}70%{transform:translateX(10px)}}@keyframes drift{from{transform:translate(-10px,-8px) rotate(-4deg)}to{transform:translate(18px,12px) rotate(5deg)}}
@media(max-height:500px){.screen{padding:5px 8px}.mascot{font-size:44px}.title{font-size:25px;margin:0 0 5px}.game-menu{width:min(94vw,820px);gap:9px}.game-tile{min-height:120px;border-radius:18px;padding:7px;box-shadow:0 5px 0 #b9d0df}.game-icon{font-size:48px}.game-name{font-size:18px;margin-top:2px}.top{height:34px;flex-basis:34px}.top button{padding:4px 8px;font-size:14px}.status{font-size:14px}.prompt{font-size:22px;min-height:30px;margin:1px 0 4px}.feedback{height:22px;font-size:17px;margin-top:2px}.bingo{width:min(76vw,600px);height:min(76vh,275px);gap:5px}.bingo-cell{font-size:38px;border-radius:12px;box-shadow:0 3px 0 #c7dce8}.sequence-stage{height:90px}.sequence-flash{width:82px;height:82px;font-size:48px;border-radius:14px}.sequence-options{width:min(84vw,640px);grid-template-columns:repeat(6,1fr);gap:6px}.sequence-choice{height:74px;font-size:42px;border-radius:12px}.sequence-slots{min-height:26px}.seq-dot{width:22px;height:22px}.arena{width:min(88vw,720px);height:min(70vh,250px);border-radius:16px}.mover{width:65px;height:65px;font-size:40px;box-shadow:0 3px 0 #c7dce8}.finish-icon{font-size:52px}.finish-title{font-size:28px}.homebtn{padding:7px 16px;font-size:18px}}
</style></head><body>
<section id="home" class="screen home"><div class="mascot">🧊🚀⭐</div><div class="title">¡Más juegos!</div><div class="game-menu"><button class="game-tile" onclick="startBingo()"><span class="game-icon">🎲</span><span class="game-name">BINGO</span></button><button class="game-tile" onclick="startSequence()"><span class="game-icon">⚡</span><span class="game-name">SECUENCIA</span></button><button class="game-tile" onclick="startCatch()"><span class="game-icon">🚀</span><span class="game-name">ATRÁPALO</span></button></div></section>
<section id="game" class="screen hidden"><div class="top"><button onclick="exitToHome()">⬅ SALIR</button><div id="status" class="status"></div><button onclick="repeatPrompt()">🔊 OTRA VEZ</button></div><div id="prompt" class="prompt"></div><div id="play"></div><div id="feedback" class="feedback"></div></section>
<section id="finish" class="screen hidden"><div class="finish-icon">🏆⭐</div><div class="finish-title">¡Muy bien!</div><div id="finishText" class="status"></div><button class="homebtn" onclick="restartActive()">OTRA PARTIDA</button><button class="homebtn" onclick="exitToHome()">MENÚ</button></section>
<script>
const ITEMS=[{w:'cat',s:'gato',e:'🐱'},{w:'dog',s:'perro',e:'🐶'},{w:'lion',s:'león',e:'🦁'},{w:'fish',s:'pez',e:'🐟'},{w:'red',s:'rojo',e:'🔴'},{w:'blue',s:'azul',e:'🔵'},{w:'green',s:'verde',e:'🟢'},{w:'yellow',s:'amarillo',e:'🟡'},{w:'one',s:'uno',e:'1️⃣'},{w:'two',s:'dos',e:'2️⃣'},{w:'three',s:'tres',e:'3️⃣'},{w:'four',s:'cuatro',e:'4️⃣'},{w:'apple',s:'manzana',e:'🍎'},{w:'car',s:'auto',e:'🚗'},{w:'house',s:'casa',e:'🏠'},{w:'book',s:'libro',e:'📘'},{w:'hand',s:'mano',e:'✋'},{w:'eye',s:'ojo',e:'👁️'},{w:'nose',s:'nariz',e:'👃'},{w:'foot',s:'pie',e:'🦶'},{w:'sun',s:'sol',e:'☀️'},{w:'moon',s:'luna',e:'🌙'},{w:'star',s:'estrella',e:'⭐'},{w:'rocket',s:'cohete',e:'🚀'}];
const $=id=>document.getElementById(id);const shuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
let active='',lastPair=null,timers=[];function clearTimers(){timers.forEach(clearTimeout);timers=[]}function cancelAudio(){try{AndroidVoice.cancel()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel()}function pair(en,es){lastPair=[en,es];try{AndroidVoice.pair(en,es);return}catch(e){}if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(en);u.lang='en-US';u.rate=.68;u.onend=()=>{const v=new SpeechSynthesisUtterance(es);v.lang='es-AR';v.rate=.72;speechSynthesis.speak(v)};speechSynthesis.speak(u)}}function english(text){try{AndroidVoice.english(text);return}catch(e){}if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='en-US';u.rate=.68;speechSynthesis.speak(u)}}function praise(){try{AndroidVoice.praise('Great job!')}catch(e){english('Great job!')}}function show(id){['home','game','finish'].forEach(x=>$(x).classList.toggle('hidden',x!==id))}function exitToHome(){clearTimers();cancelAudio();$('play').innerHTML='';$('feedback').textContent='';show('home')}function repeatPrompt(){if(lastPair)pair(lastPair[0],lastPair[1])}function restartActive(){active==='bingo'?startBingo():active==='sequence'?startSequence():startCatch()}

// BINGO: tablero 3x3, el audio llama imágenes del propio tablero. Completar una línea gana.
let bingoBoard=[],bingoMarked=new Set(),bingoTarget=null,bingoCalls=0;
function startBingo(){active='bingo';clearTimers();cancelAudio();bingoCalls=0;bingoMarked=new Set();bingoBoard=shuffle(ITEMS).slice(0,9);show('game');$('status').textContent='Bingo';$('feedback').textContent='';renderBingo();pair('Bingo! Listen and tap.','Bingo. Escuchá y tocá.');timers.push(setTimeout(nextBingoCall,1200))}
function renderBingo(){const p=$('play');p.className='bingo';p.innerHTML='';bingoBoard.forEach(o=>{const b=document.createElement('button');b.className='bingo-cell'+(bingoMarked.has(o.w)?' marked':'');b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>tapBingo(b,o);p.appendChild(b)})}
function nextBingoCall(){const left=bingoBoard.filter(o=>!bingoMarked.has(o.w));if(!left.length){finishGame('¡Bingo completo!');return}bingoTarget=shuffle(left)[0];bingoCalls++;$('prompt').textContent='🔊 '+bingoTarget.e;pair('Find the '+bingoTarget.w,'Buscá '+bingoTarget.s)}
function tapBingo(btn,o){cancelAudio();if(!bingoTarget)return;if(o.w!==bingoTarget.w){btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';pair('Try again','Probá otra vez');return}bingoMarked.add(o.w);btn.classList.add('marked');$('feedback').textContent='⭐ GREAT JOB!';praise();if(hasBingo()){timers.push(setTimeout(()=>finishGame('¡BINGO!'),800))}else timers.push(setTimeout(nextBingoCall,650))}
function hasBingo(){const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];return lines.some(L=>L.every(i=>bingoMarked.has(bingoBoard[i].w)))}

// SECUENCIA: observa 2-4 imágenes en orden y luego tócalas en el mismo orden.
let seqRound=0,seqItems=[],seqPos=0,seqShowing=false;
function startSequence(){active='sequence';seqRound=0;show('game');nextSequenceRound()}
function nextSequenceRound(){clearTimers();cancelAudio();if(seqRound>=6){finishGame('¡6 secuencias!');return}const n=seqRound<2?2:seqRound<5?3:4;seqItems=shuffle(ITEMS).slice(0,n);seqPos=0;seqShowing=true;$('status').textContent=`Secuencia ${seqRound+1} de 6`;$('feedback').textContent='';$('prompt').textContent='👀 Mirá y escuchá';const p=$('play');p.className='sequence-stage';p.innerHTML='';lastPair=['Look and listen','Mirá y escuchá'];pair(...lastPair);timers.push(setTimeout(()=>showSequenceStep(0),700))}
function showSequenceStep(i){if(i>=seqItems.length){timers.push(setTimeout(showSequenceAnswer,550));return}const p=$('play');p.innerHTML='';const d=document.createElement('div');d.className='sequence-flash';d.textContent=seqItems[i].e;p.appendChild(d);english(seqItems[i].w);timers.push(setTimeout(()=>showSequenceStep(i+1),900))}
function showSequenceAnswer(){seqShowing=false;$('prompt').textContent='👉 Tu turno';lastPair=['Your turn','Tu turno'];pair(...lastPair);const p=$('play');p.className='';p.innerHTML='<div id="seqSlots" class="sequence-slots"></div><div id="seqOptions" class="sequence-options"></div>';const slots=$('seqSlots');seqItems.forEach(()=>{const d=document.createElement('div');d.className='seq-dot';slots.appendChild(d)});const distract=shuffle(ITEMS.filter(x=>!seqItems.some(s=>s.w===x.w))).slice(0,Math.max(0,6-seqItems.length));const opts=shuffle([...seqItems,...distract]).slice(0,6);opts.forEach(o=>{const b=document.createElement('button');b.className='sequence-choice';b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>tapSequence(b,o);$('seqOptions').appendChild(b)})}
function tapSequence(btn,o){if(seqShowing)return;cancelAudio();if(o.w!==seqItems[seqPos].w){btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');seqPos=0;[...document.querySelectorAll('.seq-dot')].forEach(d=>d.classList.remove('done'));$('feedback').textContent='Otra vez 🙂';pair('Try again','Probá otra vez');return}document.querySelectorAll('.seq-dot')[seqPos].classList.add('done');seqPos++;if(seqPos===seqItems.length){$('feedback').textContent='⭐ GREAT JOB!';praise();seqRound++;timers.push(setTimeout(nextSequenceRound,800))}}

// ATRÁPALO: seis imágenes se mueven y hay que tocar la que pide la voz.
let catchRound=0,catchTarget=null,catchItems=[];
function startCatch(){active='catch';catchRound=0;show('game');nextCatchRound()}
function nextCatchRound(){clearTimers();cancelAudio();if(catchRound>=8){finishGame('¡8 atrapados!');return}catchItems=shuffle(ITEMS).slice(0,6);catchTarget=catchItems[Math.floor(Math.random()*catchItems.length)];$('status').textContent=`Atrápalo ${catchRound+1} de 8`;$('feedback').textContent='';$('prompt').textContent='🎯 '+catchTarget.e;const p=$('play');p.className='arena';p.innerHTML='';const spots=[[8,10],[40,8],[72,12],[18,58],[52,55],[78,60]];catchItems.forEach((o,i)=>{const b=document.createElement('button');b.className='mover';b.textContent=o.e;b.dataset.word=o.w;b.style.left=`calc(${spots[i][0]}% - 30px)`;b.style.top=`calc(${spots[i][1]}% - 25px)`;b.style.setProperty('--dur',(1.6+(i%3)*.35)+'s');b.onclick=()=>tapCatch(b,o);p.appendChild(b)});pair('Catch the '+catchTarget.w,'Atrapá '+catchTarget.s)}
function tapCatch(btn,o){cancelAudio();if(o.w!==catchTarget.w){btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';pair('Try again','Probá otra vez');return}btn.classList.add('good');$('feedback').textContent='⭐ GREAT JOB!';praise();catchRound++;timers.push(setTimeout(nextCatchRound,700))}
function finishGame(text){clearTimers();cancelAudio();$('finishText').textContent=text;show('finish');praise()}
</script></body></html>''',encoding='utf-8')
print('JUGAMOS 2 creado: Bingo + Secuencia + Atrápalo, app independiente y fuente única.')
