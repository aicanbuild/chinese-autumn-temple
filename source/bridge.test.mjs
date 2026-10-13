import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');const extraction=code.slice(code.indexOf('export function extractRegion'),code.indexOf('export function createRituals')).replace('export function','function');
const {extractRegion}=new Function('THREE',extraction+';return {extractRegion}')(THREE);
const bridge=fs.readFileSync(new URL('../dist/bridge.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {replaceBridge}=new Function('extractRegion',bridge+';return {replaceBridge}')(extractRegion);
test('bridge replacement removes only original timber/copper within the bridge footprint',()=>{
 const scene=new THREE.Scene(),model=new THREE.Group(),newBridge=new THREE.Group();
 function triangle(x,y,z){return [x-.03,y,z,x+.03,y,z,x,y+.03,z];}
 const mat=new THREE.MeshStandardMaterial();mat.name='Polished ebony cedar';const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([...triangle(0,1,6),...triangle(0,2,-6),...triangle(9,1,6)],3));g.setIndex([0,1,2,3,4,5,6,7,8]);model.add(new THREE.Mesh(g,mat));
 const stone=new THREE.Mesh(new THREE.BoxGeometry(2,.5,1),new THREE.MeshStandardMaterial());stone.position.set(0,.5,12.9);stone.material.name='Honed silver granite';model.add(stone);const count=stone.geometry.index.count;
 assert.equal(replaceBridge(model,newBridge,scene).removedTriangles,1);assert.deepEqual([...g.index.array],[0,1,2,3,4,5]);assert.equal(g.attributes.position.count,6);assert.equal(g.attributes.position.getY(0),2);assert.equal(stone.geometry.index.count,count);assert.equal(scene.children[0],newBridge);
});
test('finished bridge stays in four material batches with packed wood maps and restrained size',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/bridge.glb',import.meta.url));assert.ok(b.length<14*1024*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.meshes.length,4);assert.equal(d.materials.length,4);assert.ok(d.materials.some(m=>m.extensions?.KHR_materials_clearcoat));assert.ok(d.images.every(i=>i.bufferView!==undefined));assert.ok(d.extensionsUsed.includes('KHR_draco_mesh_compression'));
});
test('copper finish survives export with UVs, six embedded maps and physical roughness factors',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/bridge.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 for(const name of ['Bridge | satin gilded copper','Bridge | recessed bronze']){
  const i=d.materials.findIndex(m=>m.name===name),m=d.materials[i],p=m.pbrMetallicRoughness;
  assert.ok(m.normalTexture&&p.baseColorTexture&&p.metallicRoughnessTexture);assert.ok(p.roughnessFactor>0&&p.roughnessFactor<=1);assert.ok(p.baseColorFactor.every(c=>c>=0&&c<=1));
  for(const mesh of d.meshes)for(const primitive of mesh.primitives)if(primitive.material===i){assert.ok(primitive.attributes.TEXCOORD_0!==undefined);assert.ok(primitive.attributes.NORMAL!==undefined);}
 }
 assert.equal(d.images.length,6);assert.ok(d.images.every(i=>i.bufferView!==undefined));
 assert.ok(d.images.some(i=>i.name==='bridge-copper-normal'&&i.mimeType==='image/png'));
});
test('all four bridge batches embed their contact attribute with matching vertex counts',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/bridge.glb',import.meta.url)),n=b.readUInt32LE(12),d=JSON.parse(b.subarray(20,20+n));assert.ok(b.length<14*1024*1024);
 for(const mesh of d.meshes)for(const p of mesh.primitives){const a=d.accessors[p.attributes._BRIDGE_OCCLUSION],ext=p.extensions.KHR_draco_mesh_compression;assert.equal(a.count,d.accessors[p.attributes.POSITION].count);assert.equal(a.componentType,5126);assert.equal(a.type,'SCALAR');assert.ok(Number.isInteger(ext.attributes._BRIDGE_OCCLUSION));assert.ok(d.bufferViews[ext.bufferView].byteLength>0);}
});
