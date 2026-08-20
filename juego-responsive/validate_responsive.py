from pathlib import Path

html=Path('project/app/src/main/assets/www/JUGAMOS.html')
java=Path('project/app/src/main/java/com/inglesconfran/app/MainActivity.java')
manifest=Path('project/app/src/main/AndroidManifest.xml')
gradle=next((p for p in [Path('project/app/build.gradle'),Path('project/app/build.gradle.kts')] if p.exists()),None)

s=html.read_text(encoding='utf-8')
j=java.read_text(encoding='utf-8')
m=manifest.read_text(encoding='utf-8') if manifest.exists() else ''
g=gradle.read_text(encoding='utf-8') if gradle else ''
errors=[]
checks={
 'media query teléfono':'@media (max-height:500px)',
 'grilla compacta juego 1':'#game:not(.memory-mode) .grid',
 'grilla compacta memoria':'#game.memory-mode .grid',
 'botones iguales portada':'#home .bigbtn{width:min(82vw,560px)',
 'Juego 1':'onclick="startGame()"',
 'Juego 2':'onclick="startMemory()"',
 'Salir':'onclick="exitToMenu()"',
 'opciones memoria':'memoryChoices',
 'respuesta memoria':'Elegí la imagen que falta:'
}
for name,token in checks.items():
    if token not in s: errors.append(name)
if 'package com.inglesconfran.jugamos.adaptable;' not in j: errors.append('package Java independiente')
if 'com.inglesconfran.jugamos.adaptable' not in (m+g): errors.append('applicationId/manifest independiente')
if 'slice(0,10)' not in s: errors.append('Juego 1 debe conservar 10 rondas')
if 'slice(0,4)' not in s: errors.append('Memoria debe conservar 4 imágenes')
if errors:
    raise SystemExit('VALIDACIÓN RESPONSIVE FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN RESPONSIVE ESTRUCTURAL OK')
