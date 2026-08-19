from pathlib import Path

p=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=p.read_text(encoding='utf-8')

# Menú: dos juegos claramente separados.
old='<button class="bigbtn" onclick="startGame()">JUGAR</button><div class="small">Escuchá y encontrá la imagen.</div>'
new='<button class="bigbtn" onclick="startGame()">ENCONTRÁ LA IMAGEN</button><div class="small">Escuchá y encontrá la imagen.</div><button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button><div class="small">Mirá, recordá y descubrí qué imagen desapareció.</div>'
if old not in s:
    raise SystemExit('ERROR: no se encontró el menú base exacto; no se genera APK')
s=s.replace(old,new,1)

# Barra superior: salida real y repetición que respeta el juego activo.
top_old='<div class="top"><div id="round" class="round"></div><button class="listen" onclick="sayPrompt()">🔊 OTRA VEZ</button><div id="stars" class="stars"></div></div>'
top_new='<div class="top"><button class="listen" onclick="exitToMenu()">⬅ SALIR</button><div id="round" class="round"></div><button class="listen" onclick="repeatCurrentPrompt()">🔊 OTRA VEZ</button><div id="stars" class="stars"></div></div>'
if top_old not in s:
    raise SystemExit('ERROR: no se encontró la barra superior del juego')
s=s.replace(top_old,top_new,1)

# Zona independiente de respuestas de memoria.
grid_old='<div id="grid" class="grid"></div><div id="feedback" class="feedback"></div>'
grid_new='<div id="grid" class="grid"></div><div id="memoryChoices" class="memory-choices hidden"></div><div id="feedback" class="feedback"></div>'
if grid_old not in s:
    raise SystemExit('ERROR: no se encontró la grilla principal')
s=s.replace(grid_old,grid_new,1)

# La pantalla de memoria usa cuatro posiciones horizontales y reserva físicamente el borde inferior
# para las opciones. Las opciones quedan fijas dentro del viewport: no pueden caer fuera de pantalla.
css='''#game.memory-mode{justify-content:flex-start;padding:8px 12px 128px}
#game.memory-mode .top{flex:0 0 auto}
#game.memory-mode .prompt{font-size:clamp(22px,3.2vw,40px);margin:4px 0 8px;flex:0 0 auto}
#game.memory-mode .grid{width:min(96vw,1050px);height:min(34vh,150px);grid-template-columns:repeat(4,1fr);grid-template-rows:1fr;gap:10px;flex:0 0 auto}
#game.memory-mode .card{font-size:clamp(42px,6vw,78px);border-radius:20px;box-shadow:0 6px 0 #c7dce8}
.memory-choices{position:fixed;left:50%;transform:translateX(-50%);bottom:8px;z-index:40;width:min(96vw,820px);display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px;padding:7px 10px 10px;background:rgba(244,251,255,.98);border-radius:18px}
.memory-label{width:100%;text-align:center;font-size:clamp(16px,2vw,23px);font-weight:900;line-height:1.05}
.memory-choice{border:0;border-radius:18px;background:white;box-shadow:0 5px 0 #c7dce8;font-size:clamp(36px,5.5vw,66px);min-width:92px;padding:5px 16px;cursor:pointer}
.memory-choice:active{transform:scale(.96)}
#game.memory-mode .feedback{position:fixed;left:0;right:0;bottom:108px;z-index:41;height:30px;margin:0;text-align:center;font-size:clamp(18px,2.3vw,28px);pointer-events:none}
'''
if '</style>' not in s:
    raise SystemExit('ERROR: no se encontró cierre CSS')
s=s.replace('</style>',css+'</style>',1)

# Juego 1 debe limpiar cualquier estado visual dejado por memoria.
needle='function startGame(){'
if needle not in s:
    raise SystemExit('ERROR: no se encontró startGame')
s=s.replace(needle,"function startGame(){jugamosMode='find';$('game').classList.remove('memory-mode');if($('memoryChoices')){$('memoryChoices').classList.add('hidden');$('memoryChoices').innerHTML='';}",1)

# La pantalla final permite repetir el juego activo o volver al menú.
finish_old='<button class="bigbtn" onclick="startGame()">OTRA PARTIDA</button>'
finish_new='<button class="bigbtn" onclick="restartCurrentGame()">OTRA PARTIDA</button><br><button class="bigbtn" onclick="exitToMenu()">MENÚ</button>'
if finish_old not in s:
    raise SystemExit('ERROR: no se encontró botón final')
s=s.replace(finish_old,finish_new,1)

marker='</body></html>'
if marker not in s:
    raise SystemExit('ERROR: cierre HTML no encontrado')

