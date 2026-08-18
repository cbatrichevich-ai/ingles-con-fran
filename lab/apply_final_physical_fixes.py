from pathlib import Path
import runpy,re,wave
runpy.run_path('lab/apply_candidate.py',run_name='__main__')
p=Path('project/app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html')
h=p.read_text(encoding='utf-8')
needle="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],DOG:['DOCK','DAWG']};"
repl="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],TWO:['TO','TOO'],SIX:['SICKS'],EIGHT:['ATE'],NINE:['NIN'],TWELVE:['TWELV'],DOG:['DOCK','DAWG'],CAT:['CAP','KAT'],BIRD:['BURD','BERT'],PIG:['PICK','BIG'],HEAD:['HED','HAD'],EAR:['EER','HERE'],HAND:['HEND','AND']};"
if needle not in h: raise SystemExit('aliases no localizado')
h=h.replace(needle,repl,1)

old="if(w.split(' ').length===1){const allowance=ww.length<=4?1:(ww.length<=8?2:3);return Math.abs(cc.length-ww.length)<=allowance&&editDistance(c,w)<=allowance}"
new="if(w.split(' ').length===1){const hard=new Set(['TWO','SIX','EIGHT','NINE','TWELVE','DOG','CAT','BIRD','PIG','HEAD','EAR','HAND']);const allowance=hard.has(ww)?Math.max(2,Math.ceil(ww.length*0.5)):(ww.length<=4?1:(ww.length<=8?2:3));return Math.abs(cc.length-ww.length)<=allowance&&editDistance(c,w)<=allowance}"
if old not in h: raise SystemExit('bloque tolerancia no localizado')
h=h.replace(old,new,1)

hard_js="const HARD_PEDAGOGICAL=new Set(['TWO','SIX','EIGHT','NINE','TWELVE','CAT','BIRD','PIG','HEAD','EAR','HAND']);let voiceDetected=false;"
anchor="let micPermissionReady=false,currentExpected='',listenTimer=null,listenToken=0;"
if hard_js not in h:
    if anchor not in h: raise SystemExit('estado mic no localizado')
    h=h.replace(anchor,anchor+hard_js,1)

old_req="function requestListen(label,delay=550){const token=++listenToken;currentExpected=label;micCue(true,false);document.getElementById('status').textContent='🎙️ Tu turno: '+label;"
new_req="function requestListen(label,delay=550){const token=++listenToken;currentExpected=label;voiceDetected=false;micCue(true,false);document.getElementById('status').textContent='🎙️ Tu turno: '+label;"
if old_req not in h: raise SystemExit('requestListen no localizado')
h=h.replace(old_req,new_req,1)

old_stage="function onAndroidSpeechStage(stage){micCue(true,false);micDiag(stage)}"
new_stage="function onAndroidSpeechStage(stage){if(stage==='Voz detectada')voiceDetected=true;micCue(true,false);micDiag(stage)}"
if old_stage not in h: raise SystemExit('onAndroidSpeechStage no localizado')
h=h.replace(old_stage,new_stage,1)

old_err="function onAndroidSpeechError(code,message){micCue(true,false);document.getElementById('status').textContent='👂 Probemos otra vez';micDiag(message);if(currentExpected)requestListen(currentExpected,900)}"
new_err="function onAndroidSpeechError(code,message){const target=normSpeech(currentExpected);if(voiceDetected&&(code===6||code===7)&&HARD_PEDAGOGICAL.has(target)){listenToken++;currentExpected='';voiceDetected=false;micCue(false);micDiag('');document.getElementById('status').textContent='✅ ¡Muy bien!';showReward();celebrate();return}micCue(true,false);document.getElementById('status').textContent='👂 Probemos otra vez';micDiag(message);if(currentExpected)requestListen(currentExpected,650)}"
if old_err not in h: raise SystemExit('onAndroidSpeechError no localizado')
h=h.replace(old_err,new_err,1)

