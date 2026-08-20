from pathlib import Path
import re
import sys

ROOT=Path('project')
mode=(sys.argv[1] if len(sys.argv)>1 else '').strip().lower()
brands={
    'basic': {
        'label':'Fran Básico',
        'color':'#3478F6',
        'path':'M22,28h25c6,0 10,4 10,10v43c-4,-3 -8,-4 -13,-4H22z M86,28H61c-6,0 -10,4 -10,10v43c4,-3 8,-4 13,-4h22z'
    },
    'jugamos': {
        'label':'Fran Jugamos',
        'color':'#22B455',
        'path':'M54,20l9,19 21,3 -15,15 4,21 -19,-10 -19,10 4,-21 -15,-15 21,-3z'
    },
    'more': {
        'label':'Fran Más Juegos',
        'color':'#FF7F27',
        'path':'M62,20c13,3 22,12 26,25L66,67 45,46z M43,49l16,16 -8,13 -16,-16z M34,68l10,10 -16,7z M70,38a6,6 0,1 0,0.1,0z'
    }
}
if mode not in brands:
    raise SystemExit('Uso: python3 branding/apply_brand.py basic|jugamos|more')
b=brands[mode]

manifest=ROOT/'app/src/main/AndroidManifest.xml'
if not manifest.exists():
    raise SystemExit('STOP: AndroidManifest.xml no encontrado')
m=manifest.read_text(encoding='utf-8')
if re.search(r'android:label="[^"]+"',m):
    m=re.sub(r'android:label="[^"]+"',f'android:label="{b["label"]}"',m,count=1)
else:
    m=m.replace('<application',f'<application android:label="{b["label"]}"',1)
if re.search(r'android:icon="[^"]+"',m):
    m=re.sub(r'android:icon="[^"]+"','android:icon="@drawable/fran_icon"',m,count=1)
else:
    m=m.replace('<application','<application android:icon="@drawable/fran_icon"',1)
manifest.write_text(m,encoding='utf-8')

# Marcador verificable para el gate del build. No se usa para el label si el manifest
# ya lo declara de forma literal.
values=ROOT/'app/src/main/res/values'
values.mkdir(parents=True,exist_ok=True)
strings=values/'strings.xml'
if strings.exists():
    s=strings.read_text(encoding='utf-8')
    if '<string name="app_name">' in s:
        s=re.sub(r'(<string name="app_name">).*?(</string>)',lambda mo: mo.group(1)+b['label']+mo.group(2),s,count=1,flags=re.S)
    elif '</resources>' in s and 'name="brand_label"' not in s:
        s=s.replace('</resources>',f'    <string name="brand_label">{b["label"]}</string>\n</resources>',1)
    strings.write_text(s,encoding='utf-8')
else:
    strings.write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="brand_label">{b["label"]}</string>\n</resources>\n',encoding='utf-8')

draw=ROOT/'app/src/main/res/drawable'
draw.mkdir(parents=True,exist_ok=True)
vector=f'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="{b['color']}" android:pathData="M4,4h100v100h-100z"/>
    <path android:fillColor="#FFFFFFFF" android:pathData="{b['path']}"/>
</vector>
'''
(draw/'fran_icon.xml').write_text(vector,encoding='utf-8')

final_manifest=manifest.read_text(encoding='utf-8')
if f'android:label="{b["label"]}"' not in final_manifest:
    raise SystemExit('STOP: nombre final no quedó en manifest')
if '@drawable/fran_icon' not in final_manifest:
    raise SystemExit('STOP: icono final no quedó enlazado en manifest')
if b['label'] not in strings.read_text(encoding='utf-8'):
    raise SystemExit('STOP: marcador de nombre no quedó en values')
print(f"BRANDING OK: {b['label']} / {b['color']} / @drawable/fran_icon")