script=r'''<script>
let jugamosMode='find';
let memRound=0, memScore=0, memSet=[], missing=null, memLocked=false, memTimer=null, memPhase='memorize';
function memorySpeakPair(en,es){
 try{if(window.AndroidVoice&&AndroidVoice.speakPair){AndroidVoice.speakPair(en,es);return}}catch(e){}
 if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(en);u.lang='en-US';u.rate=.68;u.onend=()=>{setTimeout(()=>{const v=new SpeechSynthesisUtterance(es);v.lang='es-AR';v.rate=.72;speechSynthesis.speak(v)},180)};speechSynthesis.speak(u)}
}
function memoryCancelPair(){try{if(window.AndroidVoice&&AndroidVoice.cancelPair)AndroidVoice.cancelPair()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel()}
function repeatCurrentPrompt(){
 if(jugamosMode!=='memory'){sayPrompt();return}
 if(memPhase==='question') memorySpeakPair("What's missing?",'¿Cuál falta?');
 else memorySpeakPair('Look and remember','Mirá y recordá');
}
function exitToMenu(){
 memoryCancelPair(); try{if(window.AndroidVoice&&AndroidVoice.stop)AndroidVoice.stop()}catch(e){}
 if(memTimer){clearTimeout(memTimer);memTimer=null}
 $('game').classList.remove('memory-mode');
 $('memoryChoices').classList.add('hidden'); $('memoryChoices').innerHTML=''; $('feedback').textContent='';
 show('home');
}
function restartCurrentGame(){if(jugamosMode==='memory')startMemory();else startGame()}
function startMemory(){
 jugamosMode='memory';memRound=0;memScore=0;memPhase='memorize';
 $('game').classList.add('memory-mode');show('game');nextMemory();
}
function nextMemory(){
 if(memRound>=8){
  memoryCancelPair();if(memTimer){clearTimeout(memTimer);memTimer=null}
  $('memoryChoices').classList.add('hidden');$('game').classList.remove('memory-mode');show('finish');
  $('finalText').textContent=`Conseguiste ${memScore} estrellas`;voice('Fantastic!',true);return
 }
 memPhase='memorize';memLocked=true;$('round').textContent=`Memoria ${memRound+1} de 8`;$('stars').textContent='⭐'.repeat(memScore);$('feedback').textContent='';
 $('memoryChoices').classList.add('hidden');$('memoryChoices').innerHTML='';
 // TARJETA 1: se eligen cuatro imágenes una sola vez para toda la ronda.
 memSet=shuffle([...ITEMS]).slice(0,4); missing=memSet[Math.floor(Math.random()*4)];
 $('prompt').innerHTML='👀 Look and remember<br><span style="font-size:.58em;font-weight:700">Mirá y recordá</span>';
 $('grid').innerHTML='';memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;b.dataset.word=o.w;$('grid').appendChild(b)});
 memorySpeakPair('Look and remember','Mirá y recordá');memTimer=setTimeout(hideMemory,4300);
}
function hideMemory(){
 memTimer=null;memoryCancelPair();memPhase='question';
 $('prompt').innerHTML='❓ What’s missing?<br><span style="font-size:.58em;font-weight:700">¿Cuál falta?</span>';
 // TARJETA 2: se reutiliza EL MISMO memSet, en EL MISMO ORDEN. Sólo una posición pasa a ❓.
 $('grid').innerHTML='';
 memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.dataset.word=o.w;b.disabled=true;b.textContent=(o.w===missing.w?'❓':o.e);$('grid').appendChild(b)});
 // Respuestas SIEMPRE visibles en una franja fija inferior: correcta + dos distractores.
 const distract=shuffle(ITEMS.filter(x=>!memSet.some(m=>m.w===x.w))).slice(0,2);const opts=shuffle([missing,...distract]);
 const box=$('memoryChoices');box.innerHTML='<div class="memory-label">Elegí la imagen que falta:</div>';
 opts.forEach(o=>{const b=document.createElement('button');b.className='memory-choice';b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>chooseMemory(b,o);box.appendChild(b)});
 box.classList.remove('hidden');memLocked=false;memorySpeakPair("What's missing?",'¿Cuál falta?');
}
function chooseMemory(btn,o){
 if(memLocked)return;memoryCancelPair();
 if(o.w===missing.w){
  memLocked=true;btn.classList.add('good');memScore++;$('stars').textContent='⭐'.repeat(memScore);
  const spanish=(memRound%2===1);$('feedback').textContent=spanish?'⭐ ¡BUEN TRABAJO!':'⭐ GREAT JOB!';
  if(spanish){try{AndroidVoice.speakSpanish('Buen trabajo')}catch(e){}}else voice('Great job!',true);
  memRound++;memTimer=setTimeout(nextMemory,2400)
 }else{
  btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';memorySpeakPair('Try again','Probá otra vez')
 }
}
</script>'''
s=s.replace(marker,script+marker,1)

required=[
 'onclick="startMemory()"','¿CUÁL FALTA?','onclick="exitToMenu()"','⬅ SALIR',
 "grid-template-columns:repeat(4,1fr)",'.memory-choices{position:fixed','bottom:8px',
 'slice(0,4)','memSet.forEach','b.textContent=(o.w===missing.w?\'❓\':o.e)',
 'Elegí la imagen que falta:','box.classList.remove(\'hidden\')','restartCurrentGame()','repeatCurrentPrompt()'
]
missing_req=[x for x in required if x not in s]
if missing_req:
    raise SystemExit('ERROR Juego 2 incompleto: '+repr(missing_req))
p.write_text(s,encoding='utf-8')
print('Juego 2 corregido: mismas 4 imágenes, una sola falta y respuestas fijadas dentro del viewport.')
