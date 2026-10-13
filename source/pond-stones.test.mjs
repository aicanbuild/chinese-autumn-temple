import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const rituals=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');const extraction=rituals.slice(rituals.indexOf('export function extractRegion'),rituals.indexOf('export function createRituals')).replace('export function','function');
const {extractRegion}=new Function('THREE',extraction+';return {extractRegion}')(THREE);
const source=fs.readFileSync(new URL('../dist/pond-stones.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installPondStones}=new Function('THREE','extractRegion',source+';return {installPondStones}')(THREE,extractRegion);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/pond-stones.json',import.meta.url)));
test('pond stones share eight batches and preserve nonuniform native placement',()=>{
 const model=new THREE.Group(),prototypes=new THREE.Group(),scene=new THREE.Scene();const mat=new THREE.MeshStandardMaterial();mat.name='Natural mossy bank stones';const old=new THREE.Mesh(new THREE.BoxGeometry(.1,.1,.1),mat);old.position.set(0,-.8,6);model.add(old);
 for(let k=0;k<8;k++){const m=new THREE.Mesh(new THREE.IcosahedronGeometry(1,1),new THREE.MeshStandardMaterial());m.name=`PondStone_${k}`;prototypes.add(m);}
 const result=installPondStones(model,prototypes,layout,scene);assert.equal(result.count,617);assert.equal(result.meshes.length,8);assert.equal(new Set(result.meshes.map(m=>m.material)).size,1);assert.equal(old.geometry.index.count,0);
 for(let kind=0;kind<8;kind++){
  const mesh=result.meshes[kind],placements=layout.placements.filter(p=>p[0]===kind);assert.equal(mesh.count,placements.length);assert.equal(mesh.material.vertexColors,true);assert.equal(mesh.castShadow,true,'submerged stones must also occlude sunlight');assert.equal(mesh.receiveShadow,true);
  const expected=placements.map(([id,x,y,z,sx,sy,sz,angle])=>{const o=new THREE.Object3D();o.position.set(x,z,-y);o.scale.set(sx,sz,sy);o.rotation.y=angle;o.updateMatrix();return o.matrix;});
  for(let i=0;i<mesh.count;i++){
   const matrix=new THREE.Matrix4();mesh.getMatrixAt(i,matrix);
   const match=expected.findIndex(m=>m.elements.every((v,k)=>Math.abs(v-matrix.elements[k])<.00001));assert.ok(match>=0,'every original transform appears exactly once');expected.splice(match,1);
   const bounds=mesh.geometry.boundingBox.clone().applyMatrix4(matrix);
   if(i>=mesh.userData.waterReflectionCount)assert.ok(bounds.max.y<-.030,'only wholly submerged instances leave reflections');
   else assert.ok(bounds.max.y>=-.030);
  }
  assert.equal(expected.length,0);
  if(kind>=6){assert.equal(mesh.userData.waterSide,'below');assert.ok(mesh.boundingBox.max.y<-.70);}
 }
});
test('bank stones leave the bridge entrances open and stay outside swimming routes',()=>{
 for(const [kind,x,y,z,sx,sy,sz,angle,zone] of layout.placements){assert.ok([x,y,z,sx,sy,sz,angle].every(Number.isFinite));assert.ok(sx>0&&sy>0&&sz>0);if(zone==='bank'){assert.ok(Math.abs(x)>1.75);assert.ok((x/11.5)**2+((y+5.8)/6.9)**2>.98);}if(zone==='bed')assert.ok(z+sz<-.70);}
});
test('portable stone geometry has normals and vertex variation without duplicated texture payloads',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/pond-stones.glb',import.meta.url));assert.ok(b.length<512*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.meshes.length,8);assert.equal(d.images?.length??0,0);for(const m of d.meshes)for(const p of m.primitives){assert.ok(p.attributes.NORMAL!==undefined);assert.ok(p.attributes.COLOR_0!==undefined);assert.ok(d.accessors[p.indices].count>=240);}
});
