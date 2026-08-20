import fs from 'fs';
import {spawn, spawnSync} from 'child_process';
import os from 'os';
import path from 'path';

const htmlPath=process.argv[2]||'project/app/src/main/assets/www/JUGAMOS.html';
if(!fs.existsSync(htmlPath)) throw new Error(`HTML no encontrado: ${htmlPath}`);
const html=fs.readFileSync(htmlPath,'utf8');
const candidates=['google-chrome','google-chrome-stable','chromium','chromium-browser'];
let chrome=null;
for(const c of candidates){const r=spawnSync('which',[c],{encoding:'utf8'});if(r.status===0&&r.stdout.trim()){chrome=r.stdout.trim();break;}}
if(!chrome) throw new Error('Chrome/Chromium no disponible');
const port=9550+Math.floor(Math.random()*200);
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'jugamos-responsive-'));
const proc=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=*',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitJson(url){for(let i=0;i<80;i++){try{const r=await fetch(url);if(r.ok)return await r.json();}catch{}await sleep(100)}throw new Error('DevTools no respondió')}
let ws;let seq=0;const pending=new Map();
function cdp(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
function boxCheck(nameSel){return `(()=>{const e=document.querySelector(${JSON.stringify(nameSel)});if(!e)return '${nameSel}:no-existe';const r=e.getBoundingClientRect(),st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden')return '${nameSel}:oculto';if(r.top<0||r.left<0||r.bottom>innerHeight+1||r.right>innerWidth+1)return '${nameSel}:fuera';return ''})()`}
try{
 const targets=await waitJson(`http://127.0.0.1:${port}/json`);const target=targets.find(t=>t.type==='page')||targets[0];
 ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true})});
 ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}});
 await cdp('Page.enable');await cdp('Runtime.enable');const tree=await cdp('Page.getFrameTree');const frameId=tree.frameTree.frame.id;
 const sizes=[[1280,800,'tablet'],[1280,720,'tablet'],[960,540,'compact-tablet'],[854,393,'phone'],[800,360,'phone'],[740,360,'phone']];
 for(const [W,H,label] of sizes){
   await cdp('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:false});
   await cdp('Page.setDocumentContent',{frameId,html});await sleep(120);
   await cdp('Runtime.evaluate',{expression:`memorySpeakPair=function(){};memoryCancelPair=function(){};cancelPromptPair=function(){};voice=function(){};`});
   const expr=`(()=>{
     const failures=[];
     const inside=(sel)=>{const e=document.querySelector(sel);if(!e){failures.push(sel+' no existe');return}const r=e.getBoundingClientRect(),st=getComputedStyle(e);if(st.display==='none'||st.visibility==='hidden')failures.push(sel+' oculto');if(r.top<-1||r.left<-1||r.bottom>innerHeight+1||r.right>innerWidth+1)failures.push(sel+' fuera de pantalla')};
     // Portada: dos botones de igual ancho y todo visible.
     show('home');
     const homeBtns=[...document.querySelectorAll('#home .bigbtn')];
     if(homeBtns.length!==2) failures.push('portada no tiene 2 botones');
     if(homeBtns.length===2&&Math.abs(homeBtns[0].getBoundingClientRect().width-homeBtns[1].getBoundingClientRect().width)>2) failures.push('botones portada desparejos');
     inside('#home'); homeBtns.forEach((b,i)=>inside('#home .bigbtn:nth-of-type('+(i+1)+')'));

     // Juego 1: encabezado, consigna, cuatro tarjetas y feedback deben coexistir.
     startGame();
     if(deck.length!==10) failures.push('Juego 1 no conserva 10 rondas');
     inside('#game .top');inside('#prompt');inside('#grid');inside('#feedback');
     const cards=[...document.querySelectorAll('#grid .card')];if(cards.length!==4)failures.push('Juego 1 no muestra 4 tarjetas');cards.forEach(c=>{const r=c.getBoundingClientRect();if(r.top<0||r.left<0||r.bottom>innerHeight+1||r.right>innerWidth+1)failures.push('tarjeta Juego 1 fuera')});
     const topR=document.querySelector('#game .top').getBoundingClientRect(),gridR=document.querySelector('#grid').getBoundingClientRect();
     if(gridR.top<topR.bottom) failures.push('grilla tapa encabezado');

     // Memoria: mismas cuatro posiciones, una sola falta y opciones visibles.
     startMemory();if(memTimer){clearTimeout(memTimer);memTimer=null}
     const before=[...document.querySelectorAll('#grid .card')].map(b=>({w:b.dataset.word,t:b.textContent}));const miss=missing.w;hideMemory();
     const after=[...document.querySelectorAll('#grid .card')].map(b=>({w:b.dataset.word,t:b.textContent}));
     if(before.length!==4||after.length!==4)failures.push('Memoria no conserva 4');
     let q=0,same=0;for(let i=0;i<4;i++){if(before[i].w!==after[i].w)failures.push('Memoria cambia conjunto/orden');if(after[i].t==='❓')q++;else if(after[i].t===before[i].t)same++}
     if(q!==1||same!==3)failures.push('Memoria no deja 3 iguales + 1 ?');
     const opts=[...document.querySelectorAll('#memoryChoices .memory-choice')];if(opts.length!==3)failures.push('Memoria no muestra 3 opciones');if(!opts.some(b=>b.dataset.word===miss))failures.push('Falta correcta no está en opciones');
     inside('#game .top');inside('#prompt');inside('#grid');inside('#memoryChoices');opts.forEach(b=>{const r=b.getBoundingClientRect();if(r.top<0||r.left<0||r.bottom>innerHeight+1||r.right>innerWidth+1)failures.push('opción memoria fuera')});
     exitToMenu();if(document.getElementById('home').classList.contains('hidden'))failures.push('SALIR no vuelve a portada');
     return {failures,w:innerWidth,h:innerHeight};
   })()`;
   const rr=await cdp('Runtime.evaluate',{expression:expr,returnByValue:true});if(rr.exceptionDetails)throw new Error(rr.exceptionDetails.text||'Excepción JS');const v=rr.result.value;if(v.failures.length)throw new Error(`${W}x${H} ${label}: ${v.failures.join('; ')}`);
   console.log(`OK ${W}x${H} ${label}: portada + Juego 1 + Memoria dentro de viewport`);
 }
 console.log('VALIDACIÓN RESPONSIVE RUNTIME OK');
} finally {try{ws?.close()}catch{}try{proc.kill('SIGKILL')}catch{}try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
