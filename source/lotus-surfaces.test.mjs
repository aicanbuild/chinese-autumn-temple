import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/lotus-surfaces.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const install=new Function('THREE',code+';return installLotusSurfaces;')(THREE);
test('lotus replacement preserves material and converts source to destination world frame',()=>{
 const root=new THREE.Group(),source=new THREE.Group();root.position.set(2,3,4);source.rotation.x=-Math.PI/2;
 for(const name of ['petals','leaves','pollen','stems']){
  const dst=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());dst.material.name=name;dst.position.set(1,0,2);root.add(dst);
  const src=new THREE.Mesh(new THREE.SphereGeometry(.2,12,8));src.position.set(-2,1,3);src.userData.sourceMaterial=name;source.add(src);
 }
 const original=root.children.map(o=>o.material);assert.equal(install(root,source),4);root.updateMatrixWorld(true);
 for(let i=0;i<4;i++){
  const dst=root.children[i],src=source.children[i];assert.equal(dst.material,original[i]);assert.notEqual(dst.geometry,src.geometry);
  for(let j=0;j<src.geometry.attributes.position.count;j++){
   const a=new THREE.Vector3().fromBufferAttribute(dst.geometry.attributes.position,j).applyMatrix4(dst.matrixWorld),b=new THREE.Vector3().fromBufferAttribute(src.geometry.attributes.position,j).applyMatrix4(src.matrixWorld);assert.ok(a.distanceTo(b)<1e-6);
  }
 }
});
test('actual lotus asset carries only four geometry batches with normals and UVs',()=>{
 const bytes=fs.readFileSync(new URL('../dist/assets/lotus-surfaces.glb',import.meta.url)),length=bytes.readUInt32LE(12),glb=JSON.parse(bytes.subarray(20,20+length));
 assert.equal(glb.meshes.length,4);assert.equal(glb.images?.length||0,0);assert.equal(glb.materials?.length||0,0);
 for(const mesh of glb.meshes){assert.equal(mesh.primitives.length,1);const p=mesh.primitives[0];assert.ok('NORMAL' in p.attributes);if(mesh.name.includes('living lotus'))assert.ok('TEXCOORD_0' in p.attributes);assert.ok(glb.accessors[p.attributes.POSITION].count>1000);}
 const tags=glb.nodes.filter(n=>n.mesh!==undefined).map(n=>n.extras.sourceMaterial).sort();assert.deepEqual(tags,['Sanctuary | botanical stems','Sanctuary | living lotus leaves','Sanctuary | living lotus petals','Sanctuary | lotus pollen and seed heart']);
});
