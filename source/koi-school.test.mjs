import test from 'node:test';import assert from 'node:assert/strict';
import {sampleKoiMotion} from '../dist/koi-motion.js';import {auditSchool,reference} from './koi-school-audit.mjs';
test('school motion has analytic tangents and continuous, cadence-independent poses',()=>{
 for(const f of reference)for(let t=0;t<3600;t+=1.37){
  const a=sampleKoiMotion(f,t-.001),b=sampleKoiMotion(f,t+.001),m=sampleKoiMotion(f,t),dx=(b.x-a.x)/.002,dz=(b.z-a.z)/.002,dy=(b.y-a.y)/.002;
  assert.ok(Math.abs(Math.sin(Math.atan2(dx,dz)-m.yaw))<1e-7);assert.ok(Math.abs(Math.atan2(dy,Math.hypot(dx,dz))+m.pitch)<1e-7);assert.ok(Math.abs(Math.hypot(dx,dz)-m.speed)<1e-7);
  assert.ok(b.tailPhase>a.tailPhase);assert.ok(m.speed>.05&&m.speed<.8);
 }
 let a,b;for(let i=0;i<=900;i++)a=sampleKoiMotion(reference[3],i/30);for(let i=0;i<=1800;i++)b=sampleKoiMotion(reference[3],i/60);assert.deepEqual(a,b);
});
test('maximum-size school: animated fin and body envelopes clear each other, piers and bed for an hour',t=>{
 const result=auditSchool(reference.map(f=>({...f,group:{scale:{x:1.05}}})),{duration:3600,step:.2});
 assert.ok(result.pair>.02,JSON.stringify(result));assert.ok(result.pier>.03);assert.ok(result.bed>.02);t.diagnostic(JSON.stringify(result));
});
test('different tail phases and depth extrema remain separated through sampled day',t=>{
 const fish=reference.map((f,i)=>({...f,drift:i*.41,depth:i%2?-.58:-.33,group:{scale:{x:1.05}}}));
 const result=auditSchool(fish,{duration:86400,step:3.17});
 assert.ok(result.pair>.02,JSON.stringify(result));assert.ok(result.pier>.03);assert.ok(result.bed>.02);t.diagnostic(JSON.stringify(result));
});
