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
 '24 palabras':'{w:\'rocket\'',
 'responsive teléfono':'@media(max-height:500px)',
 'TTS bilingüe':'function pair(en,es)',
 'sin micrófono':'AndroidVoice.pair'
}
for name,token in checks.items():
    if token not in s: errors.append(name)
if s.count("w:'") < 24: errors.append('banco de 24 palabras incompleto')
if 'package com.inglesconfran.jugamos2;' not in j: errors.append('package Java independiente')
if 'com.inglesconfran.jugamos2' not in g+m: errors.append('applicationId/manifest independiente')
if 'UtteranceProgressListener' not in j: errors.append('TTS por fin real de locución')
if 'speakPair' not in j or 'postDelayed' not in j: errors.append('encadenamiento bilingüe')
if 'SpeechRecognizer' in j or 'RECORD_AUDIO' in m: errors.append('Jugamos 2 no debe usar micrófono')
if errors: raise SystemExit('VALIDACIÓN JUGAMOS 2 FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN JUGAMOS 2 ESTRUCTURAL OK')
