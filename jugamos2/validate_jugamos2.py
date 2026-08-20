from pathlib import Path

html=Path('project/app/src/main/assets/www/JUGAMOS2.html')
java=Path('project/app/src/main/java/com/inglesconfran/app/MainActivity.java')
gradle=next((p for p in [Path('project/app/build.gradle'),Path('project/app/build.gradle.kts')] if p.exists()),None)
manifest=Path('project/app/src/main/AndroidManifest.xml')

s=html.read_text(encoding='utf-8')
j=java.read_text(encoding='utf-8')
g=gradle.read_text(encoding='utf-8') if gradle else ''
m=manifest.read_text(encoding='utf-8') if manifest.exists() else ''
errors=[]
checks={
 'portada 3 juegos':'game-menu',
 'Bingo':'function startBingo()',
 'Bingo 3x3':'grid-template-columns:repeat(3,1fr)',
 'Secuencia':'function startSequence()',
 'Atrápalo':'function startCatch()',
 'salida':'function exitToHome()',
 'reinicio mismo juego':'function restartActive()',
 '24 palabras':"w:'rocket'",
 'responsive teléfono':'@media(max-height:500px)',
 'texto español visible':'.prompt-es{',
 'cola de audio':'audioChain=Promise.resolve(true)',
 'callback Android':'function onAndroidAudioDone',
 'Bingo bilingüe':"'Find the '+bingoTarget.w,'Buscá '+bingoTarget.a",
 'Secuencia palabra bilingüe':"showPrompt('👀',o.w,o.s)",
 'Atrápalo bilingüe':"'Catch the '+catchTarget.w,'Atrapá '+catchTarget.a",
 'premio bilingüe':"sayPair('Great job!','¡Muy bien!',false)",
 'reintento bilingüe':"sayPair('Try again','Probá otra vez',false)"
}
for name,token in checks.items():
    if token not in s: errors.append(name)
if s.count("w:'") < 24: errors.append('banco de 24 palabras incompleto')
if s.count("a:'") < 24: errors.append('artículos españoles incompletos')
if 'package com.inglesconfran.jugamos2;' not in j: errors.append('package Java independiente')
if 'com.inglesconfran.jugamos2' not in g+m: errors.append('applicationId/manifest independiente')
if 'UtteranceProgressListener' not in j: errors.append('TTS sin callback de fin real')
if 'AndroidVoice.pair(en,es,id)' not in s: errors.append('JS no envía id de callback al TTS')
if 'notifyDone(callbackId,true)' not in j: errors.append('Android no confirma fin del español')
if 'pair_en_' not in j or 'pair_es_' not in j: errors.append('Android no separa fin inglés/español')
if 'SpeechRecognizer' in j or 'RECORD_AUDIO' in m: errors.append('Jugamos 2 no debe usar micrófono')
for forbidden in [
    'setTimeout(nextBingoCall,1200)',
    'setTimeout(()=>showSequenceStep(0),700)',
    'setTimeout(()=>showSequenceStep(i+1),900)',
    'setTimeout(nextCatchRound,700)'
]:
    if forbidden in s: errors.append('temporizador capaz de cortar audio: '+forbidden)
if errors: raise SystemExit('VALIDACIÓN JUGAMOS 2 FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN JUGAMOS 2 OK: tres juegos, bilingüe visible+audio, fin real EN->ES y sin temporizadores de corte.')
