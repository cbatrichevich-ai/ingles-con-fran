import fs from 'fs';
import {spawn,spawnSync} from 'child_process';
import os from 'os';
import path from 'path';

const htmlPath=process.argv[2]||'project/app/src/main/assets/www/ABRIR-INGLES-CON-FRAN.html';
if(!fs.existsSync(htmlPath)) throw new Error(`HTML no encontrado: ${htmlPath}`);
const html=fs.readFileSync(htmlPath,'utf8');
let chrome=null;
for(const c of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){
  const r=spawnSync('which',[c],{encoding:'utf8'}); if(r.status===0&&r.stdout.trim()){chrome=r.stdout.trim();break;}
}
if(!chrome) throw new Error('Chrome/Chromium no disponible');
const port=9650+Math.floor(Math.random()*150), profile=fs.mkdtempSync(path.join(os.tmpdir(),'fran-basic-'));
const proc=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=*',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitJson(url){for(let i=0;i<80;i++){try{const r=await fetch(url);if(r.ok)return await r.json()}catch{}await sleep(100)}throw new Error('DevTools no respondió')}
let ws,seq=0;const pending=new Map();
function cdp(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
try{
 const targets=await waitJson(`http://127.0.0.1:${port}/json`);const target=targets.find(t=>t.type==='page')||targets[0];
 ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true})});
 ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}});
 await cdp('Page.enable');await cdp('Runtime.enable');const tree=await cdp('Page.getFrameTree');const frameId=tree.frameTree.frame.id;
 const sizes=[[1280,800,'tablet'],[960,540,'tablet-compacta'],[854,393,'phone'],[800,360,'phone'],[740,360,'phone']];
 for(const [W,H,label] of sizes){
  await cdp('Emulation.setDeviceMetricsOverride',{width:W,height:H,deviceScaleFactor:1,mobile:false});
  await cdp('Page.setDocumentContent',{frameId,html});await sleep(120);
  const expr=`(()=>{const f=[];const vr=e=>{const r=e.getBoundingClientRect();return r.top>=-1&&r.left>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1};
   const mods=[...document.querySelectorAll('#home .module')];if(mods.length!==8)f.push('portada no tiene 8 módulos');
   if(innerHeight<=500){if(!mods.every(vr))f.push('algún módulo de portada queda fuera del viewport');const cs=getComputedStyle(document.querySelector('.modules'));if(cs.gridTemplateColumns.split(' ').length!==4)f.push('portada teléfono no usa 4 columnas');}
   openModule('colores');
   const top=document.querySelector('#lesson .top'), cards=[...document.querySelectorAll('#content .card')];
   if(!top||!vr(top))f.push('encabezado no visible');if(cards.length<4)f.push('colores no renderiza tarjetas');
   if(innerHeight<=500){const first=cards.slice(0,4);if(!first.every(vr))f.push('primera fila de tarjetas no entra completa');if(first.some(x=>x.getBoundingClientRect().height>118))f.push('tarjetas demasiado altas en teléfono');const tr=top.getBoundingClientRect(),cr=first[0].getBoundingClientRect();if(cr.top<tr.bottom-1)f.push('tarjetas pisan encabezado');
    const cue=document.getElementById('micCue');cue.className='miccue on listening';const mr=cue.getBoundingClientRect();if(mr.height>75)f.push('micrófono sigue sobredimensionado');
   }
   goHome();openModule('frases');const phrases=[...document.querySelectorAll('#content .phrase')];if(!phrases.length)f.push('frases no renderiza');if(innerHeight<=500&&phrases[0].getBoundingClientRect().height>100)f.push('frases demasiado altas');
   return {f,width:innerWidth,height:innerHeight};})()`;
  const rr=await cdp('Runtime.evaluate',{expression:expr,returnByValue:true});if(rr.exceptionDetails)throw new Error(rr.exceptionDetails.text||'Excepción JS');const v=rr.result.value;if(v.f.length)throw new Error(`${W}x${H}: ${v.f.join('; ')}`);console.log(`OK ${W}x${H} ${label}: portada + encabezado + tarjetas + micrófono + frases`);
 }
 console.log('VALIDACIÓN BÁSICA RESPONSIVE RUNTIME OK');
} finally {try{ws?.close()}catch{}try{proc.kill('SIGKILL')}catch{}try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
