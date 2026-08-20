from pathlib import Path

ROOT=Path('project')
java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
html=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'

j=java.read_text(encoding='utf-8')
needle='public class Bridge{\n'
insert='public class Bridge{\n  @JavascriptInterface public void exitApp(){runOnUiThread(()->{cancelCurrent();finish();});}\n'
if needle not in j:
    raise SystemExit('STOP: no se encontro Bridge en Basica')
j=j.replace(needle,insert,1)
java.write_text(j,encoding='utf-8')

h=html.read_text(encoding='utf-8')
css='''.exitapp{display:block;margin:12px auto 0;border:0;border-radius:14px;background:#e85c63;color:white;padding:9px 18px;font-size:14px;font-weight:900;cursor:pointer}\n@media(max-height:500px){.exitapp{margin:5px auto 0;padding:6px 13px;font-size:11px;border-radius:10px}}\n'''
if '.exitapp{' not in h:
    h=h.replace('</style>',css+'</style>',1)
old='</div><div class="footer">Versión inicial sin juegos ni pregunta sorpresa.</div></div></section>'
new='</div><button class="exitapp" onclick="closeApp()">✕ CERRAR APP</button><div class="footer">Versión inicial sin juegos ni pregunta sorpresa.</div></div></section>'
if old not in h:
    raise SystemExit('STOP: no se encontro cierre de portada Basica')
h=h.replace(old,new,1)
marker='function goHome(){\n  stopAudio();cancelListen();micDiag(\'\');show(\'home\')}'
replacement=marker+"\nfunction closeApp(){stopAudio();cancelListen();micDiag('');try{if(window.AndroidSpeech&&AndroidSpeech.exitApp){AndroidSpeech.exitApp();return}}catch(e){}window.close()}"
if marker not in h:
    raise SystemExit('STOP: no se encontro goHome Basica')
h=h.replace(marker,replacement,1)
html.write_text(h,encoding='utf-8')
print('BASICA: boton CERRAR APP visible y cierre nativo agregado.')
