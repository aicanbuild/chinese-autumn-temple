import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const regionSource=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extractRegion=new Function('THREE',regionSource.slice(regionSource.indexOf('export function extractRegion'),regionSource.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(T);
const installSource=fs.readFileSync(new URL('../dist/aureole-relief.js',import.meta.url),'utf8');
const installAureoleRelief=new Function('extractRegion',installSource.slice(installSource.indexOf('export function')).replace('export ','')+';return installAureoleRelief;')(extractRegion);
test('native mandorla export is two geometry batches with complete normals and UVs',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/aureole-relief.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.ok(b.length<512*1024);assert.equal(d.meshes.length,2);assert.equal((d.materials??[]).length,0);assert.equal((d.images??[]).length,0);
 assert.deepEqual(new Set(d.nodes.filter(n=>n.mesh!==undefined).map(n=>n.extras.sourceMaterial)),new Set(['Sanctuary | hand burnished gold','Sanctuary | antique gilt bronze']));
 let triangles=0;for(const m of d.meshes)for(const p of m.primitives){triangles+=d.accessors[p.indices].count/3;assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);}
 assert.equal(triangles,117888);
});
test('mandorla replacement preserves unrelated bronze faces, original gold and finished materials',()=>{
 const scene=new T.Scene(),root=new T.Group(),asset=new T.Group();
 const gold=new T.MeshPhysicalMaterial({clearcoat:.3}),bronze=new T.MeshStandardMaterial();gold.name='Sanctuary | hand burnished gold';bronze.name='Sanctuary | antique gilt bronze';
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute([0,3,-9.19,.01,3,-9.19,0,3.01,-9.19, 2,3,-9.19,2.01,3,-9.19,2,3.01,-9.19, 0,3,-9.19,.01,3,-9.19,0,3,-9.17],3));g.computeVertexNormals();
 const old=new T.Mesh(g,bronze),originalGold=new T.Mesh(new T.BoxGeometry(),gold);root.add(old,originalGold);const preservedGold=originalGold.geometry;
 for(const m of [gold,bronze]){const mesh=new T.Mesh(new T.BoxGeometry());mesh.userData.sourceMaterial=m.name;asset.add(mesh);}
 const report=installAureoleRelief(asset,root,scene);assert.equal(report.removedTriangles,1);assert.equal(old.geometry.index.count,6);assert.equal(originalGold.geometry,preservedGold);
 assert.equal(asset.children[0].material,gold);assert.equal(asset.children[1].material,bronze);assert.equal(gold.clearcoat,.3);assert.equal(asset.children[0].castShadow,true);assert.equal(asset.children[1].receiveShadow,true);
 const pos=old.geometry.attributes.position;assert.equal(pos.count,6);assert.ok(Array.from(pos.array).includes(2));assert.ok(Array.from(pos.array).some(x=>Math.abs(x+9.17)<1e-5));
});
