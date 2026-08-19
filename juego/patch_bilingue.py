from pathlib import Path

root=Path('project')
java=root/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=root/'app/src/main/assets/www/JUGAMOS.html'

s=java.read_text(encoding='utf-8')
s=s.replace('tts.setSpeechRate(0.82f)', 'tts.setSpeechRate(0.68f)')
s=s.replace('speakNow(text,1.04f,0.82f)', 'speakNow(text,1.04f,0.68f)')
s=s.replace('@JavascriptInterface public void praise(String text){ speakNow(text,1.12f,0.90f); }', '@JavascriptInterface public void praise(String text){ speakNow(text,1.12f,0.78f); }\n        @JavascriptInterface public void speakSpanish(String text){ speakSpanishNow(text); }')
needle='    private void speakNow(final String text, final float pitch, final float rate){'
insert='''    private void speakSpanishNow(final String text){\n        runOnUiThread(()->{\n            if(tts==null || !ttsReady || text==null) return;\n            tts.setLanguage(new Locale("es","AR"));\n            tts.setPitch(1.02f); tts.setSpeechRate(0.72f);\n            tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"jugamos_es");\n        });\n    }\n\n'''
s=s.replace(needle,insert+needle)
# English calls restore English locale before speaking.
s=s.replace('if(tts==null || !ttsReady || text==null) return;\n            tts.setPitch(pitch);', 'if(tts==null || !ttsReady || text==null) return;\n            tts.setLanguage(Locale.US);\n            tts.setPitch(pitch);')
java.write_text(s,encoding='utf-8')

s=html.read_text(encoding='utf-8')
translations={'cat':'gato','dog':'perro','lion':'león','fish':'pez','red':'rojo','blue':'azul','green':'verde','yellow':'amarillo','one':'uno','two':'dos','three':'tres','four':'cuatro','apple':'manzana','car':'auto','house':'casa','book':'libro','hand':'mano','eye':'ojo','nose':'nariz','foot':'pie','sun':'sol','moon':'luna','star':'estrella','rocket':'cohete'}
for en,es in translations.items():
    s=s.replace("{w:'%s',e:"%en, "{w:'%s',s:'%s',e:"%(en,es))
s=s.replace("u.rate=.82", "u.rate=.68")
old="function sayPrompt(){if(!current)return;$('prompt').textContent='🔊 Find the '+current.w+'!';voice('Find the '+current.w)}"
new="function sayPrompt(){if(!current)return;$('prompt').innerHTML='🔊 Find the '+current.w+'!<br><span style=\"font-size:.58em;font-weight:700\">Buscá: '+current.s+'</span>';voice('Find the '+current.w);setTimeout(()=>{try{if(window.AndroidVoice&&AndroidVoice.speakSpanish){AndroidVoice.speakSpanish('Buscá '+current.s);return}}catch(e){} if('speechSynthesis'in window){const u=new SpeechSynthesisUtterance('Buscá '+current.s);u.lang='es-AR';u.rate=.72;speechSynthesis.speak(u)}},3200)}"
s=s.replace(old,new)
s=s.replace('setTimeout(nextRound,900)', 'setTimeout(nextRound,2400)')
html.write_text(s,encoding='utf-8')
print('Jugamos ajustado: inglés lento sin corte, traducción española y mayor pausa entre rondas.')
