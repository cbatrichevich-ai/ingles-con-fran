from pathlib import Path

ROOT=Path('project')
java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=ROOT/'app/src/main/assets/www/JUGAMOS2.html'

if not java.exists() or not html.exists():
    raise SystemExit('STOP: Jugamos 2 generado no encontrado')

# TTS nativo: cada locución EN -> ES termina por callbacks reales de Android.
# Ningún temporizador de juego decide cuándo cortar o iniciar el siguiente audio.
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
import org.json.JSONObject;
import java.util.Locale;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private WebView webView;
    private TextToSpeech tts;
    private boolean ready=false;
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
        tts=new TextToSpeech(this,this);
        webView.loadUrl("file:///android_asset/www/JUGAMOS2.html");
    }

    @Override public void onInit(int status){
        if(status==TextToSpeech.SUCCESS){
            int r=tts.setLanguage(Locale.US);
            ready=r!=TextToSpeech.LANG_MISSING_DATA && r!=TextToSpeech.LANG_NOT_SUPPORTED;
            if(ready){tts.setSpeechRate(.68f);tts.setPitch(1.03f);}
        }
    }

    public class VoiceBridge {
        @JavascriptInterface public void pair(String en,String es,String callbackId){ speakPair(en,es,callbackId); }
        @JavascriptInterface public void cancel(){ cancelNow(); }
    }

    private void cancelNow(){
        runOnUiThread(()->{ token++; if(tts!=null) tts.stop(); });
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

    private void speakPair(final String en, final String es, final String callbackId){
        runOnUiThread(()->{
            if(!ready || tts==null || en==null){ notifyDone(callbackId,false); return; }
            final int my=++token;
            final String enId="pair_en_"+my;
            final String esId="pair_es_"+my;
            tts.stop();
            tts.setLanguage(Locale.US); tts.setSpeechRate(.68f); tts.setPitch(1.03f);
            tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                @Override public void onStart(String id){}
                @Override public void onError(String id){
                    if(enId.equals(id) || esId.equals(id)) notifyDone(callbackId,false);
                }
                @Override public void onDone(String id){
                    if(enId.equals(id)){
                        runOnUiThread(()->{
                            if(my!=token || tts==null){ notifyDone(callbackId,false); return; }
                            new Handler(Looper.getMainLooper()).postDelayed(()->{
                                if(my!=token || tts==null){ notifyDone(callbackId,false); return; }
                                if(es==null || es.trim().isEmpty()){ notifyDone(callbackId,true); return; }
                                tts.setLanguage(new Locale("es","AR")); tts.setSpeechRate(.72f); tts.setPitch(1.01f);
                                tts.speak(es,TextToSpeech.QUEUE_FLUSH,null,esId);
                            },150);
                        });
                    } else if(esId.equals(id)) {
                        if(my==token) notifyDone(callbackId,true);
                    }
                }
            });
            tts.speak(en,TextToSpeech.QUEUE_FLUSH,null,enId);
        });
    }

    @Override public void onBackPressed(){
        if(webView!=null) webView.evaluateJavascript("exitToHome()",null); else super.onBackPressed();
    }
    @Override protected void onDestroy(){
        if(tts!=null){tts.stop();tts.shutdown();}
        if(webView!=null) webView.destroy();
        super.onDestroy();
    }
}
''',encoding='utf-8')

h=html.read_text(encoding='utf-8')
if '<script>' not in h or '</script>' not in h:
    raise SystemExit('STOP: script de Jugamos 2 no encontrado')

if '.prompt-es{' not in h:
    h=h.replace('</style>',r'''
