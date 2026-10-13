import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const ritual=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extractRegion=new Function('THREE',ritual.slice(ritual.indexOf('export function extractRegion'),ritual.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(THREE);
const code=fs.readFileSync(new URL('../dist/pine-crowns.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const {installPineCrowns}=new Function('THREE','extractRegion',code+';return {installPineCrowns};')(THREE,extractRegion);
test('pine canopy replacement preserves bamboo rings sharing its material and supports both LODs',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene(),near=new THREE.Group();
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([0,2,0,1,2,0,0,2.1,1, 0,2,-12,1,2,-12,0,2.1,-11],3));
 const m=new THREE.MeshStandardMaterial();m.name='Deep green pine needles';root.add(new THREE.Mesh(g,m));
 for(let i=0;i<12;i++){const o=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());o.name=`pine-${i}`;near.add(o);}
 const result=installPineCrowns(root,near,near.clone(),scene);assert.equal(result.oldTriangles,1);assert.equal(g.index.count,3);assert.equal(result.levels.length,12);
 const camera=new THREE.PerspectiveCamera();camera.position.set(0,0,100);camera.updateMatrixWorld();result.update(camera);assert.ok(result.levels.every(l=>l.getCurrentLevel()===1));
 camera.position.set(0,0,2);camera.updateMatrixWorld();result.update(camera);assert.ok(result.levels.every(l=>l.getCurrentLevel()===0));
});
test('failed replacement never removes original pine foliage',()=>{
 const model=new THREE.Group();assert.throws(()=>installPineCrowns(model,new THREE.Group(),new THREE.Group(),new THREE.Scene()),/six pairs/);
});
test('pine assets preserve all trees, three-dimensional pigment geometry and distant crown extent',()=>{
 const meta=JSON.parse(fs.readFileSync(new URL('../dist/assets/pine-crowns.json',import.meta.url)));const trees=JSON.parse(fs.readFileSync(new URL('../dist/assets/garden-trees.json',import.meta.url)));
 assert.deepEqual(meta.pines,trees.pines);assert.equal(meta.crowns,36);assert.equal(meta.needleCount,84672);assert.equal(meta.distantNeedles,28224);
 const load=name=>{const b=fs.readFileSync(new URL(`../dist/assets/${name}.glb`,import.meta.url));assert.ok(b.length<6*1024*1024);return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));};
 const near=load('pine-crowns'),far=load('pine-crowns-distant');assert.equal(near.meshes.length,12);assert.equal(far.meshes.length,12);
 const find=(d,name)=>d.meshes[d.nodes.find(n=>n.name===name).mesh].primitives[0];
 for(let i=0;i<6;i++){
  const n=find(near,`Pine ${i} needles`),f=find(far,`Pine ${i} needles`);assert.ok(n.attributes.COLOR_0!==undefined&&n.attributes.NORMAL!==undefined);
  assert.equal(near.accessors[n.indices].count,far.accessors[f.indices].count*3);
  const nb=near.accessors[n.attributes.POSITION],fb=far.accessors[f.attributes.POSITION];
  for(let k=0;k<3;k++){assert.ok(Math.abs(nb.min[k]-fb.min[k])<.14);assert.ok(Math.abs(nb.max[k]-fb.max[k])<.14);}
 }
 meta.attachmentPointsNative.forEach((p,i)=>{const [x,y,h]=meta.pines[Math.floor(i/6)],j=i%6,a=j*2.35,r=(1-j*.10)*1.45;const expected=[x+Math.cos(a)*r,y+Math.sin(a)*r,.8+j*h*.14+.23];assert.ok(p.every((q,k)=>Math.abs(q-expected[k])<.00001));});
});
