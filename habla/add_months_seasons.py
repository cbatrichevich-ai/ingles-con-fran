from pathlib import Path

ROOT=Path('project')
html=ROOT/'app/src/main/assets/www/FRAN-HABLA.html'
if not html.exists():
    raise SystemExit('STOP: FRAN-HABLA.html no encontrado')
h=html.read_text(encoding='utf-8')

# Agregar dos familias nuevas sin tocar las otras tres aplicaciones.
start=h.find('const CATS={')
if start<0:
    raise SystemExit('STOP: CATS no encontrado')
end=h.find('\n};',start)
if end<0:
    raise SystemExit('STOP: cierre de CATS no encontrado')
if "months:{icon:'📅'" not in h:
    extra=""",
 months:{icon:'📅',label:'MESES',wordMode:true,enStart:'Listen and say',esStart:'Escuchá y repetí',opts:[
  {i:'📅1',en:'January',es:'Enero',fEn:'January',fEs:'Enero'},
  {i:'📅2',en:'February',es:'Febrero',fEn:'February',fEs:'Febrero'},
  {i:'📅3',en:'March',es:'Marzo',fEn:'March',fEs:'Marzo'},
  {i:'📅4',en:'April',es:'Abril',fEn:'April',fEs:'Abril'},
  {i:'📅5',en:'May',es:'Mayo',fEn:'May',fEs:'Mayo'},
  {i:'📅6',en:'June',es:'Junio',fEn:'June',fEs:'Junio'},
  {i:'📅7',en:'July',es:'Julio',fEn:'July',fEs:'Julio'},
  {i:'📅8',en:'August',es:'Agosto',fEn:'August',fEs:'Agosto'},
  {i:'📅9',en:'September',es:'Septiembre',fEn:'September',fEs:'Septiembre'},
  {i:'📅10',en:'October',es:'Octubre',fEn:'October',fEs:'Octubre'},
  {i:'📅11',en:'November',es:'Noviembre',fEn:'November',fEs:'Noviembre'},
  {i:'📅12',en:'December',es:'Diciembre',fEn:'December',fEs:'Diciembre'}]},
 seasons:{icon:'🌎',label:'ESTACIONES',wordMode:true,enStart:'Listen and say',esStart:'Escuchá y repetí',opts:[
  {i:'🌸',en:'Spring',es:'Primavera',fEn:'Spring',fEs:'Primavera'},
  {i:'☀️',en:'Summer',es:'Verano',fEn:'Summer',fEs:'Verano'},
  {i:'🍂',en:'Autumn',es:'Otoño',fEn:'Autumn',fEs:'Otoño'},
  {i:'❄️',en:'Winter',es:'Invierno',fEn:'Winter',fEs:'Invierno'}]}"""
    h=h[:end]+extra+h[end:]

# Ocho familias: 4 columnas x 2 filas. Meses usa páginas de 4 para que nada se salga de pantalla.
extra_css="""
#menu.game-menu{grid-template-columns:repeat(4,1fr)}
.page-nav{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:6px;min-height:34px}.page-nav.hidden{display:none}.page-nav button{border:0;border-radius:12px;background:white;box-shadow:0 3px 0 #d7c9ef;padding:5px 12px;font-weight:900;color:#20324a}.page-nav span{font-weight:900;color:#6a5b82}
@media(max-height:600px){.screen{padding:5px 8px}.hero{font-size:42px}.title{font-size:27px;margin:1px 0}.sub{font-size:13px;margin:1px 0 6px}#menu.game-menu{grid-template-columns:repeat(4,1fr);gap:6px;width:min(96vw,900px)}.tile{min-height:72px;border-radius:14px;padding:4px;box-shadow:0 3px 0 #d7c9ef}.tile .ico{font-size:29px}.tile .txt{font-size:11px;margin-top:2px}.exit{padding:5px 11px;font-size:12px;margin-top:5px}.top{min-height:30px}.top button{padding:4px 8px;font-size:11px;border-radius:9px;box-shadow:0 2px 0 #d7c9ef}.family{font-size:15px}.builder{padding-top:0}.starter-row{margin:0 0 3px;gap:5px}.starter{padding:5px 9px;border-radius:12px;min-width:150px;box-shadow:0 3px 0 #5d38b3}.starter .en{font-size:18px}.starter .es{font-size:10px;margin-top:1px}.plus{font-size:21px}.options{gap:5px;width:min(96vw,900px)}.option{min-height:78px;border-radius:12px;padding:3px;box-shadow:0 3px 0 #ccdcea}.option .ico{font-size:31px}.option .en{font-size:10px;margin-top:2px}.option .es{font-size:9px;margin-top:0}.phrase{margin-top:4px;min-height:54px;padding:4px 9px;border-radius:13px;box-shadow:0 3px 0 #d8e2eb}.phrase .bigico{font-size:31px}.phrase .full-en{font-size:18px}.phrase .full-es{font-size:10px;margin-top:1px}.turn{margin-top:3px;padding:3px 10px;font-size:15px;border-radius:10px;box-shadow:0 3px 0 #dbc963}.micstatus{min-height:24px;margin-top:2px;padding:2px 7px;font-size:12px;border-radius:8px}.page-nav{min-height:22px;margin-top:1px;gap:6px}.page-nav button{padding:2px 7px;font-size:10px}.page-nav span{font-size:10px}.hint{display:none}}
"""
if '.page-nav{' not in h:
    h=h.replace('</style>',extra_css+'</style>',1)

