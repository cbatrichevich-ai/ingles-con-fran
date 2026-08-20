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
 'audio bilingüe':'function sayPair(en,es)',
 'locución individual':'function sayOne(text,lang)',
 'teacher guía':'async function coachSequence(i,x,token)',
 'primer llamado':'Ahora vos. Decí:',
 'segunda vuelta':'Bien. Una vez más:',
 'cierre amable':'Muy bien por practicar. Seguimos.',
 'pausa palabra':'TURN_WORD_MS=1700',
 'pausa frase':'TURN_PHRASE_MS=2400',
 'avance automático':'function advancePhrase()',
 'repetir':'function repeatPhrase()',
 'cierre':'function closeApp()',
 'responsive':'@media(max-height:500px)'
}
for name,token in checks.items():
    if token not in h: errors.append(name)
if h.count("fEn:") != 40: errors.append(f'contenidos ingleses: {h.count("fEn:")} != 40')
if h.count("fEs:") != 40: errors.append(f'contenidos españoles: {h.count("fEs:")} != 40')
for month in ['January','February','March','April','May','June','July','August','September','October','November','December']:
    if f"fEn:'{month}'" not in h: errors.append('mes faltante: '+month)
for season in ['Spring','Summer','Autumn','Winter']:
    if f"fEn:'{season}'" not in h: errors.append('estación faltante: '+season)
if 'package com.inglesconfran.habla;' not in j: errors.append('package Java')
if 'ttsEn.setSpeechRate(.92f)' not in j or 'ttsEs.setSpeechRate(.96f)' not in j: errors.append('ritmo TTS')
if 'UtteranceProgressListener' not in j: errors.append('callbacks de fin real')
if '@JavascriptInterface public void single(' not in j: errors.append('puente de locución individual')
if '@JavascriptInterface public void exitApp()' not in j: errors.append('cierre nativo')
if 'Fran Habla' not in m: errors.append('nombre visible')
if '@drawable/fran_habla_icon' not in m: errors.append('icono visible')
if 'RECORD_AUDIO' in m: errors.append('no debe pedir permiso de micrófono')
if 'SpeechRecognizer' in j or 'RecognizerIntent' in j: errors.append('no debe fingir reconocimiento')
if 'AndroidSpeech' in h or 'onAndroidSpeechResult' in h: errors.append('no debe quedar lógica de reconocimiento en HTML')
if errors:
    raise SystemExit('VALIDACIÓN HABLA FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN HABLA OK: 24 frases + 12 meses + 4 estaciones, teacher oral EN/ES, dos turnos cortos, avance automático y sin reconocimiento ficticio.')
