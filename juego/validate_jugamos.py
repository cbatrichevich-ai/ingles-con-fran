from pathlib import Path
import re

html=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=html.read_text(encoding='utf-8')

expected={
'cat':'el gato','dog':'el perro','lion':'el león','fish':'el pez',
'red':'el rojo','blue':'el azul','green':'el verde','yellow':'el amarillo',
'one':'el uno','two':'el dos','three':'el tres','four':'el cuatro',
'apple':'la manzana','car':'el auto','house':'la casa','book':'el libro',
'hand':'la mano','eye':'el ojo','nose':'la nariz','foot':'el pie',
'sun':'el sol','moon':'la luna','star':'la estrella','rocket':'el cohete'}

errors=[]
for en,es in expected.items():
    pat=r"\{w:'"+re.escape(en)+r"',s:'"+re.escape(es)+r"',e:"
    if not re.search(pat,s):
        errors.append(f'Falta o está alterado el ítem {en} -> {es}')

if len(re.findall(r"\{w:'",s)) < 24:
    errors.append('Hay menos de 24 ítems de vocabulario')
if "voice('Find the '+current.w)" not in s:
    errors.append('La consigna inglesa ya no usa la palabra actual')
if "3200" not in s:
    errors.append('No está aplicada la pausa anti-corte de 3200 ms')
if "Buen trabajo" not in s or "Great job!" not in s:
    errors.append('No están ambas felicitaciones')

if errors:
    raise SystemExit('VALIDACIÓN FALLÓ:\n- ' + '\n- '.join(errors))
print('VALIDACIÓN OK: 24 ítems completos, artículos correctos, consigna inglesa intacta y premios bilingües.')
