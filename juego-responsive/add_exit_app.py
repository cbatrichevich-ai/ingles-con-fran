from pathlib import Path

ROOT=Path('project')
java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=ROOT/'app/src/main/assets/www/JUGAMOS.html'

j=java.read_text(encoding='utf-8')
needle='    public class VoiceBridge {\n'
insert='    public class VoiceBridge {\n        @JavascriptInterface public void exitApp(){ runOnUiThread(()->{ cancelPairNow(); finish(); }); }\n'
if needle not in j:
    raise SystemExit('STOP: no se encontro VoiceBridge en Jugamos')
j=j.replace(needle,insert,1)
java.write_text(j,encoding='utf-8')

h=html.read_text(encoding='utf-8')
css='''.exitapp{border:0;border-radius:18px;background:#e85c63;color:white;padding:9px 18px;font-size:16px;font-weight:900;box-shadow:0 4px 0 #c84a50;margin-top:10px}\n@media(max-height:500px){.exitapp{padding:5px 12px;font-size:12px;border-radius:11px;box-shadow:0 3px 0 #c84a50;margin-top:4px}}\n'''
if '.exitapp{' not in h:
    h=h.replace('</style>',css+'</style>',1)
old='<button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button><div class="small">Mirá, recordá y descubrí qué imagen desapareció.</div></section>'
new='<button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button><div class="small">Mirá, recordá y descubrí qué imagen desapareció.</div><button class="exitapp" onclick="closeApp()">✕ CERRAR APP</button></section>'
if old not in h:
    raise SystemExit('STOP: no se encontro portada final Jugamos')
h=h.replace(old,new,1)
h=h.replace('onclick="exitToMenu()">⬅ SALIR</button>','onclick="exitToMenu()">⬅ MENÚ</button>')
marker='function exitToMenu(){'
if marker not in h:
    raise SystemExit('STOP: no se encontro exitToMenu en Jugamos')
closefn="function closeApp(){try{cancelPromptPair()}catch(e){}try{memoryCancelPair()}catch(e){}try{if(window.AndroidVoice&&AndroidVoice.exitApp){AndroidVoice.exitApp();return}}catch(e){}window.close()}\n"
h=h.replace(marker,closefn+marker,1)
html.write_text(h,encoding='utf-8')
print('JUGAMOS ADAPTABLE: boton CERRAR APP y cierre nativo agregados; SALIR interno renombrado MENÚ.')
