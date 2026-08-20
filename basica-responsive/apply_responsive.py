from pathlib import Path
import re

ROOT=Path('project')

# Variante independiente de la app básica actual: conserva lógica, audios y micrófono.
for p in [ROOT/'app/build.gradle', ROOT/'app/build.gradle.kts']:
    if p.exists():
        s=p.read_text(encoding='utf-8')
        s=s.replace('com.inglesconfran.app','com.inglesconfran.app.adaptable')
        p.write_text(s,encoding='utf-8')

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if manifest.exists():
    s=manifest.read_text(encoding='utf-8')
    s=s.replace('com.inglesconfran.app','com.inglesconfran.app.adaptable')
    manifest.write_text(s,encoding='utf-8')

java=ROOT/'app/src/main/java/com/inglesconfran/app/MainActivity.java'
s=java.read_text(encoding='utf-8')
s=s.replace('package com.inglesconfran.app;','package com.inglesconfran.app.adaptable;',1)
java.write_text(s,encoding='utf-8')

strings=ROOT/'app/src/main/res/values/strings.xml'
if strings.exists():
    s=strings.read_text(encoding='utf-8')
    s=re.sub(r'(<string name="app_name">).*?(</string>)',r'\1Inglés con Fran - Adaptable\2',s,flags=re.S)
    strings.write_text(s,encoding='utf-8')

html=ROOT/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
h=html.read_text(encoding='utf-8')
css=r'''
/* VARIANTE ADAPTABLE: tableta conserva diseño amplio; teléfono apaisado usa modo compacto. */
@media (max-height:500px){
  body{background:linear-gradient(135deg,#fff9df,#eaf8ff,#f7efff)}
  .screen{min-height:100vh;padding:4px 8px}
  .panel{width:min(96vw,980px);padding:7px 10px;border-radius:18px}
  .brand h1{font-size:27px;line-height:1;margin:0}
  .brand p{font-size:13px;line-height:1;margin:3px 0 5px}
  .modules{grid-template-columns:repeat(4,1fr);gap:6px;margin-top:5px}
  .module{border-radius:14px;padding:5px 4px;font-size:13px;line-height:1.05;box-shadow:0 3px 8px #33406a15;border-width:2px;min-height:66px;display:flex;flex-direction:column;align-items:center;justify-content:center}
  .module .ico{font-size:29px;line-height:1;margin-bottom:2px}
  .footer{display:none}

  #lesson{padding:3px 8px 8px}
  .top{position:sticky;top:0;z-index:20;max-width:none;width:100%;min-height:34px;background:rgba(244,251,255,.96);border-radius:0 0 10px 10px;padding:1px 2px}
  .top h2{font-size:19px;line-height:1;margin:3px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .btn{padding:5px 8px;font-size:11px;border-radius:10px}
  .status{font-size:13px;line-height:1.05;min-height:20px;margin:2px 0}
  .teacher{margin:4px auto;padding:5px;border-radius:12px;gap:4px}
  .grid{max-width:100%;margin:4px auto;grid-template-columns:repeat(4,1fr);gap:6px}
  .card{border-radius:13px;padding:4px;box-shadow:0 3px 8px #34406a13}
  .card img{height:50px}
  .visual{height:48px;border-radius:10px;font-size:25px}
  .en{font-size:13px;line-height:1;margin-top:3px}
  .es{font-size:10px;line-height:1;margin:2px 0 3px}
  .smallbuttons{gap:3px;flex-wrap:nowrap}
  .smallbuttons button{font-size:9px;padding:4px 5px;min-width:0}

  .timegrid{grid-template-columns:repeat(4,1fr);max-width:100%;margin:4px auto;gap:6px}
  .timegrid .card{padding:5px}
  .timegrid .card img{height:58px}
  .timegrid .smallbuttons{margin-top:4px}
  .timegrid .smallbuttons button{font-size:9px;padding:4px 5px}

  .phrasegrid{max-width:100%;margin:4px auto;grid-template-columns:repeat(2,1fr);gap:6px}
  .phrase{border-radius:13px;padding:5px;grid-template-columns:72px 1fr;gap:6px;box-shadow:0 3px 8px #34406a13}
  .phrasevisual{height:64px;border-radius:10px}
  .phrasevisual img{max-width:44px;max-height:54px}
  .phrasevisual.two img{max-width:34px}
  .phrasevisual .heart{font-size:22px}
  .phrasevisual .badge{font-size:20px;right:4px;top:3px}
  .phrasecopy strong{font-size:13px;line-height:1.05}
  .phrasecopy>span{font-size:10px;line-height:1}
  .phrasecopy .smallbuttons{margin-top:4px!important}

  .miccue{margin:3px auto 4px}
  .miccircle{width:54px;height:54px;font-size:30px;box-shadow:0 4px 12px #e8347245}
  .miccaption{font-size:12px;margin-top:2px}
  .micdiag{max-width:92vw;margin:3px auto;padding:4px 7px;border-radius:8px;font-size:10px}
}
'''
if '</style>' not in h:
    raise SystemExit('STOP: no se encontró </style> en la app básica')
h=h.replace('</style>',css+'\n</style>',1)
html.write_text(h,encoding='utf-8')
print('BÁSICA ADAPTABLE preparada: misma app educativa y micrófono; interfaz compacta sólo en teléfono apaisado; identidad independiente.')
