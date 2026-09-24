from pathlib import Path
import runpy

# Parte de la generalización existente y corrige los caminos reales que la auditoría detectó.
runpy.run_path('lab/apply_lab.py', run_name='__main__')

ROOT=Path('project')
htmlp=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
h=htmlp.read_text(encoding='utf-8')

# HORA: sus botones usaban playHoraV7 y nunca pasaban por el coordinador de micrófono.
h=h.replace("en.onclick=()=>playHoraV7(it.enAudio,it.en);","en.onclick=()=>playContent(it.enAudio,it.en,true);",1)
h=h.replace("es.onclick=()=>playHoraV7(it.esAudio,it.es);","es.onclick=()=>playContent(it.esAudio,it.es,false);",1)

# Recompensa visual breve, sin bloquear navegación ni reconocimiento siguiente.
reward_css="""
.rewardpop{position:fixed;inset:0;display:none;pointer-events:none;z-index:9999;align-items:center;justify-content:center}.rewardpop.on{display:flex;animation:rewardfade 1.35s ease forwards}.rewardbox{background:#fff;border-radius:30px;padding:22px 34px;box-shadow:0 18px 70px #20345c40;text-align:center;font-size:38px;font-weight:950;color:#31a45c;animation:rewardbounce .55s ease}.rewardstars{font-size:44px;letter-spacing:8px}@keyframes rewardbounce{0%{transform:scale(.55)}70%{transform:scale(1.12)}100%{transform:scale(1)}}@keyframes rewardfade{0%,72%{opacity:1}100%{opacity:0}}
"""
if '.rewardpop{' not in h:
    h=h.replace('</style>',reward_css+'</style>',1)
if 'id="rewardPop"' not in h:
    h=h.replace('</section>\n<section id="lesson"', '</section>\n<div id="rewardPop" class="rewardpop"><div class="rewardbox"><div class="rewardstars">⭐ ✨ ⭐</div><div>¡Muy bien!</div></div></div>\n<section id="lesson"',1)

marker="function onAndroidPermissionReady(){micPermissionReady=true;micDiag('')}"
extra="""
function showReward(){const r=document.getElementById('rewardPop');if(!r)return;r.classList.remove('on');void r.offsetWidth;r.classList.add('on');setTimeout(()=>r.classList.remove('on'),1450)}
"""
if extra.strip() not in h:
    h=h.replace(marker,extra+marker,1)

# Éxito: recompensa visible + circuito positivo ya existente de Mabel (192-196).
old="if(ok){listenToken++;currentExpected='';micCue(false);micDiag('');document.getElementById('status').textContent='✅ ¡Muy bien!'}"
new="if(ok){listenToken++;currentExpected='';micCue(false);micDiag('');document.getElementById('status').textContent='✅ ¡Muy bien!';showReward();celebrate()}"
if old not in h: raise SystemExit('STOP: no se encontró rama de éxito del reconocimiento')
h=h.replace(old,new,1)

# Tolerancia pedagógica explícita para hipótesis habituales de palabras cortas difíciles.
old2="if(ww==='RED'&&['READ','BREAD'].includes(cc))return true;"
new2="""const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],DOG:['DOCK','DAWG']};if(aliases[ww]&&aliases[ww].includes(cc))return true;"""
if old2 not in h: raise SystemExit('STOP: no se encontró tolerancia RED')
h=h.replace(old2,new2,1)

# Frases: conservar exigencia de contenido, pero admitir pequeñas pérdidas de palabras funcionales.
old3="if(wt.length&&hits/Math.max(1,wt.length)>=0.6)return true;"
new3="if(wt.length&&hits/Math.max(1,wt.length)>=0.55)return true;"
h=h.replace(old3,new3,1)

# Navegación de módulo: cancela escucha anterior antes de abrir cualquier tarjeta.
h=h.replace("function openModule(key){\n  if(key==='hora'){stopAudio();show('lesson');renderHoraV7();return;}","function openModule(key){\n  cancelListen();micDiag('');\n  if(key==='hora'){stopAudio();show('lesson');renderHoraV7();return;}",1)

htmlp.write_text(h,encoding='utf-8')
print('CANDIDATA APLICADA: Hora entra por playContent; español no abre micrófono; navegación cancela escucha; recompensa visual + celebrate existente; 187.wav preservado.')
