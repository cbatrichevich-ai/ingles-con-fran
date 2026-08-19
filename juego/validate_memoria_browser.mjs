import fs from 'fs';
import {spawn, spawnSync} from 'child_process';
import os from 'os';
import path from 'path';

const htmlPath = process.argv[2] || 'project/app/src/main/assets/www/JUGAMOS.html';
if (!fs.existsSync(htmlPath)) throw new Error(`HTML no encontrado: ${htmlPath}`);
const html = fs.readFileSync(htmlPath, 'utf8');
const candidates = ['google-chrome','google-chrome-stable','chromium','chromium-browser'];
let chrome = null;
for (const c of candidates) {
  const r = spawnSync('which',[c],{encoding:'utf8'});
  if (r.status===0 && r.stdout.trim()) { chrome=r.stdout.trim(); break; }
}
if (!chrome) throw new Error('Chrome/Chromium no disponible para validación visual');
const port = 9333 + Math.floor(Math.random()*200);
const profile = fs.mkdtempSync(path.join(os.tmpdir(),'jugamos-chrome-'));
const proc = spawn(chrome,[
  '--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=*',
  `--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'
],{stdio:'ignore'});

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitJson(url){
  for(let i=0;i<80;i++){
    try{ const r=await fetch(url); if(r.ok) return await r.json(); }catch{}
    await sleep(100);
  }
  throw new Error('DevTools no respondió');
}
let ws; let seq=0; const pending=new Map();
function cdp(method,params={}){
  return new Promise((resolve,reject)=>{
    const id=++seq; pending.set(id,{resolve,reject});
    ws.send(JSON.stringify({id,method,params}));
  });
}
try{
  const targets=await waitJson(`http://127.0.0.1:${port}/json`);
  const target=targets.find(t=>t.type==='page')||targets[0];
  ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
  ws.addEventListener('message',ev=>{
    const m=JSON.parse(ev.data);
    if(m.id && pending.has(m.id)){
      const p=pending.get(m.id); pending.delete(m.id);
      if(m.error)p.reject(new Error(JSON.stringify(m.error))); else p.resolve(m.result);
    }
  });
  await cdp('Page.enable'); await cdp('Runtime.enable');
  const tree=await cdp('Page.getFrameTree'); const frameId=tree.frameTree.frame.id;
  const sizes=[[1280,720],[960,540],[800,360]];
  for(const [W,H] of sizes){
    await cdp('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:false});
    await cdp('Page.setDocumentContent',{frameId,html});
    await sleep(120);
    await cdp('Runtime.evaluate',{expression:`memorySpeakPair=function(){};memoryCancelPair=function(){};cancelPromptPair=function(){};voice=function(){};`});
    const expr=`(()=>{
      const failures=[];
      startGame();
      if(deck.length!==10) failures.push('Juego 1 no tiene 10 rondas');
      if(document.querySelectorAll('#grid .card').length!==4) failures.push('Juego 1 no muestra 4 opciones');
      if(locked!==false) failures.push('Juego 1 bloquea respuesta inicial');
      const exit=[...document.querySelectorAll('button')].find(b=>b.textContent.includes('SALIR'));
      if(!exit||getComputedStyle(exit).display==='none') failures.push('SALIR no visible');
      for(let k=0;k<100;k++){
        memRound=0; nextMemory(); if(memTimer){clearTimeout(memTimer);memTimer=null;}
        const before=[...document.querySelectorAll('#grid .card')].map(b=>({w:b.dataset.word,t:b.textContent}));
        const miss=missing.w; hideMemory();
        const after=[...document.querySelectorAll('#grid .card')].map(b=>({w:b.dataset.word,t:b.textContent}));
        const opts=[...document.querySelectorAll('#memoryChoices .memory-choice')];
        if(before.length!==4||after.length!==4){failures.push('Memoria no conserva 4 posiciones');break;}
        let q=0,unchanged=0;
        for(let i=0;i<4;i++){
          if(before[i].w!==after[i].w){failures.push('Cambió el orden/conjunto entre tarjetas');break;}
          if(after[i].t==='❓'){q++;if(after[i].w!==miss)failures.push('El ? no corresponde a la faltante');}
          else if(after[i].t===before[i].t) unchanged++;
        }
        if(q!==1||unchanged!==3){failures.push('No quedan exactamente 3 iguales + 1 ?');break;}
        if(opts.length!==3||![...opts].some(b=>b.dataset.word===miss)){failures.push('Opciones no incluyen la faltante');break;}
        const box=document.getElementById('memoryChoices');
        if(box.classList.contains('hidden')||getComputedStyle(box).display==='none'){failures.push('Opciones ocultas');break;}
        const br=box.getBoundingClientRect();
        if(br.top<0||br.bottom>innerHeight||br.left<0||br.right>innerWidth){failures.push('Panel de opciones fuera de viewport');break;}
        for(const b of opts){const r=b.getBoundingClientRect();if(r.top<0||r.bottom>innerHeight||r.left<0||r.right>innerWidth){failures.push('Una opción queda fuera de viewport');break;}}
      }
      exitToMenu();
      if(!document.getElementById('game').classList.contains('hidden')||document.getElementById('home').classList.contains('hidden')) failures.push('SALIR no vuelve al menú');
      return {failures,width:innerWidth,height:innerHeight};
    })()`;
    const rr=await cdp('Runtime.evaluate',{expression:expr,returnByValue:true});
    if(rr.exceptionDetails) throw new Error(rr.exceptionDetails.text||'Excepción JS');
    const v=rr.result.value;
    if(v.failures.length) throw new Error(`${W}x${H}: ${v.failures.join('; ')}`);
    console.log(`OK ${W}x${H}: 100 rondas memoria + Juego 1 + SALIR + viewport`);
  }
  console.log('VALIDACIÓN VISUAL/RUNTIME OK');
} finally {
  try{ws?.close();}catch{}
  try{proc.kill('SIGKILL');}catch{}
  try{fs.rmSync(profile,{recursive:true,force:true});}catch{}
}
