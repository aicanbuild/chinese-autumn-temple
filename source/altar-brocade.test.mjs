import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';import {installAltarBrocade} from '../dist/altar-brocade.js';
const b=fs.readFileSync(new URL('../dist/assets/altar-brocade.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
test('real cloth export retains woven gold mask, thread normal and independent lining',()=>{
 assert.ok(b.length<2*1024*1024);assert.equal(d.meshes.length,1);assert.equal(d.meshes[0].primitives.length,2);assert.equal(d.images.length,3);
 const fabric=d.materials.find(m=>m.name.includes('gilt thread')),lining=d.materials.find(m=>m.name.includes('lining'));
 assert.ok(fabric.pbrMetallicRoughness.metallicRoughnessTexture);assert.ok(fabric.normalTexture);assert.equal(lining.pbrMetallicRoughness.metallicFactor,0);
 let triangles=0;for(const p of d.meshes[0].primitives){assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);triangles+=d.accessors[p.indices].count/3;}
 assert.ok(triangles<55000&&triangles>20000);
});
test('runner installation preserves authored masks, geometry and positions with restrained silk sheen',()=>{
 const scene=new THREE.Scene(),asset=new THREE.Group(),material=new THREE.MeshPhysicalMaterial({sheen:1,roughness:.5,metalness:1});material.map=new THREE.Texture();material.metalnessMap=new THREE.Texture();material.roughnessMap=material.metalnessMap;material.normalMap=new THREE.Texture();
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(),material);mesh.position.set(-2.16,1.7,-7.68);asset.add(mesh);const geometry=mesh.geometry,map=material.metalnessMap;
 const result=installAltarBrocade(asset,scene);assert.equal(result.meshes,1);assert.equal(mesh.geometry,geometry);assert.equal(mesh.material.metalnessMap,map);assert.deepEqual(mesh.position.toArray(),[-2.16,1.7,-7.68]);assert.equal(material.sheen,.16);assert.equal(material.metalness,1);assert.equal(mesh.castShadow,true);assert.equal(mesh.receiveShadow,true);assert.equal(mesh.userData.waterSide,'above');assert.equal(material.map.anisotropy,8);
});
