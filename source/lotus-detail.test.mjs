import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/sanctuary-detail.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');const create=new Function('THREE',code+';return createSanctuaryDetail;')(THREE);
test('two-surface optical LOD keeps materials and recovers original attributes up close or inside',()=>{
 const root=new THREE.Group(),far=new THREE.Group();
 for(let i=0;i<2;i++){const material=new THREE.MeshStandardMaterial();material.name='lotus'+i;const full=new THREE.Mesh(new THREE.SphereGeometry(.5,24,16),material),low=new THREE.Mesh(new THREE.SphereGeometry(.5,8,6));full.geometry.setAttribute('_lotus_transmittance',new THREE.BufferAttribute(new Float32Array(full.geometry.attributes.position.count).fill(.3),1));low.geometry.setAttribute('_lotus_transmittance',new THREE.BufferAttribute(new Float32Array(low.geometry.attributes.position.count).fill(.3),1));low.userData.sourceMaterial=material.name;root.add(full);far.add(low);}
 const original=root.children.map(o=>o.geometry),materials=root.children.map(o=>o.material),detail=create(root,far,{expectedMeshes:2,errorBudget:.0015,pixelLimit:.5}),camera=new THREE.PerspectiveCamera(43,16/9,.1,100);camera.position.z=26;camera.lookAt(0,0,0);camera.updateMatrixWorld();
 detail.update(camera,1080);assert.equal(detail.stats.distantMeshes,2);assert.ok(detail.stats.savedTriangles>0);root.children.forEach((o,i)=>{assert.equal(o.material,materials[i]);assert.ok(o.geometry.attributes._lotus_transmittance);});
 camera.position.z=1;camera.updateMatrixWorld();detail.update(camera,1080);assert.equal(detail.stats.fullMeshes,2);root.children.forEach((o,i)=>assert.equal(o.geometry,original[i]));
 camera.position.z=26;camera.updateMatrixWorld();detail.update(camera,1080);detail.update(camera,1080,true);assert.equal(detail.stats.fullMeshes,2);assert.equal(detail.stats.savedTriangles,0);
});
test('distant geometry keeps optical attributes and measured error below its conservative runtime budget',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/lotus-distant.glb',import.meta.url)),j=JSON.parse(b.subarray(20,20+b.readUInt32LE(12))),r=JSON.parse(fs.readFileSync(new URL('../dist/assets/lotus-distant.json',import.meta.url)));
 assert.equal(j.meshes.length,2);assert.equal(j.materials?.length||0,0);assert.equal(j.images?.length||0,0);assert.ok(r.sourceUnchanged);assert.ok(r.maximumSampledError<=.00075);assert.equal(r.runtimeErrorBudget,.0015);assert.equal(r.reducedParts+r.retainedParts,130);assert.ok(r.reducedParts>=100);
 let total=0;for(const m of j.meshes)for(const p of m.primitives){total+=j.accessors[p.indices].count/3;for(const key of ['NORMAL','TEXCOORD_0','_LOTUS_TRANSMITTANCE','_LOTUS_THICKNESS'])assert.ok(key in p.attributes);}
 assert.equal(total,Object.values(r.materials).reduce((sum,m)=>sum+m.triangles,0));assert.ok(total<r.fullTriangles*.3);assert.ok(b.length<400000);
});
