import {applyFoliageLighting} from '../dist/foliage-lighting.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/understory.json',import.meta.url)));
const source=fs.readFileSync(new URL('../dist/understory.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installUnderstory}=new Function('applyFoliageLighting','THREE',source+';return {installUnderstory}')(applyFoliageLighting,THREE);
test('understory keeps its entire crown outside the navigable temple garden and axial approach',()=>{
 assert.equal(layout.shrubs.length,127);assert.equal(layout.variants,3);
 for(const [x,y,z,scale,rotation,variant] of layout.shrubs){assert.ok([x,y,z,scale,rotation].every(Number.isFinite));assert.ok(Math.hypot(x,y)-scale*layout.maximumPrototypeRadius>20);assert.ok(!(y<10&&Math.abs(x)<19));assert.ok(scale>=.7&&scale<=1.25);assert.ok(variant>=0&&variant<3);}
});
test('spatial shrub batches preserve every placement and use opaque geometry with bounds',()=>{
 const asset=new THREE.Group(),scene=new THREE.Scene();
 for(let i=0;i<3;i++){const root=new THREE.Group();root.name=`Understory_${i}`;for(const name of ['leaves','twigs']){const p=new THREE.Mesh(new THREE.BoxGeometry(2,1,2),new THREE.MeshStandardMaterial());p.name=`Understory_${name}_${i}`;root.add(p);}asset.add(root);}
 const result=installUnderstory(asset,layout,scene);assert.equal(result.shrubs,127);assert.equal(result.batches.reduce((s,b)=>s+b.count,0),254);
 const positions=[];for(const batch of result.batches){assert.equal(batch.material.transparent,false);assert.equal(batch.material.alphaTest,0);assert.ok(batch.frustumCulled&&batch.boundingBox&&batch.boundingSphere);const m=new THREE.Matrix4();for(let i=0;i<batch.count;i++){batch.getMatrixAt(i,m);positions.push(new THREE.Vector3().setFromMatrixPosition(m));}}
 for(const [x,y,z] of layout.shrubs)assert.equal(positions.filter(p=>p.distanceTo(new THREE.Vector3(x,z,-y))<.0001).length,2);
});
test('portable shrub asset contains real leaf silhouettes, pigment and packed leaf finishes',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/understory.glb',import.meta.url));assert.ok(b.length<3*1024*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.equal(d.meshes.length,6);assert.equal(d.images.length,2);assert.ok(d.images.every(i=>i.bufferView!==undefined));assert.ok(d.materials.every(m=>!m.alphaMode||m.alphaMode==='OPAQUE'));
 for(const m of d.meshes.filter(m=>m.name.includes('leaves'))){const p=m.primitives[0];assert.equal(d.accessors[p.indices].count,684*6*3);assert.ok(p.attributes.COLOR_0!==undefined&&p.attributes.TEXCOORD_0!==undefined);}
});
