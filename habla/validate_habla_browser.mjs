import fs from 'fs';
import {spawn,spawnSync} from 'child_process';
import os from 'os';
import path from 'path';

const htmlPath=process.argv[2]||'project/app/src/main/assets/www/FRAN-HABLA.html';
if(!fs.existsSync(htmlPath))throw new Error(`HTML no encontrado: ${htmlPath}`);
const html=fs.readFileSync(htmlPath,'utf8');
let chrome=null;
for(const c of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){const r=spawnSync('which',[c],{encoding:'utf8'});if(r.status===0&&r.stdout.trim()){chrome=r.stdout.trim();break;}}
if(!chrome)throw new Error('Chrome/Chromium no disponible');
const port=9750+Math.floor(Math.random()*180),profile=fs.mkdtempSync(path.join(os.tmpdir(),'fran-habla-'));
const proc=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--remote-allow-origins=*',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitTargets(){for(let i=0;i<220;i++){try{const r=await fetch(`http://127.0.0.1:${port}/json`);if(r.ok){const a=await r.json();if(Array.isArray(a)&&a.length)return a}}catch{}await sleep(100)}throw new Error('DevTools no respondió')}
let ws,seq=0;const pending=new Map();
function cdp(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
try{
 const targets=await waitTargets(),target=targets.find(t=>t.type==='page')||targets[0];
 ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true})});
 ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}});
 await cdp('Page.enable');await cdp('Runtime.enable');const tree=await cdp('Page.getFrameTree'),frameId=tree.frameTree.frame.id;
 for(const [W,H,label] of [[1280,800,'tablet'],[960,540,'compacta'],[854,393,'phone'],[800,360,'phone']]){
  await cdp('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:false});
  await cdp('Page.setDocumentContent',{frameId,html});await sleep(160);
  await cdp('Runtime.evaluate',{expression:`if(typeof renderMenu==='function')renderMenu(); window.__realCoachSequence=coachSequence; sayPair=(en,es)=>Promise.resolve(true); sayOne=(t,l)=>Promise.resolve(true); cancelAudio=()=>{}; coachSequence=(i,x,t)=>{document.getElementById('turn').classList.remove('hidden');setCoach('🗣️ Tu turno','listening');return Promise.resolve();};`});
  const expr=`(async()=>{const f=[];const tick=(ms=0)=>new Promise(r=>setTimeout(r,ms));const inside=e=>{if(!e){f.push('elemento inexistente');return}const r=e.getBoundingClientRect(),s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden')f.push('elemento oculto');if(r.left<-1||r.top<-1||r.right>innerWidth+1||r.bottom>innerHeight+1)f.push('elemento fuera viewport')};
   renderMenu();show('home');const tiles=[...document.querySelectorAll('.tile')];if(tiles.length!==8)f.push('portada no tiene 8 familias');tiles.forEach(inside);inside(document.querySelector('.exit'));
   if(tiles.length===8){const hs=tiles.map(x=>x.getBoundingClientRect().height),ww=tiles.map(x=>x.getBoundingClientRect().width);if(Math.max(...hs)-Math.min(...hs)>2||Math.max(...ww)-Math.min(...ww)>2)f.push('familias desparejas')}
   for(const k of Object.keys(CATS)){openCategory(k);const c=CATS[k],opts=[...document.querySelectorAll('.option')],expected=Math.min(4,c.opts.length);if(opts.length!==expected)f.push(k+': cantidad visible incorrecta');inside(document.querySelector('.top'));inside(document.querySelector('.starter'));inside(document.querySelector('.options'));opts.forEach(inside);const idx=Number(opts[0].dataset.idx||0),x=c.opts[idx];choosePhrase(idx,opts[0]);await tick();const p=document.getElementById('phrase');if(p.classList.contains('hidden'))f.push(k+': contenido no aparece');if(!p.textContent.includes(x.fEn)||!p.textContent.includes(x.fEs))f.push(k+': falta EN/ES');inside(p);const turn=document.getElementById('turn');if(turn.classList.contains('hidden'))f.push(k+': no marca turno oral');inside(turn);inside(document.getElementById('micStatus'));if(c.opts.length>4){const nav=document.getElementById('pageNav');if(nav.classList.contains('hidden'))f.push(k+': paginación oculta');inside(nav)}goHome()}
   openCategory('months');if(document.getElementById('pageInfo').textContent!=='1 / 3')f.push('meses: página inicial incorrecta');changeOptionPage(1);await tick();const first2=document.querySelector('.option');if(optionPage!==1||!first2||first2.dataset.idx!=='4')f.push('meses: página 2 no empieza en May');goHome();
   if(${W}===1280){
     coachSequence=window.__realCoachSequence;TURN_WORD_MS=0;TURN_PHRASE_MS=0;TURN_END_MS=0;let log=[];sayPair=(en,es)=>{log.push('PAIR:'+en+'|'+es);return Promise.resolve(true)};sayOne=(t,l)=>{log.push(l+':'+t);return Promise.resolve(true)};cancelAudio=()=>{};
     openCategory('months');let mo=[...document.querySelectorAll('.option')];choosePhrase(0,mo[0]);await tick(650);const exp=['PAIR:January|Enero','es:Ahora vos. Decí:','en:January','es:Bien. Una vez más:','en:January','es:Muy bien por practicar. Seguimos.'];for(let i=0;i<exp.length;i++)if(log[i]!==exp[i])f.push('meses: secuencia oral incorrecta en paso '+(i+1));if(Object.keys(sessionVisits).length!==12)f.push('meses: no avanzó automáticamente por los 12');if((sessionVisits[0]||0)!==1)f.push('meses: repitió January en loop');
     log=[];openCategory('want');let wo=[...document.querySelectorAll('.option')];choosePhrase(0,wo[0]);await tick(300);const exp2=['PAIR:I want water|Quiero agua','es:Ahora vos. Decí:','en:I want water','es:Bien. Una vez más:','en:I want water','es:Muy bien por practicar. Seguimos.'];for(let i=0;i<exp2.length;i++)if(log[i]!==exp2[i])f.push('frase: secuencia oral incorrecta en paso '+(i+1));if(Object.keys(sessionVisits).length!==4)f.push('frases: no avanzó automáticamente por las 4');goHome();
   }
   return {f,w:innerWidth,h:innerHeight};})()`;
  const rr=await cdp('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(rr.exceptionDetails)throw new Error(rr.exceptionDetails.text||'Excepción JS');const v=rr.result.value;if(v.f.length)throw new Error(`${W}x${H} ${label}: ${v.f.join('; ')}`);console.log(`OK ${W}x${H} ${label}: 8 familias + teacher oral + dos turnos cortos + avance automático`)
 }
 console.log('VALIDACIÓN FRAN HABLA RUNTIME OK');
}finally{try{ws?.close()}catch{}try{proc.kill('SIGKILL')}catch{}try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
