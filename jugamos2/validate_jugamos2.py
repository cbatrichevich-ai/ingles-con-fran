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
 'volver a menú':'function exitToHome()',
 'cerrar app':'function closeApp()',
 'botón cerrar visible':'CERRAR APP',
 'reinicio mismo juego':'function restartActive()',
 '24 palabras':"w:'rocket'",
 'responsive teléfono':'@media(max-height:500px)',
 'texto español visible':'.prompt-es{',
 'cola de audio':'audioChain=Promise.resolve(true)',
 'callback Android':'function onAndroidAudioDone',
 'Bingo bilingüe':"'Find the '+bingoTarget.w,'Buscá '+bingoTarget.a",
 'Secuencia palabra bilingüe':"showPrompt('👀',o.w,o.s)",
 'Atrápalo bilingüe':"'Catch the '+catchTarget.w,'Atrapá '+catchTarget.a",
 'reintento bilingüe':"sayPair('Try again','Probá otra vez',false)",
 'interacción cancela Bingo':'function tapBingo(btn,o){if(bingoLocked||!bingoTarget)return;cancelAudio();',
 'interacción cancela Secuencia':'function tapSequence(btn,o){if(seqShowing||seqLocked)return;cancelAudio();',
 'interacción cancela Atrápalo':'function tapCatch(btn,o){if(catchLocked||!catchTarget)return;cancelAudio();'
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
if 'ttsEn' not in j or 'ttsEs' not in j: errors.append('TTS no usa motores EN/ES separados')
if 'new Handler' in j or 'postDelayed' in j: errors.append('queda pausa artificial EN->ES')
if '.92f' not in j or '.96f' not in j: errors.append('velocidad TTS rápida no aplicada')
if '@JavascriptInterface public void exitApp()' not in j: errors.append('puente de cierre nativo ausente')
if 'SpeechRecognizer' in j or 'RECORD_AUDIO' in m: errors.append('Mas Juegos no debe usar micrófono')
for forbidden in [
    'setTimeout(nextBingoCall,1200)',
    'setTimeout(()=>showSequenceStep(0),700)',
    'setTimeout(()=>showSequenceStep(i+1),900)',
    'setTimeout(nextCatchRound,700)',
    "sayPair('Great job!','¡Muy bien!',false)"
]:
    if forbidden in s: errors.append('freno innecesario aún presente: '+forbidden)
if errors: raise SystemExit('VALIDACIÓN MAS JUEGOS FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN MAS JUEGOS OK: 3 juegos, bilingüe, TTS rápido por motores separados, interacción inmediata y cierre real.')
