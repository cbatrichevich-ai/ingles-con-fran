from pathlib import Path

root=Path('project')
java=root/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=root/'app/src/main/assets/www/JUGAMOS.html'

s=java.read_text(encoding='utf-8')
s=s.replace('import android.speech.tts.TextToSpeech;', 'import android.speech.tts.TextToSpeech;\nimport android.speech.tts.UtteranceProgressListener;')
s=s.replace('    private boolean ttsReady=false;', '    private boolean ttsReady=false;\n    private int pairToken=0;')
s=s.replace('tts.setSpeechRate(0.82f)', 'tts.setSpeechRate(0.68f)')
s=s.replace('speakNow(text,1.04f,0.82f)', 'speakNow(text,1.04f,0.68f)')
s=s.replace('@JavascriptInterface public void praise(String text){ speakNow(text,1.12f,0.90f); }\n        @JavascriptInterface public void stop(){ runOnUiThread(()->{ if(tts!=null) tts.stop(); }); }', '''@JavascriptInterface public void praise(String text){ cancelPairNow(); speakNow(text,1.12f,0.78f); }
        @JavascriptInterface public void speakSpanish(String text){ cancelPairNow(); speakSpanishNow(text); }
        @JavascriptInterface public void speakPair(String en,String es){ speakPairNow(en,es); }
        @JavascriptInterface public void cancelPair(){ cancelPairNow(); }
        @JavascriptInterface public void stop(){ cancelPairNow(); }''')
needle='    private void speakNow(final String text, final float pitch, final float rate){'
insert='''    private void cancelPairNow(){
        runOnUiThread(()->{ pairToken++; if(tts!=null) tts.stop(); });
    }

    private void speakSpanishNow(final String text){
        runOnUiThread(()->{
            if(tts==null || !ttsReady || text==null) return;
            tts.setLanguage(new Locale("es","AR"));
            tts.setPitch(1.02f); tts.setSpeechRate(0.72f);
            tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"jugamos_es");
        });
    }

    private void speakPairNow(final String en, final String es){
        runOnUiThread(()->{
            if(tts==null || !ttsReady || en==null) return;
            final int myToken=++pairToken;
            final String utteranceId="jugamos_pair_"+myToken;
            tts.setLanguage(Locale.US); tts.setPitch(1.04f); tts.setSpeechRate(0.68f);
            tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){
                @Override public void onStart(String id){}
                @Override public void onError(String id){}
                @Override public void onDone(String id){
                    if(!utteranceId.equals(id)) return;
                    runOnUiThread(()->{
                        if(myToken!=pairToken || tts==null || es==null) return;
                        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->{
                            if(myToken!=pairToken || tts==null) return;
                            tts.setLanguage(new Locale("es","AR"));
                            tts.setPitch(1.02f); tts.setSpeechRate(0.72f);
                            tts.speak(es,TextToSpeech.QUEUE_FLUSH,null,"jugamos_es_"+myToken);
                        },180);
                    });
                }
            });
            tts.speak(en,TextToSpeech.QUEUE_FLUSH,null,utteranceId);
        });
    }

'''
if needle not in s:
    raise SystemExit('STOP: no se encontró speakNow')
s=s.replace(needle,insert+needle)
s=s.replace('if(tts==null || !ttsReady || text==null) return;\n            tts.setPitch(pitch);', 'if(tts==null || !ttsReady || text==null) return;\n            tts.setLanguage(Locale.US);\n            tts.setPitch(pitch);')
java.write_text(s,encoding='utf-8')

s=html.read_text(encoding='utf-8')
translations={'cat':'gato','dog':'perro','lion':'león','fish':'pez','red':'rojo','blue':'azul','green':'verde','yellow':'amarillo','one':'uno','two':'dos','three':'tres','four':'cuatro','apple':'manzana','car':'auto','house':'casa','book':'libro','hand':'mano','eye':'ojo','nose':'nariz','foot':'pie','sun':'sol','moon':'luna','star':'estrella','rocket':'cohete'}
for en,es in translations.items():
    s=s.replace("{w:'%s',e:"%en, "{w:'%s',s:'%s',e:"%(en,es))
s=s.replace("u.rate=.82", "u.rate=.68")
# Juego normal: 10 rondas aleatorias. Las 24 palabras siguen disponibles en el banco.
s=s.replace("deck=shuffle([...ITEMS])", "deck=shuffle([...ITEMS]).slice(0,10)")
old="function sayPrompt(){if(!current)return;$('prompt').textContent='🔊 Find the '+current.w+'!';voice('Find the '+current.w)}"
new="function cancelPromptPair(){try{if(window.AndroidVoice&&AndroidVoice.cancelPair)AndroidVoice.cancelPair()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel()}\nfunction sayPrompt(){if(!current)return;$('prompt').innerHTML='🔊 Find the '+current.w+'!<br><span style=\"font-size:.58em;font-weight:700\">Buscá: '+current.s+'</span>';try{if(window.AndroidVoice&&AndroidVoice.speakPair){AndroidVoice.speakPair('Find the '+current.w,'Buscá '+current.s);return}}catch(e){}if('speechSynthesis'in window){speechSynthesis.cancel();const en=new SpeechSynthesisUtterance('Find the '+current.w);en.lang='en-US';en.rate=.68;en.onend=()=>{setTimeout(()=>{const es=new SpeechSynthesisUtterance('Buscá '+current.s);es.lang='es-AR';es.rate=.72;speechSynthesis.speak(es)},180)};speechSynthesis.speak(en)}}"
if old not in s:
    raise SystemExit('STOP: no se encontró sayPrompt base')
s=s.replace(old,new)
# La respuesta queda habilitada desde que aparecen las imágenes; al tocar se cancela cualquier traducción pendiente.
s=s.replace("function choose(btn,item){if(locked)return;", "function choose(btn,item){if(locked)return;cancelPromptPair();")
s=s.replace('setTimeout(nextRound,900)', 'setTimeout(nextRound,2400)')
html.write_text(s,encoding='utf-8')
print('Jugamos: audio inglés completo, español 180 ms después del fin real, respuesta inmediata y 10 rondas.')