.prompt-es{font-size:.58em;font-weight:800;line-height:1.05;margin-top:2px;color:#35536e}
@media(max-height:500px){.prompt-es{font-size:.62em;margin-top:1px}}
</style>''',1)

script=r'''<script>
const ITEMS=[
 {w:'cat',s:'gato',a:'el gato',e:'🐱'},{w:'dog',s:'perro',a:'el perro',e:'🐶'},{w:'lion',s:'león',a:'el león',e:'🦁'},{w:'fish',s:'pez',a:'el pez',e:'🐟'},
 {w:'red',s:'rojo',a:'el rojo',e:'🔴'},{w:'blue',s:'azul',a:'el azul',e:'🔵'},{w:'green',s:'verde',a:'el verde',e:'🟢'},{w:'yellow',s:'amarillo',a:'el amarillo',e:'🟡'},
 {w:'one',s:'uno',a:'el uno',e:'1️⃣'},{w:'two',s:'dos',a:'el dos',e:'2️⃣'},{w:'three',s:'tres',a:'el tres',e:'3️⃣'},{w:'four',s:'cuatro',a:'el cuatro',e:'4️⃣'},
 {w:'apple',s:'manzana',a:'la manzana',e:'🍎'},{w:'car',s:'auto',a:'el auto',e:'🚗'},{w:'house',s:'casa',a:'la casa',e:'🏠'},{w:'book',s:'libro',a:'el libro',e:'📘'},
 {w:'hand',s:'mano',a:'la mano',e:'✋'},{w:'eye',s:'ojo',a:'el ojo',e:'👁️'},{w:'nose',s:'nariz',a:'la nariz',e:'👃'},{w:'foot',s:'pie',a:'el pie',e:'🦶'},
 {w:'sun',s:'sol',a:'el sol',e:'☀️'},{w:'moon',s:'luna',a:'la luna',e:'🌙'},{w:'star',s:'estrella',a:'la estrella',e:'⭐'},{w:'rocket',s:'cohete',a:'el cohete',e:'🚀'}
];
const $=id=>document.getElementById(id);
const shuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};

