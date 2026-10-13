import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const rituals=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');const extraction=rituals.slice(rituals.indexOf('export function extractRegion'),rituals.indexOf('export function createRituals')).replace('export function','function');
const {extractRegion}=new Function('THREE',extraction+';return {extractRegion}')(THREE);
const source=fs.readFileSync(new URL('../dist/guardians.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {isOldGuardianFace,installGuardians}=new Function('extractRegion',source+';return {isOldGuardianFace,installGuardians}')(extractRegion);
const v=(x,y,z)=>new THREE.Vector3(x,y,z);
test('guardian replacement preserves pedestal and boundary-crossing architecture',()=>{
 assert.ok(isOldGuardianFace([v(3.6,.90,-2.25),v(3.7,1.3,-2.2),v(3.5,1.4,-2.5)]));
 assert.ok(isOldGuardianFace([v(-3.6,1,-2.25),v(-3.7,1.3,-2.2),v(-3.5,1.4,-2.5)]));
 assert.equal(isOldGuardianFace([v(3.5,.925,-2.2),v(3.7,.925,-2.2),v(3.5,.835,-2.4)]),false);
 assert.equal(isOldGuardianFace([v(3.5,1,-2.2),v(6,1,-2.2),v(3.5,1,-2.4)]),false);
 assert.equal(isOldGuardianFace([v(0,2,-8),v(.1,2,-8),v(0,3,-8)]),false);
});
test('invalid guardian asset cannot strip original statues',()=>{
 const model=new THREE.Group();assert.throws(()=>installGuardians(model,new THREE.Group(),new THREE.Scene()),/incomplete/);
});
test('portable guardians retain both detailed meshes and embedded stone textures with attribution',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/guardian-lions.glb',import.meta.url));assert.ok(b.length<7*1024*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.equal(d.meshes.length,2);assert.equal(d.materials.length,1);assert.equal(d.images.length,2);assert.ok(d.images.every(i=>i.bufferView!==undefined));
 for(const m of d.meshes){const p=m.primitives[0];assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);assert.ok(d.accessors[p.indices].count/3>100000);assert.ok(d.accessors[p.indices].count/3<150000);}
 const mat=d.materials[0].pbrMetallicRoughness;assert.equal(mat.metallicFactor,0);assert.ok(mat.baseColorTexture&&mat.metallicRoughnessTexture);
 const lions=d.nodes.filter(n=>n.extras?.guardian_scan);assert.equal(lions.length,2);assert.ok(lions.every(n=>n.extras.attribution.includes('vmccurley')&&n.extras.attribution.includes('CC BY 4.0')));
 const html=fs.readFileSync(new URL('../dist/credits.html',import.meta.url),'utf8');assert.ok(html.includes('https://zenodo.org/records/10335910')&&html.includes('https://creativecommons.org/licenses/by/4.0/'));
});
