from pathlib import Path
import runpy,re
runpy.run_path('lab/apply_candidate.py',run_name='__main__')
p=Path('project/app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html')
h=p.read_text(encoding='utf-8')
# Tolerancias basadas exclusivamente en fallos físicos observados. Android puede devolver forma fonética cercana.
needle="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],DOG:['DOCK','DAWG']};"
repl="const aliases={RED:['READ','BREAD'],WHITE:['WIDE','WAIT'],GREEN:['GRIN'],TWO:['TO','TOO'],SIX:['SICKS'],EIGHT:['ATE'],NINE:['NIN'],TWELVE:['TWELV'],DOG:['DOCK','DAWG'],CAT:['CAP','KAT'],BIRD:['BURD','BERT'],PIG:['PICK','BIG'],HEAD:['HED','HAD'],EAR:['EER','HERE'],HAND:['HEND','AND']};"
if needle not in h: raise SystemExit('aliases no localizado')
h=h.replace(needle,repl,1)
# Extraer y reportar las entradas reales de frases para que el workflow pueda bloquear mapeos españoles.
for phrase in ['I like English','Hello, I am from']:
    pos=h.lower().find(phrase.lower())
    if pos<0: raise SystemExit('frase no localizada: '+phrase)
    print('MAPA',phrase,repr(h[max(0,pos-300):pos+500]))
p.write_text(h,encoding='utf-8')
