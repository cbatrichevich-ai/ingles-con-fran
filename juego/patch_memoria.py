from pathlib import Path

p=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=p.read_text(encoding='utf-8')

# Conserva Juego 1 y agrega entrada independiente a Juego 2.
s=s.replace('<button class="bigbtn" onclick="startGame()">JUGAR</button>', '<button class="bigbtn" onclick="startGame()">ENCONTRÁ LA IMAGEN</button><br><button class="bigbtn" onclick="startMemory()">¿CUÁL FALTA?</button>')
s=s.replace('</body></html>', r'''
<script>
let memRound=0, memScore=0, memSet=[], missing=null, memLocked=false;
function speakPair(en,es){voice(en);setTimeout(()=>{try{if(window.AndroidVoice&&AndroidVoice.speakSpanish){AndroidVoice.speakSpanish(es);return}}catch(e){}},1900)}
function startMemory(){memRound=0;memScore=0;show('game');nextMemory()}
function nextMemory(){
 if(memRound>=8){show('finish');$('finalText').textContent=`Conseguiste ${memScore} estrellas`;voice('Fantastic!',true);return}
 memLocked=true;$('round').textContent=`Memoria ${memRound+1} de 8`;$('stars').textContent='⭐'.repeat(memScore);$('feedback').textContent='';
 memSet=shuffle([...ITEMS]).slice(0,3); missing=memSet[Math.floor(Math.random()*3)];
 $('prompt').innerHTML='👀 Look and remember<br><span style="font-size:.58em;font-weight:700">Mirá y recordá</span>';
 $('grid').innerHTML=''; memSet.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;$('grid').appendChild(b)});
 speakPair('Look and remember','Mirá y recordá');
 setTimeout(hideMemory,5200);
}
function hideMemory(){
 const remaining=memSet.filter(x=>x.w!==missing.w);$('grid').innerHTML='';remaining.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;$('grid').appendChild(b)});
 $('prompt').innerHTML='❓ What’s missing?<br><span style="font-size:.58em;font-weight:700">¿Cuál falta?</span>';speakPair("What's missing?",'¿Cuál falta?');
 setTimeout(showMemoryChoices,3900);
}
function showMemoryChoices(){
 const distract=shuffle(ITEMS.filter(x=>!memSet.some(m=>m.w===x.w))).slice(0,2);const opts=shuffle([missing,...distract]);$('grid').innerHTML='';
 opts.forEach(o=>{const b=document.createElement('button');b.className='card';b.textContent=o.e;b.onclick=()=>chooseMemory(b,o);$('grid').appendChild(b)});memLocked=false;
}
function chooseMemory(btn,o){if(memLocked)return;if(o.w===missing.w){memLocked=true;btn.classList.add('good');memScore++;$('stars').textContent='⭐'.repeat(memScore);const spanish=(memRound%2===1);$('feedback').textContent=spanish?'⭐ ¡BUEN TRABAJO!':'⭐ GREAT JOB!';if(spanish){try{AndroidVoice.speakSpanish('Buen trabajo')}catch(e){}}else voice('Great job!',true);memRound++;setTimeout(nextMemory,2400)}else{btn.classList.add('bad');$('feedback').textContent='Probá otra vez 🙂';speakPair('Try again','Probá otra vez')}}
</script>
</body></html>''')
p.write_text(s,encoding='utf-8')
print('Juego 2 memoria agregado sin modificar la mecanica del Juego 1.')
