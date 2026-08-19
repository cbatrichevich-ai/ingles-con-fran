from pathlib import Path

p=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=p.read_text(encoding='utf-8')

# Menú: dos juegos claramente separados.
old='<button class="bigbtn" onclick="startGame()">JUGAR</button><div class="small">Escuchá y encontrá la imagen.</div>'
new='<button class="bigbtn" onclick="startGame()">ENCONTRÁ LA IMAGEN</button><div class="small">Escuchá y encontrá la imagen.</div><button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button><div class="small">Mirá, recordá y descubrí qué imagen desapareció.</div>'
if old not in s:
    raise SystemExit('ERROR: no se encontró el menú base exacto; no se genera APK')
s=s.replace(old,new,1)

# Botón SALIR visible dentro del juego.
top_old='<div class="top"><div id="round" class="round"></div><button class="listen" onclick="sayPrompt()">🔊 OTRA VEZ</button><div id="stars" class="stars"></div></div>'
top_new='<div class="top"><button class="listen" onclick="exitToMenu()">⬅ SALIR</button><div id="round" class="round"></div><button class="listen" onclick="sayPrompt()">🔊 OTRA VEZ</button><div id="stars" class="stars"></div></div>'
if top_old not in s:
    raise SystemExit('ERROR: no se encontró la barra superior del juego')
s=s.replace(top_old,top_new,1)

# Zona independiente de opciones de memoria; no reemplaza las imágenes recordadas.
grid_old='<div id="grid" class="grid"></div><div id="feedback" class="feedback"></div>'
grid_new='<div id="grid" class="grid"></div><div id="memoryChoices" class="memory-choices hidden"></div><div id="feedback" class="feedback"></div>'
if grid_old not in s:
    raise SystemExit('ERROR: no se encontró la grilla principal')
s=s.replace(grid_old,grid_new,1)

# CSS compacto para tres opciones debajo, manteniendo visibles las imágenes originales.
s=s.replace('.feedback{height:54px;', '.memory-choices{width:min(92vw,760px);display:flex;justify-content:center;gap:16px;margin-top:10px}.memory-choice{border:0;border-radius:20px;background:white;box-shadow:0 6px 0 #c7dce8;font-size:clamp(42px,6vw,78px);min-width:120px;padding:8px 20px;cursor:pointer}.memory-choice:active{transform:scale(.96)}.feedback{height:54px;',1)

marker='</body></html>'
if marker not in s:
    raise SystemExit('ERROR: cierre HTML no encontrado')

script=r'''<script>
let memRound=0, memScore=0, memSet=[], missing=null, memLocked=false, memTimer=null;
function memorySpeakPair(en,es){
 try{if(window.AndroidVoice&&AndroidVoice.speakPair){AndroidVoice.speakPair(en,es);return}}catch(e){}
 if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(en);u.lang='en-US';u.rate=.68;u.onend=()=>{setTimeout(()=>{const v=new SpeechSynthesisUtterance(es);v.lang='es-AR';v.rate=.72;speechSynthesis.speak(v)},180)};speechSynthesis.speak(u)}
}
function memoryCancelPair(){try{if(window.AndroidVoice&&AndroidVoice.cancelPair)AndroidVoice.cancelPair()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel()}
function exitToMenu(){
 memoryCancelPair(); try{if(window.AndroidVoice&&AndroidVoice.stop)AndroidVoice.stop()}catch(e){}
 if(memTimer){clearTimeout(memTimer);memTimer=null}
 $('memoryChoices').classList.add('hidden'); $('memoryChoices').innerHTML=''; show('home');
}
function startMemory(){memRound=0;memScore=0;show('game');nextMemory()}
function nextMemory(){
 if(memRound>=8){$('memoryChoices').classList.add('hidden');show('finish');$('finalText').textContent=`Conseguiste ${memScore} estrellas`;voice('Fantastic!',true);return}
 memLocked=true;$('round').textContent=`Memoria ${memRound+1} de 8`;$('stars').textContent='⭐'.repeat(memScore);$('feedback').textContent='';
 $('memoryChoices').classList.add('hidden');$('memoryChoices').innerHTML='';
 // Se muestran CUATRO imágenes y se conservan exactamente esas mismas para la pregunta.
 memSet=shuffle([...ITEMS]).slice(0,4); missing=memSet[Math.floor(Math.random()*4)];
 $('prompt').innerHTML='👀 Look and remember<br><span style="font-size:.58em;font-weight:700">Mirá y recordá</span>';
 $('grid').innerHTML=''; memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;b.dataset.word=o.w;$('grid').appendChild(b)});
 memorySpeakPair('Look and remember','Mirá y recordá'); memTimer=setTimeout(hideMemory,4300);
}
function hideMemory(){
 memTimer=null; memoryCancelPair();
 $('prompt').innerHTML='❓ What’s missing?<br><span style="font-size:.58em;font-weight:700">¿Cuál falta?</span>';
 // MISMA grilla, MISMAS posiciones: sólo desaparece una imagen y queda un signo de pregunta.
 $('grid').innerHTML='';
 memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.dataset.word=o.w;if(o.w===missing.w){b.textContent='❓';b.disabled=true}else{b.textContent=o.e;b.disabled=true}$('grid').appendChild(b)});
 // Las opciones se muestran aparte: la correcta + dos distractores. Nunca reemplazan la grilla recordada.
 const distract=shuffle(ITEMS.filter(x=>!memSet.some(m=>m.w===x.w))).slice(0,2);const opts=shuffle([missing,...distract]);
 const box=$('memoryChoices');box.innerHTML='';opts.forEach(o=>{const b=document.createElement('button');b.className='memory-choice';b.textContent=o.e;b.dataset.word=o.w;b.onclick=()=>chooseMemory(b,o);box.appendChild(b)});box.classList.remove('hidden');memLocked=false;
 memorySpeakPair("What's missing?",'¿Cuál falta?');
}
function chooseMemory(btn,o){
 if(memLocked)return;memoryCancelPair();
 if(o.w===missing.w){memLocked=true;btn.classList.add('good');memScore++;$('stars').textContent='⭐'.repeat(memScore);const spanish=(memRound%2===1);$('feedback').textContent=spanish?'⭐ ¡BUEN TRABAJO!':'⭐ GREAT JOB!';if(spanish){try{AndroidVoice.speakSpanish('Buen trabajo')}catch(e){}}else voice('Great job!',true);memRound++;memTimer=setTimeout(nextMemory,2400)}
 else{btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';memorySpeakPair('Try again','Probá otra vez')}
}
</script>'''
s=s.replace(marker,script+marker,1)

# Barrera material de salida: botón visible + conservación de la misma grilla + 4 imágenes + opción separada.
required=[
 'onclick="startMemory()"','¿CUÁL FALTA?','function startMemory()','What’s missing?','Mirá y recordá',
 'onclick="exitToMenu()"','⬅ SALIR','slice(0,4)','memSet.forEach','memoryChoices','memory-choice','b.textContent=\'❓\''
]
missing_req=[x for x in required if x not in s]
if missing_req:
    raise SystemExit('ERROR Juego 2 incompleto: '+repr(missing_req))
p.write_text(s,encoding='utf-8')
print('Juego 2 corregido: salida visible, 4 imágenes fijas y una sola desaparece manteniendo las otras tres.')
