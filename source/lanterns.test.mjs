import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const rituals=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');const extraction=rituals.slice(rituals.indexOf('export function extractRegion'),rituals.indexOf('export function createRituals')).replace('export function','function');
const {extractRegion}=new Function('THREE',extraction+';return {extractRegion}')(THREE);
const source=fs.readFileSync(new URL('../dist/lanterns.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installLanterns}=new Function('THREE','extractRegion',source+';return {installLanterns}')(THREE,extractRegion);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/stone-lantern.json',import.meta.url)));
test('lantern removal preserves paving even when a large face centroid lies inside the fixture',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene(),prototype=new THREE.Group(),g=new THREE.BufferGeometry();
 // A small fixture triangle, a large paving face, and a fixture outside the target volume.
 g.setAttribute('position',new THREE.Float32BufferAttribute([-.1,.3,0,.1,.3,0,0,.4,.1,-2,.2,-1,2,.2,-1,0,.2,2,4,.3,0,4.1,.3,0,4,.4,.1],3));g.setIndex([0,1,2,3,4,5,6,7,8]);
 const mat=new THREE.MeshStandardMaterial();mat.name='Honed silver granite';root.add(new THREE.Mesh(g,mat));
 installLanterns(root,prototype,{placements:[[0,0,.18,1]]},scene);assert.deepEqual([...g.index.array],[0,1,2,3,4,5]);assert.equal(g.attributes.position.getX(0),-2);
});
test('sixteen lamps share four batches with original locations and scale',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene(),prototype=new THREE.Group();
 for(let i=0;i<4;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());m.position.set(0,1,0);prototype.add(m);}
 const result=installLanterns(root,prototype,layout,scene);assert.equal(result.count,16);assert.equal(result.meshes.length,4);
 for(const mesh of result.meshes){assert.equal(mesh.count,16);for(let i=0;i<16;i++){const [x,y,z,s]=layout.placements[i],m=new THREE.Matrix4(),p=new THREE.Vector3(),q=new THREE.Quaternion(),scale=new THREE.Vector3();mesh.getMatrixAt(i,m);m.decompose(p,q,scale);assert.ok(p.distanceTo(new THREE.Vector3(x,z,-y))<.00001);assert.ok(scale.distanceTo(new THREE.Vector3(s,s,s))<.00001);}assert.ok(mesh.boundingBox);}
});
test('lantern export retains four materials, normals, UVs and packed granite maps',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/stone-lantern.glb',import.meta.url));assert.ok(b.length<2*1024*1024);const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.meshes.length,4);assert.equal(d.materials.length,4);assert.ok(d.images.every(i=>i.bufferView!==undefined));for(const m of d.meshes)for(const p of m.primitives){assert.ok(p.attributes.NORMAL!==undefined);assert.ok(p.attributes.TEXCOORD_0!==undefined);assert.ok(p.attributes._LANTERN_OCCLUSION!==undefined);}
});
test('multi-draw lamps preserve prototype geometry and placement while culling each camera independently',()=>{
 const prototype=new THREE.Group(),geometry=new THREE.SphereGeometry(.4,16,12),material=new THREE.MeshStandardMaterial();prototype.add(new THREE.Mesh(geometry,material));
 const placements={placements:[[0,0,.18,1],[30,0,.18,.8],[-30,0,.18,.8]]};
 const result=installLanterns(new THREE.Group(),prototype,placements,new THREE.Scene(),{perLampCulling:true}),batch=result.meshes[0];
 assert.equal(batch.isBatchedMesh,true);assert.equal(batch.instanceCount,3);assert.equal(batch.material,material);assert.equal(batch.userData.noAO,true);assert.equal(batch.userData.waterSide,'above');
 const baseline=installLanterns(new THREE.Group(),prototype,placements,new THREE.Scene()).meshes[0].geometry;
 assert.deepEqual([...batch.geometry.attributes.position.array],[...baseline.attributes.position.array]);assert.deepEqual([...batch.geometry.attributes.normal.array],[...baseline.attributes.normal.array]);assert.deepEqual([...batch.geometry.index.array],[...baseline.index.array]);
 for(let i=0;i<3;i++){const m=new THREE.Matrix4(),[x,y,z,s]=placements.placements[i];batch.getMatrixAt(i,m);assert.ok(new THREE.Vector3().setFromMatrixPosition(m).distanceTo(new THREE.Vector3(x,z,-y))<1e-6);assert.ok(Math.abs(m.elements[0]-s)<1e-6);}
 const camera=new THREE.PerspectiveCamera(35,1,.1,15);camera.position.set(0,.2,4);camera.lookAt(0,.2,0);camera.updateMatrixWorld();batch.updateMatrixWorld();
 batch.onBeforeRender({},null,camera,batch.geometry,batch.material);assert.equal(batch._multiDrawCount,1);
 const shadow=new THREE.OrthographicCamera(-40,40,2,-2,.1,15);shadow.position.set(0,.2,4);shadow.lookAt(0,.2,0);shadow.updateMatrixWorld();
 batch.onBeforeShadow({},batch,camera,shadow,batch.geometry,new THREE.MeshDepthMaterial());assert.equal(batch._multiDrawCount,3);
 batch.onBeforeRender({},null,camera,batch.geometry,batch.material);assert.equal(batch._multiDrawCount,1);assert.equal(batch.instanceCount,3);
 batch.dispose();
});
