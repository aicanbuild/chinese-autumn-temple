import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const ritual=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extractRegion=new Function('THREE',ritual.slice(ritual.indexOf('export function extractRegion'),ritual.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(THREE);
const s=fs.readFileSync(new URL('../dist/bank-grass.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installBankGrass}=new Function('THREE','extractRegion',s+';return {installBankGrass};')(THREE,extractRegion);
test('legacy removal preserves rock moss, other materials, and new curved grass',()=>{
 const model=new THREE.Group(),scene=new THREE.Scene(),asset=new THREE.Group();
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([
  -.025,.18,0,.025,.18,0,.1,.5,.1, -.025,.18,0,.1,.5,.1,.2,.41,.2,
  1,.21,0,1.05,.23,0,1.06,.25,.1, 2,.65,0,2.3,.65,0,2.4,.75,.1],3));
 const m=new THREE.MeshStandardMaterial();m.name='Soft forest moss';model.add(new THREE.Mesh(g,m));
 const other=new THREE.Mesh(g.clone(),new THREE.MeshStandardMaterial());model.add(other);
 const result=installBankGrass(model,asset,scene);assert.equal(result.removedLegacyTriangles,2);assert.equal(g.index.count,6);assert.equal(other.geometry.attributes.position.count,12);assert.ok(scene.children.includes(asset));
});
test('actual grass export has fine curved leaves, pigmentation, and clear path/bridge/sand margins',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/bank-grass.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const meta=JSON.parse(fs.readFileSync(new URL('../dist/assets/bank-grass.json',import.meta.url)));
 assert.ok(meta.tufts>=45);assert.ok(meta.blades>1500);assert.equal(meta.segmentsPerBlade,12);assert.ok(meta.maxRadius<.35);
 const prims=d.meshes.flatMap(m=>m.primitives);assert.equal(prims.length,3);assert.ok(b.length<5*1024*1024);
 for(const p of prims){assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.COLOR_0!==undefined);const a=d.accessors[p.attributes.POSITION];assert.ok(a.max[1]>.3&&a.max[1]<.6);}
 for(const [x,y] of meta.centersNative){
  assert.ok(Math.abs(x)>3.05&&y<-.45);assert.ok((x/11.5)**2+((y+5.8)/6.9)**2>1.11);
  for(const cx of [-6,6])assert.ok(Math.abs(x-cx)>2.72||Math.abs(y+14)>1.37);
  for(const side of [-1,1])for(let j=0;j<27;j++)assert.ok(Math.abs(x-side*(13+.65*Math.sin(j*.17)))>1.155||Math.abs(y-(-10+j*.75))>.793);
 }
 assert.deepEqual(meta.preserved,{altar_sculpture:38,incense_vessel:196,sanctuary_interior:2384,fern_cutout_restored:96});
});
