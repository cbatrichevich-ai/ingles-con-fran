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
 '8 familias':'Object.entries(CATS)',
 'quiero':"want:{icon:'💬'",
 'me gusta':"like:{icon:'❤️'",
 'estoy':"am:{icon:'🙂'",
 'necesito':"need:{icon:'🙋'",
 'puedo':"can:{icon:'✋'",
 'cotidianas':"daily:{icon:'☀️'",
 'meses':"months:{icon:'📅'",
 'estaciones':"seasons:{icon:'🌎'",
 'enero':"fEn:'January',fEs:'Enero'",
 'diciembre':"fEn:'December',fEs:'Diciembre'",
 'primavera':"fEn:'Spring',fEs:'Primavera'",
 'invierno':"fEn:'Winter',fEs:'Invierno'",
 'paginación':'function renderOptionPage()',
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
if h.count("fEn:") != 40: errors.append(f'contenidos ingleses: {h.count("fEn:")} != 40')
if h.count("fEs:") != 40: errors.append(f'contenidos españoles: {h.count("fEs:")} != 40')
if h.count("fEn:'January'") != 1 or h.count("fEn:'December'") != 1: errors.append('12 meses incompletos')
for month in ['January','February','March','April','May','June','July','August','September','October','November','December']:
    if f"fEn:'{month}'" not in h: errors.append('mes faltante: '+month)
for season in ['Spring','Summer','Autumn','Winter']:
    if f"fEn:'{season}'" not in h: errors.append('estación faltante: '+season)
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
print('VALIDACIÓN HABLA OK: 24 frases + 12 meses + 4 estaciones, audio EN+ES, palabra clave, máximo dos intentos por visita, reintento diferido finito y salida real.')
