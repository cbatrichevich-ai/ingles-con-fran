from pathlib import Path
import re

ROOT=Path('project')

# Variante independiente: no reemplaza la app que ya usa Francisco.
for p in [ROOT/'app/build.gradle', ROOT/'app/build.gradle.kts']:
    if p.exists():
        s=p.read_text(encoding='utf-8')
        s=s.replace('com.inglesconfran.jugamos','com.inglesconfran.jugamos.adaptable')
        p.write_text(s,encoding='utf-8')

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if manifest.exists():
    s=manifest.read_text(encoding='utf-8')
    s=s.replace('com.inglesconfran.jugamos','com.inglesconfran.jugamos.adaptable')
    manifest.write_text(s,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
s=java.read_text(encoding='utf-8')
s=s.replace('package com.inglesconfran.jugamos;','package com.inglesconfran.jugamos.adaptable;')
java.write_text(s,encoding='utf-8')

strings=ROOT/'app/src/main/res/values/strings.xml'
if strings.exists():
    s=strings.read_text(encoding='utf-8')
    s=re.sub(r'(<string name="app_name">).*?(</string>)',r'\1Inglés con Fran - Jugamos Adaptable\2',s,flags=re.S)
    strings.write_text(s,encoding='utf-8')

html=ROOT/'app/src/main/assets/www/JUGAMOS.html'
s=html.read_text(encoding='utf-8')
s=s.replace('<title>Inglés con Fran - Jugamos</title>','<title>Inglés con Fran - Jugamos Adaptable</title>',1)

responsive_css=r'''
/* VARIANTE ADAPTABLE: tablet conserva amplitud; teléfono apaisado entra en modo compacto. */
#home{background:
 radial-gradient(circle at 15% 20%,rgba(255,221,87,.38) 0 7%,transparent 7.5%),
 radial-gradient(circle at 83% 18%,rgba(115,205,255,.35) 0 8%,transparent 8.5%),
 radial-gradient(circle at 82% 82%,rgba(169,131,255,.23) 0 10%,transparent 10.5%),
 linear-gradient(145deg,#f4fbff,#eef8ff)}
#home .hero{filter:drop-shadow(0 7px 5px rgba(23,50,77,.12));animation:homeFloat 2.4s ease-in-out infinite alternate}
#home .bigbtn{width:min(82vw,560px);margin-top:5px}
#home .small{margin:7px 0 13px}
@keyframes homeFloat{from{transform:translateY(-3px) rotate(-1deg)}to{transform:translateY(4px) rotate(1deg)}}

/* Teléfonos apaisados: no agrandar la interfaz hasta comerse encabezado y consigna. */
@media (max-height:500px){
  #home.screen{padding:4px 12px;justify-content:center}
  #home .hero{font-size:44px;margin:0;line-height:1}
  #home .logo{font-size:28px;margin:0 0 1px;line-height:1}
  #home .sub{font-size:16px;margin:1px 0 4px}
  #home .bigbtn{width:min(78vw,500px);padding:8px 16px;font-size:20px;border-radius:17px;box-shadow:0 5px 0 #b4c8d7;margin:4px 0}
  #home .small{display:none}

  #game.screen{padding:4px 8px;justify-content:flex-start}
  #game .top{height:36px;min-height:36px;flex:0 0 36px;gap:7px}
  #game .round{font-size:15px;white-space:nowrap}
  #game .stars{font-size:18px;letter-spacing:1px;white-space:nowrap;overflow:hidden;max-width:36vw}
  #game .listen{padding:5px 9px;font-size:15px;border-radius:13px;box-shadow:0 3px 0 #b4c8d7;white-space:nowrap}
  #game .prompt{font-size:clamp(20px,6.2vh,27px);line-height:1.02;margin:1px 0 4px;min-height:39px;flex:0 0 auto}
  #game:not(.memory-mode) .grid{width:min(90vw,720px);height:min(64vh,224px);grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:8px;flex:0 0 auto}
  #game:not(.memory-mode) .card{font-size:clamp(38px,14vh,58px);border-radius:16px;box-shadow:0 4px 0 #c7dce8}
  #game:not(.memory-mode) .feedback{height:22px;font-size:18px;line-height:22px;margin-top:2px;flex:0 0 auto}

  #game.memory-mode{padding:4px 8px 104px;justify-content:flex-start}
  #game.memory-mode .top{height:34px;min-height:34px}
  #game.memory-mode .prompt{font-size:clamp(19px,5.8vh,25px);min-height:38px;margin:1px 0 3px}
  #game.memory-mode .grid{width:min(94vw,760px);height:min(30vh,105px);gap:6px}
  #game.memory-mode .card{font-size:clamp(34px,12vh,50px);border-radius:14px;box-shadow:0 4px 0 #c7dce8}
  .memory-choices{bottom:4px;width:min(94vw,720px);gap:6px;padding:5px 7px 7px;border-radius:13px}
  .memory-label{font-size:15px;line-height:1}
  .memory-choice{font-size:clamp(30px,10vh,44px);min-width:78px;padding:3px 12px;border-radius:13px;box-shadow:0 3px 0 #c7dce8}
  #game.memory-mode .feedback{bottom:85px;height:20px;font-size:17px;line-height:20px}

  #finish.screen{padding:5px 12px}
  #finish .hero{font-size:48px;margin:0}
  #finish .logo{font-size:28px;margin:1px}
  #finish .sub{font-size:17px;margin:3px 0 7px}
  #finish .bigbtn{padding:8px 18px;font-size:19px;border-radius:17px;box-shadow:0 5px 0 #b4c8d7;margin:3px 0}
}

/* Tabletas: botones del menú siempre con la misma jerarquía visual. */
@media (min-height:501px){
  #home .bigbtn{min-height:72px}
}
'''
if '</style>' not in s:
    raise SystemExit('ERROR: no se encontró </style>')
s=s.replace('</style>',responsive_css+'\n</style>',1)

required=[
 'Jugamos Adaptable','@media (max-height:500px)','#game:not(.memory-mode) .grid',
 '#game.memory-mode .grid','#home .bigbtn{width:min(82vw,560px)',
 'com.inglesconfran.jugamos.adaptable'
]
# El último requisito vive en Android, no en HTML.
for token in required[:-1]:
    if token not in s:
        raise SystemExit('ERROR responsive incompleto: '+token)
html.write_text(s,encoding='utf-8')
print('VARIANTE ADAPTABLE preparada: tablet amplia + teléfono apaisado compacto, sin tocar la app aprobada.')
