import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const rituals=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');const extraction=rituals.slice(rituals.indexOf('export function extractRegion'),rituals.indexOf('export function createRituals')).replace('export function','function');
const {extractRegion}=new Function('THREE',extraction+';return {extractRegion}')(THREE);
const source=fs.readFileSync(new URL('../dist/sanctuary-floor.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installSanctuaryFloor}=new Function('extractRegion',source+';return {installSanctuaryFloor}')(extractRegion);
test('stone floor replacement preserves nearby furniture and boundary-crossing cedar',()=>{
 const root=new THREE.Group(),asset=new THREE.Group(),scene=new THREE.Scene(),g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.Float32BufferAttribute([-.2,1.07,-3.475,.2,1.07,-3.475,0,1.07,-10.725,-.2,1.005,-7.925,.2,1.005,-7.925,0,1.005,-9.375,-9,1.07,-3.475,9,1.07,-3.475,0,1.07,-10.725],3));g.setIndex([0,1,2,3,4,5,6,7,8]);const m=new THREE.MeshStandardMaterial();m.name='Polished ebony cedar';root.add(new THREE.Mesh(g,m));
 for(let i=0;i<3;i++)asset.add(new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial()));
 const r=installSanctuaryFloor(root,asset,scene);assert.equal(r.removedTriangles,1);assert.equal(g.index.count,6);assert.ok(Math.abs(g.attributes.position.getY(0)-1.005)<.00001);assert.equal(g.attributes.position.getX(3),-9);assert.ok(asset.children.every(o=>o.castShadow&&o.receiveShadow&&o.userData.waterSide==='above'));
});
test('incomplete paving asset cannot erase the original floor',()=>{
 assert.throws(()=>installSanctuaryFloor(new THREE.Group(),new THREE.Group(),new THREE.Scene()),/incomplete/);
});
test('portable paving has physical slab geometry, neutral variation and three embedded surface maps',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary-floor.glb',import.meta.url));assert.ok(b.length<5*1024*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.meshes.length,3);assert.equal(d.materials.length,3);assert.equal(d.images.length,3);assert.ok(d.images.every(i=>i.bufferView!==undefined));
 for(const m of d.materials.filter(m=>!m.name.includes('joint'))){assert.equal(m.pbrMetallicRoughness.metallicFactor,0);assert.ok(m.pbrMetallicRoughness.baseColorTexture&&m.pbrMetallicRoughness.metallicRoughnessTexture&&m.normalTexture);assert.equal(m.pbrMetallicRoughness.roughnessFactor??1,1);}
 const r=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary-floor.json',import.meta.url)));assert.equal(r.fieldSlabs,112);assert.equal(r.borderSlabs,44);assert.equal(r.parts,157);assert.equal(r.topMeters,1.07);assert.equal(r.jointMeters,.004);assert.ok(r.jointBedMeters<r.topMeters);
 let tris=0;for(const mesh of d.meshes)for(const p of mesh.primitives){tris+=d.accessors[p.indices].count/3;assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);}
 assert.ok(tris>10000&&tris<40000);
});