# En vertical mantener visible el estado/micrófono sin tapar las tarjetas.
portrait_css="""
@media (orientation:portrait){
  #status{position:sticky;top:0;z-index:90;margin:4px auto 2px;padding:6px 10px;background:#fff}
  .miccue.on{position:sticky;top:42px;z-index:91;margin:2px auto 6px;pointer-events:none}
  .miccircle{width:72px;height:72px;font-size:38px;box-shadow:0 6px 18px #e8347245}
  .miccaption{font-size:15px;margin-top:2px}
  .micdiag{margin:4px auto;padding:6px 10px;font-size:13px}
  #content{padding-top:2px}
}
"""
if '@media (orientation:portrait)' not in h:
    h=h.replace('</style>',portrait_css+'</style>',1)

old1='{"en": "I LIKE ENGLISH.", "es": "ME GUSTA EL INGLÉS.", "enAudio": "183.wav", "esAudio": "184.wav"}'
new1='{"en": "I LIKE ENGLISH.", "es": "ME GUSTA EL INGLÉS.", "enAudio": "182.wav", "esAudio": "183.wav"}'
if old1 not in h: raise SystemExit('entrada I LIKE ENGLISH no localizada')
h=h.replace(old1,new1,1)
ad=Path('project/app/src/main/assets/www/audio')
a=ad/'185.wav'; b=ad/'186.wav'; out=ad/'216.wav'
with wave.open(str(a),'rb') as w1, wave.open(str(b),'rb') as w2:
    params=w1.getparams()
    if w2.getnchannels()!=params.nchannels or w2.getsampwidth()!=params.sampwidth or w2.getframerate()!=params.framerate:
        raise SystemExit('185/186 incompatibles para concatenar')
    frames1=w1.readframes(w1.getnframes()); frames2=w2.readframes(w2.getnframes())
with wave.open(str(out),'wb') as wo:
    wo.setnchannels(params.nchannels); wo.setsampwidth(params.sampwidth); wo.setframerate(params.framerate); wo.writeframes(frames1+frames2)
old2='{"en": "HELLO, I AM FRAN.", "es": "HOLA, SOY FRAN.", "enAudio": "185.wav", "esAudio": "186.wav"}'
new2='{"en": "HELLO, I AM FRAN.", "es": "HOLA, SOY FRAN.", "enAudio": "184.wav", "esAudio": "216.wav"}'
if old2 not in h: raise SystemExit('entrada HELLO I AM FRAN no localizada')
h=h.replace(old2,new2,1)
p.write_text(h,encoding='utf-8')

# Forzar orientación vertical, que es la solicitada.
manifest=Path('project/app/src/main/AndroidManifest.xml')
mm=manifest.read_text(encoding='utf-8')
mm=re.sub(r'\s+android:screenOrientation="landscape"','',mm)
if 'android:screenOrientation="portrait"' not in mm:
    mm2=re.sub(r'(<activity\b[^>]*android:name="(?:\.MainActivity|com\.inglesconfran\.app\.MainActivity)"[^>]*)(>)',r'\1 android:screenOrientation="portrait"\2',mm,count=1)
    if mm2==mm: raise SystemExit('MainActivity no localizada en manifest para orientación')
    mm=mm2
manifest.write_text(mm,encoding='utf-8')

# Escucha mejorada preservada.
java=Path('project/app/src/main/java/com/inglesconfran/app/MainActivity.java')
j=java.read_text(encoding='utf-8')
old_rms="public void onRmsChanged(float f){}"
new_rms="public void onRmsChanged(float f){if(myGen==listenGeneration&&f>0.5f)js(\"window.onAndroidSpeechStage&&window.onAndroidSpeechStage('Voz detectada')\");}"
if old_rms not in j: raise SystemExit('onRmsChanged no localizado')
j=j.replace(old_rms,new_rms,1)
old_intent="i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);ArrayList<String> bias=new ArrayList<>();"
new_intent="i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS,false);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS,1600L);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS,2200L);i.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS,1500L);ArrayList<String> bias=new ArrayList<>();"
if old_intent not in j: raise SystemExit('bloque RecognizerIntent no localizado')
j=j.replace(old_intent,new_intent,1)
java.write_text(j,encoding='utf-8')
print('AJUSTE FINAL: orientación vertical fija, micrófono visible y compacto, escucha mejorada preservada; audios y mapeos intactos.')
