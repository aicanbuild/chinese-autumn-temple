import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
test('the altar sculpture is a compact restored scan with valid world-space placement',()=>{
 const bytes=fs.readFileSync(new URL('../dist/assets/sculpture.glb',import.meta.url));
 assert.equal(bytes.toString('utf8',0,4),'glTF');assert.ok(bytes.length<4*1024*1024);
 const doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
 assert.ok(doc.materials.length>=1&&doc.materials.length<=4);assert.ok(doc.meshes.length>=1&&doc.meshes.length<=4);assert.ok(doc.extensionsUsed.includes('KHR_draco_mesh_compression'));
 const bounds=new THREE.Box3();let triangles=0;
 function visit(i,parent){const n=doc.nodes[i],local=new THREE.Matrix4();if(n.matrix)local.fromArray(n.matrix);else local.compose(new THREE.Vector3().fromArray(n.translation||[0,0,0]),new THREE.Quaternion().fromArray(n.rotation||[0,0,0,1]),new THREE.Vector3().fromArray(n.scale||[1,1,1]));const world=new THREE.Matrix4().multiplyMatrices(parent,local);
  if(n.mesh!==undefined)for(const p of doc.meshes[n.mesh].primitives){const a=doc.accessors[p.attributes.POSITION];bounds.union(new THREE.Box3(new THREE.Vector3(...a.min),new THREE.Vector3(...a.max)).applyMatrix4(world));triangles+=doc.accessors[p.indices].count/3;}
  for(const c of n.children||[])visit(c,world);
 }
 for(const i of doc.scenes[doc.scene||0].nodes)visit(i,new THREE.Matrix4());
 assert.ok(triangles>150000);assert.ok(bounds.min.y>=1.89&&bounds.max.y<3.95);
 assert.ok(bounds.min.x>-.85&&bounds.max.x<.85);assert.ok(bounds.min.z>-9.15&&bounds.max.z<-8.0);
});
