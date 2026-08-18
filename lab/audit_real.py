from pathlib import Path
import re,json,sys
root=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
html=root/'app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html'
s=html.read_text(encoding='utf-8')
(out/'full.html').write_text(s,encoding='utf-8')
# Extract DATA source exactly as stored
m=re.search(r'const\s+DATA\s*=\s*(\{.*?\});\s*(?:const|let|var|function)',s,re.S)
if m:(out/'DATA-source.txt').write_text(m.group(1),encoding='utf-8')
# Functions and handlers with bodies (best-effort brace parser)
def funcs(src):
    starts=[]
    for x in re.finditer(r'(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{',src): starts.append((x.start(),x.end(),x.group(1)))
    chunks=[]
    for st,pos,name in starts:
        depth=1;i=pos
        quote=None;esc=False
        while i<len(src) and depth:
            c=src[i]
            if quote:
                if esc: esc=False
                elif c=='\\': esc=True
                elif c==quote: quote=None
            else:
                if c in "'\"`": quote=c
                elif c=='{': depth+=1
                elif c=='}': depth-=1
            i+=1
        chunks.append(f'===== {name} =====\n'+src[st:i])
    return '\n\n'.join(chunks)
(out/'functions.txt').write_text(funcs(s),encoding='utf-8')
# All audio references and direct playContent/playFile calls, preserving context
rows=['kind\tfile\tlabel\tcontext']
for pat,kind in [(r'playContent\(([^\n;]+)', 'playContent'),(r'playFile\(([^\n;]+)','playFile'),(r'(?:enAudio|esAudio)\s*:\s*["\']([^"\']+)["\']','DATA-audio')]:
    for x in re.finditer(pat,s):
        ctx=s[max(0,x.start()-180):min(len(s),x.end()+180)].replace('\n',' ')
        rows.append(f'{kind}\t{x.group(1)[:160]}\t\t{ctx[:500]}')
(out/'card-map.tsv').write_text('\n'.join(rows),encoding='utf-8')
# Inventory assets and likely positive feedback recordings
adir=root/'app/src/main/assets/www/audio'
files=sorted(p.name for p in adir.glob('*') if p.is_file())
(out/'audio-files.txt').write_text('\n'.join(files),encoding='utf-8')
# Critical tokens / counts
keys=['playContent(','playFile(','enAudio','esAudio','187.wav','prompt_ahora_vos.wav','goHome','render','hour','time','AndroidSpeech','startListening','cancelListening']
summary=[f'HTML={html}',f'HTML_BYTES={len(s.encode())}',f'AUDIO_FILES={len(files)}']+[f'{k}={s.count(k)}' for k in keys]
(out/'summary.txt').write_text('\n'.join(summary),encoding='utf-8')
print('\n'.join(summary))
