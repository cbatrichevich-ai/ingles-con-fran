from pathlib import Path
import runpy,re
runpy.run_path('lab/apply_candidate.py',run_name='__main__')
p=Path('project/app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html')
h=p.read_text(encoding='utf-8')
needle="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],DOG:['DOCK','DAWG']};"
repl="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],TWO:['TO','TOO'],SIX:['SICKS'],EIGHT:['ATE'],NINE:['NIN'],TWELVE:['TWELV'],DOG:['DOCK','DAWG'],CAT:['CAP','KAT'],BIRD:['BURD','BERT'],PIG:['PICK','BIG'],HEAD:['HED','HAD'],EAR:['EER','HERE'],HAND:['HEND','AND']};"
if needle not in h: raise SystemExit('aliases no localizado')
h=h.replace(needle,repl,1)
# La base real identifica las dos tarjetas finales así; registrar sus mapeos sin inventar nombres.
for phrase in ['I LIKE ENGLISH.','HELLO, I AM FRAN.']:
    pos=h.find(phrase)
    if pos<0: raise SystemExit('frase real no localizada: '+phrase)
    print('MAPA REAL',phrase,repr(h[max(0,pos-180):pos+300]))
# Mantener exactamente los mapeos declarados en DATA; la prueba física indica que el contenido de 183-186
# no coincide con sus etiquetas, por lo que no se intercambian archivos a ciegas.
p.write_text(h,encoding='utf-8')
