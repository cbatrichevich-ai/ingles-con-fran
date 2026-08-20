from pathlib import Path

ROOT=Path('project')
java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=ROOT/'app/src/main/assets/www/JUGAMOS2.html'

if not java.exists() or not html.exists():
    raise SystemExit('STOP: Jugamos 2 final no encontrado')

# Dos motores TTS separados evitan el retardo de cambiar idioma sobre el mismo motor.
java.write_text(r'''package com.inglesconfran.jugamos2;

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
    private boolean enReady=false, esReady=false;
    private int token=0;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        webView=new WebView(this); setContentView(webView);
        webView.setWebViewClient(new WebViewClient()); webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(),"AndroidVoice");
        WebSettings s=webView.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true); s.setLoadWithOverviewMode(true); s.setUseWideViewPort(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        ttsEn=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEn.setLanguage(Locale.US);enReady=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(enReady){ttsEn.setSpeechRate(.92f);ttsEn.setPitch(1.03f);}}});
        ttsEs=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS){int r=ttsEs.setLanguage(new Locale("es","AR"));esReady=r!=TextToSpeech.LANG_MISSING_DATA&&r!=TextToSpeech.LANG_NOT_SUPPORTED;if(esReady){ttsEs.setSpeechRate(.96f);ttsEs.setPitch(1.01f);}}});
        webView.loadUrl("file:///android_asset/www/JUGAMOS2.html");
    }

    public class VoiceBridge{
        @JavascriptInterface public void pair(String en,String es,String callbackId){speakPair(en,es,callbackId);}
        @JavascriptInterface public void cancel(){cancelNow();}
        @JavascriptInterface public void exitApp(){runOnUiThread(()->{cancelNow();finish();});}
    }

    private void notifyDone(final String callbackId, final boolean ok){
        if(callbackId==null||webView==null)return;
        runOnUiThread(()->{if(webView!=null){String js="window.onAndroidAudioDone&&window.onAndroidAudioDone("+JSONObject.quote(callbackId)+","+(ok?"true":"false")+")";webView.evaluateJavascript(js,null);}});
    }

    private void cancelNow(){
        runOnUiThread(()->{token++;if(ttsEn!=null)ttsEn.stop();if(ttsEs!=null)ttsEs.stop();});
    }

    private void speakPair(final String en,final String es,final String callbackId){
        runOnUiThread(()->{
            if(!enReady||!esReady||ttsEn==null||ttsEs==null||en==null){notifyDone(callbackId,false);return;}
            final int my=++token; final String enId="en_"+my, esId="es_"+my;
            ttsEn.stop();ttsEs.stop();
            ttsEs.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                @Override public void onStart(String id){}
                @Override public void onError(String id){if(esId.equals(id))notifyDone(callbackId,false);}
                @Override public void onDone(String id){if(esId.equals(id)&&my==token)notifyDone(callbackId,true);}
            });
            ttsEn.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                @Override public void onStart(String id){}
                @Override public void onError(String id){if(enId.equals(id))notifyDone(callbackId,false);}
                @Override public void onDone(String id){
                    if(!enId.equals(id))return;
                    runOnUiThread(()->{
                        if(my!=token||ttsEs==null){notifyDone(callbackId,false);return;}
                        if(es==null||es.trim().isEmpty()){notifyDone(callbackId,true);return;}
                        ttsEs.speak(es,TextToSpeech.QUEUE_FLUSH,null,esId);
                    });
                }
            });
            ttsEn.speak(en,TextToSpeech.QUEUE_FLUSH,null,enId);
        });
    }

    @Override public void onBackPressed(){if(webView!=null)webView.evaluateJavascript("exitToHome()",null);else super.onBackPressed();}
    @Override protected void onDestroy(){if(ttsEn!=null){ttsEn.stop();ttsEn.shutdown();}if(ttsEs!=null){ttsEs.stop();ttsEs.shutdown();}if(webView!=null)webView.destroy();super.onDestroy();}
}
''',encoding='utf-8')

h=html.read_text(encoding='utf-8')

# Ritmo del fallback web: voz casi normal, sin pausas artificiales.
h=h.replace("u.rate=.68", "u.rate=.92").replace("v.rate=.72", "v.rate=.96")

