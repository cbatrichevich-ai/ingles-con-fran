from pathlib import Path

root=Path('project')
html=root/'app/src/main/assets/www/JUGAMOS.html'
s=html.read_text(encoding='utf-8')

# Reemplazar los sustantivos españoles por formas con artículo.
articles={
'cat':'el gato','dog':'el perro','lion':'el león','fish':'el pez',
'red':'el rojo','blue':'el azul','green':'el verde','yellow':'el amarillo',
'one':'el uno','two':'el dos','three':'el tres','four':'el cuatro',
'apple':'la manzana','car':'el auto','house':'la casa','book':'el libro',
'hand':'la mano','eye':'el ojo','nose':'la nariz','foot':'el pie',
'sun':'el sol','moon':'la luna','star':'la estrella','rocket':'el cohete'}
for en,full_es in articles.items():
    import re
    s=re.sub(r"\{w:'"+re.escape(en)+r"',s:'[^']*',e:", "{w:'%s',s:'%s',e:"%(en,full_es), s)

# La consigna española usa la forma completa con artículo.
s=s.replace("Buscá: '+current.s", "Encontrá: '+current.s")
s=s.replace("AndroidVoice.speakSpanish('Buscá '+current.s)", "AndroidVoice.speakSpanish('Encontrá '+current.s)")
s=s.replace("new SpeechSynthesisUtterance('Buscá '+current.s)", "new SpeechSynthesisUtterance('Encontrá '+current.s)")

# Alternar la felicitación: una vez inglés y la siguiente español.
old="if(item.w===current.w){locked=true;btn.classList.add('good');score++;$('feedback').textContent='⭐ ¡MUY BIEN!';$('stars').textContent='⭐'.repeat(score);voice('Great job!',true);index++;setTimeout(nextRound,2400)}"
new="if(item.w===current.w){locked=true;btn.classList.add('good');score++;$('stars').textContent='⭐'.repeat(score);const spanishPraise=(score%2===0);$('feedback').textContent=spanishPraise?'⭐ ¡BUEN TRABAJO!':'⭐ GREAT JOB!';if(spanishPraise){try{if(window.AndroidVoice&&AndroidVoice.speakSpanish){AndroidVoice.speakSpanish('Buen trabajo');}else{const u=new SpeechSynthesisUtterance('Buen trabajo');u.lang='es-AR';u.rate=.72;speechSynthesis.speak(u)}}catch(e){}}else{voice('Great job!',true)}index++;setTimeout(nextRound,2400)}"
if old not in s:
    raise SystemExit('No se encontró bloque de acierto esperado; STOP técnico')
s=s.replace(old,new)

html.write_text(s,encoding='utf-8')
print('Jugamos ajustado: artículos españoles completos y felicitaciones alternadas inglés/español.')
