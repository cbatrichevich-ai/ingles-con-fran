from pathlib import Path
import runpy,re,wave
runpy.run_path('lab/apply_candidate.py',run_name='__main__')
p=Path('project/app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html')
h=p.read_text(encoding='utf-8')
needle="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],DOG:['DOCK','DAWG']};"
repl="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],TWO:['TO','TOO'],SIX:['SICKS'],EIGHT:['ATE'],NINE:['NIN'],TWELVE:['TWELV'],DOG:['DOCK','DAWG'],CAT:['CAP','KAT'],BIRD:['BURD','BERT'],PIG:['PICK','BIG'],HEAD:['HED','HAD'],EAR:['EER','HERE'],HAND:['HEND','AND']};"
if needle not in h: raise SystemExit('aliases no localizado')
h=h.replace(needle,repl,1)
# Tolerancia especial para los casos que fallaron físicamente: sólo palabras objetivo conocidas y sólo similitud razonable.
old="if(w.split(' ').length===1){const allowance=ww.length<=4?1:(ww.length<=8?2:3);return Math.abs(cc.length-ww.length)<=allowance&&editDistance(c,w)<=allowance}"
new="if(w.split(' ').length===1){const hard=new Set(['TWO','SIX','EIGHT','NINE','TWELVE','DOG','CAT','BIRD','PIG','HEAD','EAR','HAND']);const allowance=hard.has(ww)?Math.max(2,Math.ceil(ww.length*0.5)):(ww.length<=4?1:(ww.length<=8?2:3));return Math.abs(cc.length-ww.length)<=allowance&&editDistance(c,w)<=allowance}"
if old not in h: raise SystemExit('bloque tolerancia no localizado')
h=h.replace(old,new,1)
# Mapeos comprobados por transcripción real de los WAV.
old1='{"en": "I LIKE ENGLISH.", "es": "ME GUSTA EL INGLÉS.", "enAudio": "183.wav", "esAudio": "184.wav"}'
new1='{"en": "I LIKE ENGLISH.", "es": "ME GUSTA EL INGLÉS.", "enAudio": "182.wav", "esAudio": "183.wav"}'
if old1 not in h: raise SystemExit('entrada I LIKE ENGLISH no localizada')
h=h.replace(old1,new1,1)
# HELLO: 184 dice la frase inglesa; 185 dice Hola y 186 dice Soy Fran. Crear una toma española combinada 216.wav.
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
print('FINAL: mapeos 182/183 y 184/216 aplicados; 216 concatena Hola + Soy Fran; tolerancia ampliada sólo para fallos físicos reportados.')
