from pathlib import Path

p=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=p.read_text(encoding='utf-8')

old='<button class="bigbtn" onclick="startGame()">JUGAR</button><div class="small">Escuchá y encontrá la imagen.</div>'
new='<button class="bigbtn" onclick="startGame()">ENCONTRÁ LA IMAGEN</button><div class="small">Escuchá y encontrá la imagen.</div><button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button><div class="small">Mirá, recordá y descubrí qué imagen desapareció.</div>'
if old not in s:
    raise SystemExit('ERROR: no se encontró el menú base exacto; no se genera APK')
s=s.replace(old,new,1)

marker='</body></html>'
if marker not in s:
    raise SystemExit('ERROR: cierre HTML no encontrado')
script=r'''<script>
let memRound=0, memScore=0, memSet=[], missing=null, memLocked=false;
function memorySpeakPair(en,es){
 try{if(window.AndroidVoice&&AndroidVoice.speakPair){AndroidVoice.speakPair(en,es);return}}catch(e){}
 if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(en);u.lang='en-US';u.rate=.68;u.onend=()=>{setTimeout(()=>{const v=new SpeechSynthesisUtterance(es);v.lang='es-AR';v.rate=.72;speechSynthesis.speak(v)},180)};speechSynthesis.speak(u)}
}
function memoryCancelPair(){try{if(window.AndroidVoice&&AndroidVoice.cancelPair)AndroidVoice.cancelPair()}catch(e){}if('speechSynthesis'in window)speechSynthesis.cancel()}
function startMemory(){memRound=0;memScore=0;show('game');nextMemory()}
function nextMemory(){
 if(memRound>=8){show('finish');$('finalText').textContent=`Conseguiste ${memScore} estrellas`;voice('Fantastic!',true);return}
 memLocked=true;$('round').textContent=`Memoria ${memRound+1} de 8`;$('stars').textContent='⭐'.repeat(memScore);$('feedback').textContent='';
 memSet=shuffle([...ITEMS]).slice(0,3); missing=memSet[Math.floor(Math.random()*3)];
 $('prompt').innerHTML='👀 Look and remember<br><span style="font-size:.58em;font-weight:700">Mirá y recordá</span>';
 $('grid').innerHTML=''; memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;$('grid').appendChild(b)});
 memorySpeakPair('Look and remember','Mirá y recordá'); setTimeout(hideMemory,4300);
}
function hideMemory(){
 memoryCancelPair();
 const remaining=memSet.filter(x=>x.w!==missing.w);
 $('prompt').innerHTML='❓ What’s missing?<br><span style="font-size:.58em;font-weight:700">¿Cuál falta?</span>';
 const distract=shuffle(ITEMS.filter(x=>!memSet.some(m=>m.w===x.w))).slice(0,2);const opts=shuffle([missing,...distract]);$('grid').innerHTML='';
 opts.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;b.onclick=()=>chooseMemory(b,o);$('grid').appendChild(b)});memLocked=false;
 memorySpeakPair("What's missing?",'¿Cuál falta?');
}
function chooseMemory(btn,o){
 if(memLocked)return;memoryCancelPair();
 if(o.w===missing.w){memLocked=true;btn.classList.add('good');memScore++;$('stars').textContent='⭐'.repeat(memScore);const spanish=(memRound%2===1);$('feedback').textContent=spanish?'⭐ ¡BUEN TRABAJO!':'⭐ GREAT JOB!';if(spanish){try{AndroidVoice.speakSpanish('Buen trabajo')}catch(e){}}else voice('Great job!',true);memRound++;setTimeout(nextMemory,2400)}
 else{btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';memorySpeakPair('Try again','Probá otra vez')}
}
</script>'''
s=s.replace(marker,script+marker,1)

required=['onclick="startMemory()"','¿CUÁL FALTA?','function startMemory()','What’s missing?','Mirá y recordá','AndroidVoice.speakPair','memoryCancelPair()']
missing_req=[x for x in required if x not in s]
if missing_req:
    raise SystemExit('ERROR Juego 2 no incorporado materialmente: '+repr(missing_req))
p.write_text(s,encoding='utf-8')
print('Juego 2 incorporado: botón visible, respuesta inmediata y audio por fin real de locución.')
