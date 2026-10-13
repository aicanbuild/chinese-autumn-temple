import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const source=fs.readFileSync(new URL('../dist/simulation-time.js',import.meta.url),'utf8').replace('export function','function');
const simulationFrame=new Function(source+';return simulationFrame')();
test('4 to 144 fps and irregular frames retain real time with collision steps no longer than 45 ms',()=>{
 for(const fps of [4,8,15,24,60,144]){
  let seconds=0,physics=0;for(let i=0;i<fps*60;i++){const f=simulationFrame(1/fps);seconds+=f.delta;for(let j=0;j<f.steps;j++){assert.ok(f.step<=.045);physics+=f.step;}}
  assert.ok(Math.abs(seconds-60)<1e-8);assert.ok(Math.abs(physics-60)<1e-8);
 }
 const deltas=[.012,.14,.04,.09,.25,.006];assert.ok(Math.abs(deltas.map(d=>simulationFrame(d).delta).reduce((a,b)=>a+b,0)-deltas.reduce((a,b)=>a+b,0))<1e-12);
});
test('long stalls and invalid timestamps cannot trigger an unbounded catch-up',()=>{
 assert.deepEqual(simulationFrame(30),{delta:.25,steps:6,step:.25/6});for(const value of [0,-1,NaN,Infinity])assert.deepEqual(simulationFrame(value),{delta:0,steps:1,step:0});
});
test('hiding and restoring the actual app clears the elapsed gap and releases held input',()=>{
 const app=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8');const line=app.split('\n').find(l=>l.startsWith("document.addEventListener('visibilitychange'"));
 let callback,now=100,suspended=0,resumed=0;const document={hidden:false,addEventListener:(name,f)=>callback=f};
 const state=new Function('document','performance','audio',`let prev=0,keys={KeyW:true},held=true;${line};return()=>({prev,keys,held});`)(document,{now:()=>now},{enabled:true,ctx:{suspend(){suspended++;},resume(){resumed++;}}});
 document.hidden=true;callback();assert.deepEqual(state(),{prev:100,keys:{},held:false});now=60000;document.hidden=false;callback();assert.equal(state().prev,60000);assert.equal(suspended,1);assert.equal(resumed,1);
});