old='<div id="options" class="options"></div><div id="phrase" class="phrase hidden"></div>'
new='<div id="options" class="options"></div><div id="pageNav" class="page-nav hidden"><button onclick="changeOptionPage(-1)">◀</button><span id="pageInfo"></span><button onclick="changeOptionPage(1)">▶</button></div><div id="phrase" class="phrase hidden"></div>'
if old not in h:
    raise SystemExit('STOP: contenedor options esperado no encontrado')
h=h.replace(old,new,1)

old_decl="let micPermissionReady=false,practiceAttempt=0,currentKeyword='',sessionVisits={},retryQueue=[];"
new_decl="let micPermissionReady=false,practiceAttempt=0,currentKeyword='',sessionVisits={},retryQueue=[],optionPage=0;"
if old_decl not in h:
    raise SystemExit('STOP: declaración de práctica no encontrada')
h=h.replace(old_decl,new_decl,1)

old_advance="function advancePhrase(){cancelMic();if(currentCat==null)return;const n=CATS[currentCat].opts.length;for(let i=0;i<n;i++){if(!sessionVisits[i]){document.querySelectorAll('.option')[i].click();return}}while(retryQueue.length){const i=retryQueue.shift();if((sessionVisits[i]||0)<2){document.querySelectorAll('.option')[i].click();return}}setMic('⭐ Muy bien. Elegí otra familia cuando quieras.','good')}"
new_advance="function showOptionIndex(i){if(currentCat==null)return;optionPage=Math.floor(i/4);renderOptionPage();const b=document.querySelector('.option[data-idx=\\\"'+i+'\\\"]');if(b)b.click()}\nfunction advancePhrase(){cancelMic();if(currentCat==null)return;const n=CATS[currentCat].opts.length;for(let i=0;i<n;i++){if(!sessionVisits[i]){showOptionIndex(i);return}}while(retryQueue.length){const i=retryQueue.shift();if((sessionVisits[i]||0)<2){showOptionIndex(i);return}}setMic('⭐ Muy bien. Elegí otra familia cuando quieras.','good')}"
if old_advance not in h:
    raise SystemExit('STOP: advancePhrase esperado no encontrado')
h=h.replace(old_advance,new_advance,1)

old_open="function openCategory(k){cancelAudio();cancelMic();currentCat=k;currentOpt=null;sessionVisits={};retryQueue=[];const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class=\"en\">${esc(c.enStart)}</div><div class=\"es\">${esc(c.esStart)}</div>`;$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setMic('');const o=$('options');o.innerHTML='';c.opts.forEach((x,i)=>{const b=document.createElement('button');b.className='option';b.innerHTML=`<span class=\"ico\">${x.i}</span><div class=\"en\">${esc(x.en)}</div><div class=\"es\">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)});show('builderScreen')}"
new_open="function renderOptionPage(){if(currentCat==null)return;const c=CATS[currentCat],o=$('options');o.innerHTML='';const start=optionPage*4,end=Math.min(start+4,c.opts.length);for(let i=start;i<end;i++){const x=c.opts[i],b=document.createElement('button');b.className='option';b.dataset.idx=String(i);b.innerHTML=`<span class=\"ico\">${x.i}</span><div class=\"en\">${esc(x.en)}</div><div class=\"es\">${esc(x.es)}</div>`;b.onclick=()=>choosePhrase(i,b);o.appendChild(b)}const nav=$('pageNav'),pages=Math.ceil(c.opts.length/4);if(pages>1){nav.classList.remove('hidden');$('pageInfo').textContent=(optionPage+1)+' / '+pages}else nav.classList.add('hidden')}\nfunction changeOptionPage(delta){if(currentCat==null)return;cancelAudio();cancelMic();const pages=Math.ceil(CATS[currentCat].opts.length/4);optionPage=Math.max(0,Math.min(pages-1,optionPage+delta));$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setMic('');renderOptionPage()}\nfunction openCategory(k){cancelAudio();cancelMic();currentCat=k;currentOpt=null;sessionVisits={};retryQueue=[];optionPage=0;const c=CATS[k];$('family').textContent=c.icon+' '+c.label;$('starter').innerHTML=`<div class=\"en\">${esc(c.enStart)}</div><div class=\"es\">${esc(c.esStart)}</div>`;const plus=document.querySelector('.plus');if(plus)plus.style.display=c.wordMode?'none':'';$('phrase').classList.add('hidden');$('turn').classList.add('hidden');setMic('');renderOptionPage();show('builderScreen')}"
if old_open not in h:
    raise SystemExit('STOP: openCategory esperado no encontrado')
h=h.replace(old_open,new_open,1)

# Mejorar tolerancia para estaciones y meses sin aceptar cualquier cosa.
old_alias="const aliases={tv:['tv','television'],bathroom:['bathroom','restroom'],water:['water'],outside:['outside'],sorry:['sorry']};"
new_alias="const aliases={tv:['tv','television'],bathroom:['bathroom','restroom'],water:['water'],outside:['outside'],sorry:['sorry'],autumn:['autumn','fall'],february:['february','febuary'],september:['september','septembre']};"
if old_alias in h:
    h=h.replace(old_alias,new_alias,1)

html.write_text(h,encoding='utf-8')
print('FRAN HABLA: meses (12) y estaciones (4) agregados con EN->ES, micrófono por palabra clave, páginas de 4 y máximo dos intentos por visita.')
