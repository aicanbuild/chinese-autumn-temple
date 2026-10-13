import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/sanctuary-detail.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const create=new Function('THREE',code+';return createSanctuaryDetail;')(THREE);
function setup(){
 const root=new THREE.Group(),far=new THREE.Group();root.position.set(0,0,-2);
 for(let i=0;i<3;i++){
  const m=new THREE.MeshStandardMaterial({color:0xa87c33});m.name='m'+i;
  const full=new THREE.Mesh(new THREE.SphereGeometry(.5,32,24),m);full.position.set(i-1,0,0);full.castShadow=full.receiveShadow=true;root.add(full);
  const distant=new THREE.Mesh(new THREE.SphereGeometry(.5,12,8));distant.position.set(i-1,0,-2);distant.userData.sourceMaterial=m.name;far.add(distant);
 }
 const controller=create(root,far),camera=new THREE.PerspectiveCamera(43,16/9,.1,200);camera.position.set(0,0,30);camera.lookAt(0,0,-2);camera.updateMatrixWorld();
 return {root,far,controller,camera};
}
test('distant carving retains material, transform, shadow flags and geometry world location',()=>{
 const {root,controller,camera}=setup(),originals=root.children.map(o=>({m:o.material,g:o.geometry,matrix:o.matrixWorld.clone()}));
 controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);assert.ok(controller.stats.savedTriangles>0);
 root.children.forEach((o,i)=>{assert.equal(o.material,originals[i].m);assert.ok(o.castShadow&&o.receiveShadow);assert.deepEqual(o.matrixWorld,originals[i].matrix);assert.notEqual(o.geometry,originals[i].g);assert.ok(o.geometry.boundingBox.getCenter(new THREE.Vector3()).length()<1e-6);});
 controller.update(camera,720,true);assert.equal(controller.stats.distantMeshes,0);root.children.forEach((o,i)=>assert.equal(o.geometry,originals[i].g));
});
test('close approach, higher render resolution and field of view restore full geometry',()=>{
 const {controller,camera}=setup();controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 controller.update(camera,2880);assert.equal(controller.stats.distantMeshes,0);
 controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 camera.position.z=4;controller.update(camera,720);assert.equal(controller.stats.distantMeshes,0);
 camera.position.z=30;controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 camera.fov=10;camera.updateProjectionMatrix();controller.update(camera,720);assert.equal(controller.stats.distantMeshes,0);
});
test('camera crossing a component keeps full geometry and partial assets are rejected',()=>{
 const {controller,camera}=setup();camera.position.set(0,0,-2);controller.update(camera,720);assert.equal(controller.stats.distantMeshes,0);
 assert.throws(()=>create(new THREE.Group(),new THREE.Group()),/Missing sanctuary/);
});
test('a hysteresis band prevents geometry flicker during small camera movements',()=>{
 const {controller,camera}=setup();controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 camera.position.z=11;controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 controller.update(camera,720,true);controller.update(camera,720);assert.equal(controller.stats.distantMeshes,0);
 camera.position.z=13;controller.update(camera,720);assert.equal(controller.stats.distantMeshes,3);
 camera.position.z=8;controller.update(camera,720);assert.equal(controller.stats.distantMeshes,0);
});
test('export carries only replacement geometry, with unchanged source and bounded sampled errors',()=>{
 const path=new URL('../dist/assets/sanctuary-distant.glb',import.meta.url),b=fs.readFileSync(path),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const report=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary-distant.json',import.meta.url)));
 assert.equal(d.meshes.length,3);assert.equal((d.images??[]).length,0);assert.equal((d.materials??[]).length,0);assert.equal(d.nodes.filter(n=>n.extras?.sourceMaterial).length,3);
 assert.ok(report.sourceUnchanged);assert.ok(report.maximumSampledError<=.003);assert.ok(report.reducedParts>100);assert.ok(b.length<2000000);
 assert.ok(Object.values(report.materials).reduce((s,m)=>s+m.triangles,0)<834700*.85);
 for(const m of d.meshes)for(const p of m.primitives)assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);
 const fullBytes=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url)),fullDoc=JSON.parse(fullBytes.subarray(20,20+fullBytes.readUInt32LE(12)));
 function worldBounds(doc){
  const boxes=new Map();
  function visit(id,parent=new THREE.Matrix4()){
   const n=doc.nodes[id],m=new THREE.Matrix4();
   if(n.matrix)m.fromArray(n.matrix);else m.compose(new THREE.Vector3().fromArray(n.translation??[0,0,0]),new THREE.Quaternion().fromArray(n.rotation??[0,0,0,1]),new THREE.Vector3().fromArray(n.scale??[1,1,1]));m.premultiply(parent);
   if(n.mesh!==undefined)for(const p of doc.meshes[n.mesh].primitives){const a=doc.accessors[p.attributes.POSITION],name=n.extras?.sourceMaterial??doc.materials[p.material].name;const b=new THREE.Box3(new THREE.Vector3().fromArray(a.min),new THREE.Vector3().fromArray(a.max)).applyMatrix4(m);if(boxes.has(name))boxes.get(name).union(b);else boxes.set(name,b);}
   for(const c of n.children??[])visit(c,m);
  }
  for(const n of doc.scenes[doc.scene??0].nodes)visit(n);return boxes;
 }
 const original=worldBounds(fullDoc);
 for(const [name,box]of worldBounds(d)){const other=original.get(name);assert.ok(other,name);assert.ok(box.min.distanceTo(other.min)<.006,name+' minimum');assert.ok(box.max.distanceTo(other.max)<.006,name+' maximum');}
});
