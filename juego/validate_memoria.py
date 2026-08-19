from pathlib import Path

html=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=html.read_text(encoding='utf-8')
errors=[]
checks={
 'botón Juego 2 visible':'onclick="startMemory()"',
 'botón salir':'onclick="exitToMenu()"',
 'modo memoria':'memory-mode',
 'cuatro posiciones horizontales':'grid-template-columns:repeat(4,1fr)',
 'opciones fijadas al viewport':'.memory-choices{position:fixed',
 'borde inferior visible':'bottom:8px',
 'cuatro imágenes originales':'slice(0,4)',
 'misma colección reutilizada':'memSet.forEach',
 'una sola imagen desaparece':"b.textContent=(o.w===missing.w?'❓':o.e)",
 'opciones de respuesta':'Elegí la imagen que falta:',
 'opciones se hacen visibles':"box.classList.remove('hidden')",
 'repetición según juego':'repeatCurrentPrompt()',
 'reinicio según juego':'restartCurrentGame()'
}
for name,token in checks.items():
    if token not in s: errors.append(name)
if s.count('memSet=shuffle([...ITEMS]).slice(0,4)') != 1:
    errors.append('memSet debe generarse exactamente una vez por ronda')
if s.count("memSet.forEach(o=>") < 2:
    errors.append('la misma memSet debe dibujarse en tarjeta 1 y tarjeta 2')
if errors:
    raise SystemExit('VALIDACIÓN MEMORIA FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN MEMORIA OK: mismas 4 imágenes, una falta, opciones visibles dentro del viewport y salida disponible.')
