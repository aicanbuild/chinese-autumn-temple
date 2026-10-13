import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {installRoofTiles} from '../dist/roof-tiles.js';
test('roof replacement removes only old ceramic and preserves other architecture',()=>{
 const model=new THREE.Group(),scene=new THREE.Scene(),asset=new THREE.Group();
 const old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());old.material.name='Charcoal glazed ceramic';model.add(old);
 const gold=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());gold.material.name='Satin gilded bronze';model.add(gold);
 const replacement=new THREE.Mesh(new THREE.SphereGeometry(1,48,24),new THREE.MeshPhysicalMaterial({clearcoat:.35,roughness:1}));asset.add(replacement);
 const r=installRoofTiles(model,asset,scene);assert.equal(r.removedTriangles,12);assert.equal(r.batches,1);assert.equal(gold.parent,model);assert.equal(old.parent,null);assert.equal(asset.parent,scene);assert.equal(replacement.material.clearcoat,.35);assert.equal(replacement.material.roughness,1);assert.equal(replacement.userData.waterSide,'above');
});
test('incomplete roof load leaves existing ceramic visible',()=>{
 const model=new THREE.Group(),old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());old.material.name='Charcoal glazed ceramic';model.add(old);
 assert.throws(()=>installRoofTiles(model,new THREE.Group(),new THREE.Scene()));assert.equal(old.parent,model);
});
test('portable roof retains smooth normals, UVs, kiln tint and embedded glaze maps in one batch',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/roof-tiles.glb',import.meta.url));assert.ok(b.length<3*1024*1024);
 const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.meshes.length,1);assert.equal(d.materials.length,1);assert.equal(d.images.length,3);assert.ok(d.images.every(i=>i.bufferView!==undefined));
 const p=d.meshes[0].primitives[0];for(const key of ['NORMAL','TEXCOORD_0','COLOR_0'])assert.ok(p.attributes[key]!==undefined,key);
 assert.ok(d.accessors[p.attributes.POSITION].count<430000,'UV/color layout should retain shared surface vertices');
 const m=d.materials[0];assert.ok(m.normalTexture&&m.pbrMetallicRoughness.metallicRoughnessTexture&&m.extensions.KHR_materials_clearcoat);
 assert.equal(m.pbrMetallicRoughness.roughnessFactor??1,1,'authored roughness must not be multiplied down');
 const r=JSON.parse(fs.readFileSync(new URL('../dist/assets/roof-tiles.json',import.meta.url)));assert.equal(r.tiles,2864);assert.equal(r.preservedNonRoofFaces,1304);assert.equal(r.thicknessMeters,.008);
});
