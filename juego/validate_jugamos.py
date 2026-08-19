from pathlib import Path
import re

html=Path('project/app/src/main/assets/www/JUGAMOS.html')
s=html.read_text(encoding='utf-8')
expected={'cat':'el gato','dog':'el perro','lion':'el león','fish':'el pez','red':'el rojo','blue':'el azul','green':'el verde','yellow':'el amarillo','one':'el uno','two':'el dos','three':'el tres','four':'el cuatro','apple':'la manzana','car':'el auto','house':'la casa','book':'el libro','hand':'la mano','eye':'el ojo','nose':'la nariz','foot':'el pie','sun':'el sol','moon':'la luna','star':'la estrella','rocket':'el cohete'}
errors=[]
for en,es in expected.items():
    if not re.search(r"\{w:'"+re.escape(en)+r"',s:'"+re.escape(es)+r"',e:",s): errors.append(f'Falta o está alterado {en} -> {es}')
if len(re.findall(r"\{w:'",s)) != 24: errors.append('El banco no contiene exactamente 24 ítems')
if "deck=shuffle([...ITEMS]).slice(0,10)" not in s: errors.append('Juego 1 no está limitado a 10 rondas')
if "AndroidVoice.speakPair('Find the '+current.w" not in s: errors.append('Juego 1 no usa audio bilingüe encadenado')
if "cancelPromptPair();" not in s: errors.append('La respuesta no cancela la traducción pendiente')
if "Buen trabajo" not in s or "Great job!" not in s: errors.append('No están ambas felicitaciones')
if errors: raise SystemExit('VALIDACIÓN FALLÓ:\n- '+'\n- '.join(errors))
print('VALIDACIÓN OK: banco 24, Juego 1 de 10 rondas, audio por fin real y respuesta inmediata.')
