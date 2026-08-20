from pathlib import Path

root=Path('project')
html=root/'app/src/main/assets/www/FRAN-HABLA.html'
java=root/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
manifest=root/'app/src/main/AndroidManifest.xml'
if not html.exists() or not java.exists() or not manifest.exists():
    raise SystemExit('VALIDACIÓN HABLA FALLÓ: faltan archivos generados')

h=html.read_text(encoding='utf-8')
j=java.read_text(encoding='utf-8')
m=manifest.read_text(encoding='utf-8')
errors=[]
checks={
 '6 familias':'Object.entries(CATS)',
 'quiero':"want:{icon:'💬'",
 'me gusta':"like:{icon:'❤️'",
 'estoy':"am:{icon:'🙂'",
 'necesito':"need:{icon:'🙋'",
 'puedo':"can:{icon:'✋'",
 'cotidianas':"daily:{icon:'☀️'",
 'turno oral':'🗣️ AHORA VOS',
 'bilingüe':'function sayPair(en,es)',
 'palabra clave':'function keywordOf(x)',
 'evaluación tolerante':'function gradeSpeech(all,key)',
 'dos intentos':'practiceAttempt<2',
 'reintento diferido':'retryQueue',
 'avance finito':'sessionVisits',
 'repetir':'function repeatPhrase()',
 'cierre':'function closeApp()',
 'responsive':'@media(max-height:500px)'
}
for name,token in checks.items():
    if token not in h: errors.append(name)
if h.count("fEn:") != 24: errors.append(f'frases inglesas: {h.count("fEn:")} != 24')
if h.count("fEs:") != 24: errors.append(f'frases españolas: {h.count("fEs:")} != 24')
if 'package com.inglesconfran.habla;' not in j: errors.append('package Java')
if 'ttsEn.setSpeechRate(.92f)' not in j or 'ttsEs.setSpeechRate(.96f)' not in j: errors.append('ritmo TTS')
if 'UtteranceProgressListener' not in j: errors.append('callbacks de fin real')
if '@JavascriptInterface public void exitApp()' not in j: errors.append('cierre nativo')
if 'Fran Habla' not in m: errors.append('nombre visible')
if '@drawable/fran_habla_icon' not in m: errors.append('icono visible')
if 'RECORD_AUDIO' not in m: errors.append('permiso de micrófono')
if 'SpeechRecognizer' not in j or 'EXTRA_MAX_RESULTS,7' not in j: errors.append('reconocimiento de voz')
if 'EXTRA_BIASING_STRINGS' not in j: errors.append('sesgo por palabra esperada')
if 'onAndroidSpeechResult' not in h or 'startListening' not in j: errors.append('puente micrófono')
if errors:
    raise SystemExit('VALIDACIÓN HABLA FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN HABLA OK: 24 frases, audio EN+ES, palabra clave, máximo dos intentos por visita, reintento diferido finito y salida real.')