let active='',lastPair=null,timers=[];
let audioEpoch=0,audioSeq=0,audioChain=Promise.resolve(true),nativeWaiters=new Map();
function clearTimers(){timers.forEach(clearTimeout);timers=[]}
function onAndroidAudioDone(id,ok){id=String(id);const r=nativeWaiters.get(id);if(r){nativeWaiters.delete(id);r(!!ok)}}
function browserPair(en,es,epoch){return new Promise(resolve=>{if(epoch!==audioEpoch){resolve(false);return}if(!('speechSynthesis'in window)){resolve(true);return}speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(en);u.lang='en-US';u.rate=.68;u.onend=()=>{if(epoch!==audioEpoch){resolve(false);return}const v=new SpeechSynthesisUtterance(es);v.lang='es-AR';v.rate=.72;v.onend=()=>resolve(epoch===audioEpoch);v.onerror=()=>resolve(false);speechSynthesis.speak(v)};u.onerror=()=>resolve(false);speechSynthesis.speak(u)})}
function nativePair(en,es,epoch){return new Promise(resolve=>{if(epoch!==audioEpoch){resolve(false);return}const id=String(++audioSeq);try{if(window.AndroidVoice&&AndroidVoice.pair){nativeWaiters.set(id,ok=>resolve(ok&&epoch===audioEpoch));AndroidVoice.pair(en,es,id);return}}catch(e){nativeWaiters.delete(id)}browserPair(en,es,epoch).then(resolve)})}
function sayPair(en,es,remember=true){if(remember)lastPair=[en,es];const epoch=audioEpoch;const run=()=>epoch===audioEpoch?nativePair(en,es,epoch):false;const p=audioChain.then(run,run);audioChain=p.catch(()=>false);return p}
function cancelAudio(){audioEpoch++;try{if(window.AndroidVoice&&AndroidVoice.cancel)AndroidVoice.cancel()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel();for(const r of nativeWaiters.values())r(false);nativeWaiters.clear();audioChain=Promise.resolve(true)}
function show(id){['home','game','finish'].forEach(x=>$(x).classList.toggle('hidden',x!==id))}
function esc(t){return String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function showPrompt(icon,en,es,remember=true){$('prompt').innerHTML='<div>'+icon+' '+esc(en)+'</div><div class="prompt-es">'+esc(es)+'</div>';return sayPair(en,es,remember)}
function praise(){return sayPair('Great job!','¡Muy bien!',false)}
function tryAgain(){return sayPair('Try again','Probá otra vez',false)}
function exitToHome(){clearTimers();cancelAudio();active='';$('play').innerHTML='';$('feedback').textContent='';$('prompt').textContent='';show('home')}
function repeatPrompt(){if(!lastPair)return;const x=[...lastPair];cancelAudio();sayPair(x[0],x[1],true)}
function restartActive(){active==='bingo'?startBingo():active==='sequence'?startSequence():startCatch()}

// BINGO: 3x3. Toda consigna se muestra y se pronuncia EN -> ES.
let bingoBoard=[],bingoMarked=new Set(),bingoTarget=null,bingoCalls=0,bingoLocked=false;
function startBingo(){active='bingo';clearTimers();cancelAudio();bingoCalls=0;bingoLocked=true;bingoMarked=new Set();bingoBoard=shuffle(ITEMS).slice(0,9);show('game');$('status').textContent='Bingo';$('feedback').textContent='';renderBingo();showPrompt('🎲','Bingo! Listen and tap.','Bingo. Escuchá y tocá.').then(ok=>{if(ok&&active==='bingo'){bingoLocked=false;nextBingoCall()}})}
function renderBingo(){const p=$('play');p.className='bingo';p.innerHTML='';bingoBoard.forEach(o=>{const b=document.createElement('button');b.className='bingo-cell'+(bingoMarked.has(o.w)?' marked':'');b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>tapBingo(b,o);p.appendChild(b)})}
function nextBingoCall(){if(active!=='bingo')return;const left=bingoBoard.filter(o=>!bingoMarked.has(o.w));if(!left.length){finishGame('¡Bingo completo!');return}bingoTarget=shuffle(left)[0];bingoCalls++;bingoLocked=false;showPrompt('🔊','Find the '+bingoTarget.w,'Buscá '+bingoTarget.a)}
function tapBingo(btn,o){if(bingoLocked||!bingoTarget)return;if(o.w!==bingoTarget.w){bingoLocked=true;btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';tryAgain().then(()=>{if(active==='bingo')bingoLocked=false});return}bingoLocked=true;bingoMarked.add(o.w);btn.classList.add('marked');$('feedback').textContent='⭐ ¡MUY BIEN!';const won=hasBingo();praise().then(ok=>{if(!ok||active!=='bingo')return;if(won)finishGame('¡BINGO!');else nextBingoCall()})}
function hasBingo(){const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];return lines.some(L=>L.every(i=>bingoMarked.has(bingoBoard[i].w)))}

// SECUENCIA: cada imagen se pronuncia primero en inglés y luego en español; el paso siguiente espera el fin real de ambos audios.
let seqRound=0,seqItems=[],seqPos=0,seqShowing=false,seqLocked=false;
function startSequence(){active='sequence';clearTimers();cancelAudio();seqRound=0;show('game');nextSequenceRound()}
function nextSequenceRound(){clearTimers();if(active!=='sequence')return;if(seqRound>=6){finishGame('¡6 secuencias!');return}const n=seqRound<2?2:seqRound<5?3:4;seqItems=shuffle(ITEMS).slice(0,n);seqPos=0;seqShowing=true;seqLocked=true;$('status').textContent=`Secuencia ${seqRound+1} de 6`;$('feedback').textContent='';const p=$('play');p.className='sequence-stage';p.innerHTML='';showPrompt('👀','Look and listen','Mirá y escuchá').then(ok=>{if(ok&&active==='sequence')showSequenceStep(0)})}
function showSequenceStep(i){if(active!=='sequence')return;if(i>=seqItems.length){showSequenceAnswer();return}const o=seqItems[i];const p=$('play');p.innerHTML='';const d=document.createElement('div');d.className='sequence-flash';d.textContent=o.e;p.appendChild(d);showPrompt('👀',o.w,o.s).then(ok=>{if(!ok||active!=='sequence')return;timers.push(setTimeout(()=>showSequenceStep(i+1),220))})}
function showSequenceAnswer(){if(active!=='sequence')return;seqShowing=false;seqLocked=false;const p=$('play');p.className='';p.innerHTML='<div id="seqSlots" class="sequence-slots"></div><div id="seqOptions" class="sequence-options"></div>';const slots=$('seqSlots');seqItems.forEach(()=>{const d=document.createElement('div');d.className='seq-dot';slots.appendChild(d)});const distract=shuffle(ITEMS.filter(x=>!seqItems.some(s=>s.w===x.w))).slice(0,Math.max(0,6-seqItems.length));const opts=shuffle([...seqItems,...distract]).slice(0,6);opts.forEach(o=>{const b=document.createElement('button');b.className='sequence-choice';b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>tapSequence(b,o);$('seqOptions').appendChild(b)});showPrompt('👉','Your turn','Tu turno')}
function tapSequence(btn,o){if(seqShowing||seqLocked)return;if(o.w!==seqItems[seqPos].w){seqLocked=true;btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');seqPos=0;[...document.querySelectorAll('.seq-dot')].forEach(d=>d.classList.remove('done'));$('feedback').textContent='Otra vez 🙂';tryAgain().then(()=>{if(active==='sequence')seqLocked=false});return}document.querySelectorAll('.seq-dot')[seqPos].classList.add('done');seqPos++;if(seqPos===seqItems.length){seqLocked=true;$('feedback').textContent='⭐ ¡MUY BIEN!';seqRound++;praise().then(ok=>{if(ok&&active==='sequence')nextSequenceRound()})}}

// ATRÁPALO: seis imágenes móviles. La consigna completa es bilingüe y nunca se corta por el cambio de ronda.
let catchRound=0,catchTarget=null,catchItems=[],catchLocked=false;
function startCatch(){active='catch';clearTimers();cancelAudio();catchRound=0;show('game');nextCatchRound()}
function nextCatchRound(){if(active!=='catch')return;if(catchRound>=8){finishGame('¡8 atrapados!');return}catchLocked=false;catchItems=shuffle(ITEMS).slice(0,6);catchTarget=catchItems[Math.floor(Math.random()*catchItems.length)];$('status').textContent=`Atrápalo ${catchRound+1} de 8`;$('feedback').textContent='';const p=$('play');p.className='arena';p.innerHTML='';const spots=[[8,10],[40,8],[72,12],[18,58],[52,55],[78,60]];catchItems.forEach((o,i)=>{const b=document.createElement('button');b.className='mover';b.textContent=o.e;b.dataset.word=o.w;b.style.left=`calc(${spots[i][0]}% - 30px)`;b.style.top=`calc(${spots[i][1]}% - 25px)`;b.style.setProperty('--dur',(1.6+(i%3)*.35)+'s');b.onclick=()=>tapCatch(b,o);p.appendChild(b)});showPrompt('🎯','Catch the '+catchTarget.w,'Atrapá '+catchTarget.a)}
function tapCatch(btn,o){if(catchLocked||!catchTarget)return;if(o.w!==catchTarget.w){catchLocked=true;btn.classList.remove('bad');void btn.offsetWidth;btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';tryAgain().then(()=>{if(active==='catch')catchLocked=false});return}catchLocked=true;btn.classList.add('good');$('feedback').textContent='⭐ ¡MUY BIEN!';catchRound++;praise().then(ok=>{if(ok&&active==='catch')nextCatchRound()})}
function finishGame(text){clearTimers();$('finishText').textContent=text;show('finish')}
</script>'''

start=h.index('<script>')
end=h.index('</script>',start)+len('</script>')
h=h[:start]+script+h[end:]

required=[
    'onAndroidAudioDone','AndroidVoice.pair(en,es,id)','audioChain=Promise.resolve(true)',
    "'Find the '+bingoTarget.w,'Buscá '+bingoTarget.a",
    "showPrompt('👀',o.w,o.s)",
    "'Catch the '+catchTarget.w,'Atrapá '+catchTarget.a",
    '.prompt-es{'
]
for token in required:
    if token not in h:
        raise SystemExit('STOP: finalización bilingüe incompleta: '+token)

for forbidden in [
    'setTimeout(nextBingoCall,1200)',
    'setTimeout(()=>showSequenceStep(0),700)',
    'setTimeout(()=>showSequenceStep(i+1),900)',
    'setTimeout(nextCatchRound,700)'
]:
    if forbidden in h:
        raise SystemExit('STOP: quedó un temporizador que puede cortar audio: '+forbidden)

html.write_text(h,encoding='utf-8')
print('JUGAMOS 2 FINALIZADO: consignas visibles y habladas EN->ES; secuencia bilingüe; cambios de ronda esperan fin real del audio.')