# Botón de cierre real y nombre claro del botón que sólo vuelve al menú.
if '.exitapp{' not in h:
    h=h.replace('</style>', '.exitapp{border:0;border-radius:16px;background:#e85c63;color:white;padding:9px 18px;font-size:16px;font-weight:900;box-shadow:0 4px 0 #c84a50;margin-top:12px}.exitapp:active{transform:translateY(3px);box-shadow:0 1px 0 #c84a50}@media(max-height:500px){.exitapp{padding:5px 12px;font-size:12px;margin-top:5px;border-radius:11px}}\n</style>',1)
old_home='</div></section>\n<section id="game"'
new_home='</div><button class="exitapp" onclick="closeApp()">✕ CERRAR APP</button></section>\n<section id="game"'
if old_home not in h:
    raise SystemExit('STOP: no se encontro cierre de portada Mas Juegos')
h=h.replace(old_home,new_home,1)
h=h.replace('onclick="exitToHome()">⬅ SALIR</button>','onclick="exitToHome()">⬅ MENÚ</button>',1)
h=h.replace('<button class="homebtn" onclick="exitToHome()">MENÚ</button></section>', '<button class="homebtn" onclick="exitToHome()">MENÚ</button><button class="exitapp" onclick="closeApp()">✕ CERRAR APP</button></section>',1)

# Feedback correcto queda visual: no frena la siguiente ronda con otra locución.
old="function praise(){return sayPair('Great job!','¡Muy bien!',false)}"
if old not in h: raise SystemExit('STOP: praise final no encontrado')
h=h.replace(old,"function praise(){return Promise.resolve(true)}",1)

# Cierre nativo.
marker="function exitToHome(){clearTimers();cancelAudio();active='';$('play').innerHTML='';$('feedback').textContent='';$('prompt').textContent='';show('home')}"
if marker not in h: raise SystemExit('STOP: exitToHome final no encontrado')
h=h.replace(marker,marker+"\nfunction closeApp(){clearTimers();cancelAudio();try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}",1)

# La interacción del chico manda: tocar cancela cualquier consigna pendiente.
for a,b in [
 ("function tapBingo(btn,o){if(bingoLocked||!bingoTarget)return;","function tapBingo(btn,o){if(bingoLocked||!bingoTarget)return;cancelAudio();"),
 ("function tapSequence(btn,o){if(seqShowing||seqLocked)return;","function tapSequence(btn,o){if(seqShowing||seqLocked)return;cancelAudio();"),
 ("function tapCatch(btn,o){if(catchLocked||!catchTarget)return;","function tapCatch(btn,o){if(catchLocked||!catchTarget)return;cancelAudio();")]:
    if a not in h: raise SystemExit('STOP: handler esperado no encontrado: '+a[:30])
    h=h.replace(a,b,1)

# Eliminar esperas no educativas entre elementos de Secuencia.
h=h.replace("timers.push(setTimeout(()=>showSequenceStep(i+1),220))","timers.push(setTimeout(()=>showSequenceStep(i+1),35))")

# En Bingo y Secuencia no recitar una introducción completa en cada arranque/ronda.
old_bingo="function startBingo(){active='bingo';clearTimers();cancelAudio();bingoCalls=0;bingoLocked=true;bingoMarked=new Set();bingoBoard=shuffle(ITEMS).slice(0,9);show('game');$('status').textContent='Bingo';$('feedback').textContent='';renderBingo();showPrompt('🎲','Bingo! Listen and tap.','Bingo. Escuchá y tocá.').then(ok=>{if(ok&&active==='bingo'){bingoLocked=false;nextBingoCall()}})}"
new_bingo="function startBingo(){active='bingo';clearTimers();cancelAudio();bingoCalls=0;bingoLocked=false;bingoMarked=new Set();bingoBoard=shuffle(ITEMS).slice(0,9);show('game');$('status').textContent='Bingo';$('feedback').textContent='';renderBingo();nextBingoCall()}"
if old_bingo not in h: raise SystemExit('STOP: startBingo final no encontrado')
h=h.replace(old_bingo,new_bingo,1)
old_seq="showPrompt('👀','Look and listen','Mirá y escuchá').then(ok=>{if(ok&&active==='sequence')showSequenceStep(0)})"
if old_seq not in h: raise SystemExit('STOP: intro Secuencia final no encontrada')
h=h.replace(old_seq,"$('prompt').innerHTML='<div>👀 Look and listen</div><div class=\"prompt-es\">Mirá y escuchá</div>';lastPair=['Look and listen','Mirá y escuchá'];showSequenceStep(0)",1)

html.write_text(h,encoding='utf-8')
print('MAS JUEGOS RAPIDO: TTS EN/ES paralelo por motores separados, sin pausa artificial, interacción inmediata y CERRAR APP real.')
