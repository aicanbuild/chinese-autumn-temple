import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const threeURL=new URL('../dist/vendor/three/three.module.js',import.meta.url).href;
const utility=fs.readFileSync(new URL('../dist/vendor/three/addons/utils/BufferGeometryUtils.js',import.meta.url),'utf8').replace("from 'three'",`from '${threeURL}'`);
const {mergeGeometries}=await import('data:text/javascript;base64,'+Buffer.from(utility).toString('base64'));
import {sampleKoiMotion} from '../dist/koi-motion.js';
import {applyKoiReaction} from '../dist/koi-reaction.js';
const makeFish=(i)=>({phase:i*.71,speed:.055+(i%5)*.00875,rx:3.2+(i%4)*1.63,rz:2.2+(i%3)*1.15,depth:-.33-(i%4)*.08,drift:i*.41,group:{scale:{x:.7+(i%4)*.115}}});
test('fish headings and pitch follow the actual route tangent through acceleration and gliding',()=>{
 for(let i=0;i<16;i++)for(let t=0;t<300;t+=.37){
  const f=makeFish(i),m=sampleKoiMotion(f,t),before=sampleKoiMotion(f,t-.001),after=sampleKoiMotion(f,t+.001);
  const dx=(after.x-before.x)/.002,dz=(after.z-before.z)/.002,dy=(after.y-before.y)/.002;
  assert.ok(Math.abs(Math.sin(Math.atan2(dx,dz)-m.yaw))<1e-7);
  assert.ok(Math.abs(Math.atan2(dy,Math.hypot(dx,dz))+m.pitch)<1e-7);
  assert.ok(Math.abs(Math.hypot(dx,dz)-m.speed)<1e-7);
  assert.ok(Math.abs(m.turnBend)<=.16&&Math.abs(m.roll)<=.045);
 }
});
test('analytic swim is independent of frame cadence, bounded for a day, and smoothly varies tail effort',()=>{
 const f=makeFish(7);let a,b;
 for(let i=0;i<=900;i++)a=sampleKoiMotion(f,i/30);
 for(let i=0;i<=1800;i++)b=sampleKoiMotion(f,i/60);
 assert.deepEqual(a,b);
 let min=Infinity,max=0;
 for(let i=0;i<16;i++)for(let t=0;t<86400;t+=13.17){
  const m=sampleKoiMotion(makeFish(i),t);
  assert.ok(Object.values(m).every(Number.isFinite));assert.ok((m.x/11.48)**2+((m.z-5.8)/6.88)**2<.9);
  assert.ok(m.y<-.25&&m.y>-.8&&m.speed>.05&&m.speed<.85);
  min=Math.min(min,m.tailAmplitude);max=Math.max(max,m.tailAmplitude);
 }
 assert.ok(max-min>.06);
 for(let t=0;t<100;t+=.03){const m=sampleKoiMotion(f,t),n=sampleKoiMotion(f,t+.001);assert.ok(Math.abs(n.tailAmplitude-m.tailAmplitude)<.00002);assert.ok(n.tailPhase>m.tailPhase);}
});
test('instanced fish share motion data across parts and shadows without adding mesh batches',()=>{
 const source=fs.readFileSync(new URL('../dist/koi.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
 const {createKoi,updateKoi}=new Function('THREE','mergeGeometries','sampleKoiMotion','applyKoiReaction',source+';return {createKoi,updateKoi};')(THREE,mergeGeometries,sampleKoiMotion,applyKoiReaction);
 const root=new THREE.Group(),scene=new THREE.Scene();
 for(const name of ['kohaku','sanke','yamabuki','platinum']){
  const group=new THREE.Group();group.name='Koi_'+name;root.add(group);
  for(const part of ['Body','Pectoral fin']){const m=new THREE.MeshStandardMaterial();m.name=part;const mesh=new THREE.Mesh(new THREE.BoxGeometry(),m);mesh.name=part;group.add(mesh);}
 }
 const fish=createKoi(root,scene,()=>.5);assert.equal(fish.length,16);assert.equal(scene.children.length,8);
 updateKoi(fish,86400);
 for(const f of fish){
  const attr=f.meshes[0].geometry.attributes.koiMotion;
  for(const mesh of f.meshes)assert.equal(mesh.geometry.attributes.koiMotion,attr);
  assert.ok(attr.getX(f.index)>=0&&attr.getX(f.index)<Math.PI*2);
  const shader={uniforms:{},vertexShader:'#include <beginnormal_vertex>\n#include <begin_vertex>'};
  f.meshes[0].material.onBeforeCompile(shader);
  const depth={uniforms:{},vertexShader:'#include <beginnormal_vertex>\n#include <begin_vertex>'};f.meshes[0].customDepthMaterial.onBeforeCompile(depth);
  assert.equal(shader.vertexShader,depth.vertexShader);
  const pectoral={uniforms:{},vertexShader:'#include <beginnormal_vertex>\n#include <begin_vertex>'};f.meshes[1].material.onBeforeCompile(pectoral);
  assert.ok(pectoral.vertexShader.includes('max(abs(position.x)-.115,0.0)'));
 }
});
