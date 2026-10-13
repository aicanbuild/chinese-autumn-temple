import {applyFoliageLighting} from '../dist/foliage-lighting.js';
import {applyWoodlandWind,createWindShadows} from './foliage-test-utils.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/woodland.json',import.meta.url)));
const source=fs.readFileSync(new URL('../dist/landscape.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createLandscape}=new Function('applyFoliageLighting','THREE','applyWoodlandWind','createWindShadows',source+';return {createLandscape}')(applyFoliageLighting,THREE,applyWoodlandWind,createWindShadows);
test('forest placement keeps the temple, pond and approach clear',()=>{
 assert.equal(layout.trees.length,620);
 for(const [x,y,z,scale,rotation,species,lod] of layout.trees){assert.ok([x,y,z,scale,rotation].every(Number.isFinite));const radius=Math.hypot(x,y);assert.ok(radius>=25.99&&radius<=143.01);assert.ok(!(y<-16&&Math.abs(x)<28&&radius<57));assert.ok(scale>.7&&scale<1.7);assert.ok(species>=0&&species<3);assert.equal(lod,+(radius>65));}
});
test('spatial instancing preserves all tree transforms, opacity and bounded groves',()=>{
 const woodland=new THREE.Group(),terrain=new THREE.Group(),scene=new THREE.Scene();
 for(let s=0;s<3;s++)for(let l=0;l<2;l++){
  const root=new THREE.Group();root.name=`Woodland_${s}_${l}`;
  for(const kind of ['Branches','Leaves']){const m=new THREE.Mesh(new THREE.BoxGeometry(1,6,1),new THREE.MeshStandardMaterial());m.name=`${kind}_${s}_${l}`;root.add(m);}woodland.add(root);
 }
 const result=createLandscape(terrain,woodland,layout,scene);assert.equal(result.trees,620);
 assert.equal(result.batches.reduce((n,b)=>n+b.count,0),1240);
 const actual=[];for(const batch of result.batches){assert.ok(batch.boundingBox.getSize(new THREE.Vector3()).x<44);assert.ok(batch.frustumCulled);if(batch.name.endsWith('leaves')){assert.equal(batch.material.transparent,false);assert.equal(batch.material.depthWrite,true);assert.equal(batch.material.alphaTest,.42);}const mat=new THREE.Matrix4();for(let i=0;i<batch.count;i++){batch.getMatrixAt(i,mat);const p=new THREE.Vector3().setFromMatrixPosition(mat);actual.push(p);}}
 for(const [x,y,z] of layout.trees){assert.equal(actual.filter(p=>p.distanceTo(new THREE.Vector3(x,z,-y))<.0001).length,2);}
});
test('exported landscape assets include original vertex shading and compressed geometry',()=>{
 for(const name of ['terrain','woodland']){const bytes=fs.readFileSync(new URL(`../dist/assets/${name}.glb`,import.meta.url));assert.ok(bytes.length<12*1024*1024);const doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());assert.ok(doc.extensionsUsed.includes('KHR_draco_mesh_compression'));assert.ok(doc.meshes.some(m=>m.primitives.some(p=>p.attributes.COLOR_0!==undefined)));if(name==='woodland')assert.equal(doc.nodes.filter(n=>n.name?.startsWith('Woodland_')).length,6);}
});
test('groves share prototype buffers and materials without changing instances or shadow membership',()=>{
 const prior=fs.readFileSync(new URL('./landscape-before-sharing.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
 const oldCreate=new Function('THREE',prior+';return createLandscape')(THREE);
 const woodland=new THREE.Group();
 for(let s=0;s<3;s++)for(let l=0;l<2;l++){
  const root=new THREE.Group();root.name=`Woodland_${s}_${l}`;root.position.set(s,.1*l,0);
  for(const kind of ['Branches','Leaves']){const m=new THREE.Mesh(new THREE.BoxGeometry(1,6,1),new THREE.MeshStandardMaterial());m.name=`${kind}_${s}_${l}`;root.add(m);}woodland.add(root);
 }
 const old=oldCreate(new THREE.Group(),woodland,layout,new THREE.Scene()),now=createLandscape(new THREE.Group(),woodland,layout,new THREE.Scene());
 const key=b=>b.name+':'+Array.from(b.instanceMatrix.array).join(',');const expected=new Map(old.batches.map(b=>[key(b),b]));
 assert.equal(now.batches.length,old.batches.length);assert.equal(new Set(now.batches.map(b=>b.geometry)).size,12);assert.equal(new Set(now.batches.map(b=>b.material)).size,12);
 for(const b of now.batches){const ref=expected.get(key(b));assert.ok(ref);assert.equal(b.castShadow,ref.castShadow);assert.deepEqual(b.boundingBox,ref.boundingBox);assert.deepEqual(b.boundingSphere.center,ref.boundingSphere.center);assert.ok(b.boundingSphere.radius>=ref.boundingSphere.radius);if(b.name.endsWith('leaves')){assert.ok(b.customDepthMaterial&&b.customDistanceMaterial);assert.ok(b.userData.waterMotionPadding>0);}assert.deepEqual(b.geometry.index.array,ref.geometry.index.array);for(const [name,a]of Object.entries(b.geometry.attributes))assert.deepEqual(a.array,ref.geometry.attributes[name].array);assert.equal(b.material.roughness,ref.material.roughness);assert.equal(b.material.alphaTest,ref.material.alphaTest);}
 const leaf=now.batches.find(b=>b.name.endsWith('leaves')),shader={uniforms:{},vertexShader:'#include <begin_vertex>'};leaf.material.onBeforeCompile(shader);now.update(8);assert.equal(shader.uniforms.uWoodlandTime.value,8);
});

test('per-tree batches preserve immutable prototype buffers, transforms, wind bounds and shadow membership',()=>{
 const woodland=new THREE.Group();
 for(let s=0;s<3;s++)for(let l=0;l<2;l++){const root=new THREE.Group();root.name=`Woodland_${s}_${l}`;for(const kind of ['Branches','Leaves']){const m=new THREE.Mesh(new THREE.BoxGeometry(1,8,1),new THREE.MeshStandardMaterial());m.name=`${kind}_${s}_${l}`;root.add(m);}woodland.add(root);}
 const old=createLandscape(new THREE.Group(),woodland,layout,new THREE.Scene()),now=createLandscape(new THREE.Group(),woodland,layout,new THREE.Scene(),{perTreeCulling:true});
 assert.equal(now.perTreeCulling,true);assert.equal(now.batches.length,old.batches.length);assert.equal(new Set(now.batches.map(b=>b.geometry)).size,12);
 const matrix=new THREE.Matrix4(),expected=new THREE.Matrix4(),sphere=new THREE.Sphere(),box=new THREE.Box3();
 now.batches.forEach((batch,k)=>{
  const prior=old.batches[k];assert.ok(batch.isBatchedMesh);assert.equal(batch.instanceCount,prior.count);assert.equal(batch.castShadow,prior.castShadow);assert.equal(batch.sortObjects,false);assert.equal(batch.userData.noAO,true);
  for(let i=0;i<prior.count;i++){batch.getMatrixAt(i,matrix);prior.getMatrixAt(i,expected);assert.deepEqual(matrix.elements,expected.elements);}
  assert.deepEqual(batch.geometry.attributes.position.array,prior.geometry.attributes.position.array);assert.deepEqual(batch.geometry.index.array,prior.geometry.index.array);
  if(batch.name.endsWith('leaves')){prior.geometry.computeBoundingSphere();batch.getBoundingSphereAt(0,sphere);assert.ok(sphere.radius>=prior.geometry.boundingSphere.radius+.045);batch.getBoundingBoxAt(0,box);assert.ok(box.containsBox(prior.geometry.boundingBox));assert.ok(batch.customDepthMaterial&&batch.customDistanceMaterial);}
 });
});
