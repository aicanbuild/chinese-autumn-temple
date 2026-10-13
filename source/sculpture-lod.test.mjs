import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/sculpture-lod.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const {createSculptureLOD}=new Function('THREE',code+';return {createSculptureLOD}')(THREE);
test('distant sculpture is smaller while preserving its world placement and silhouette extent',()=>{
 function asset(name){const b=fs.readFileSync(new URL(`../dist/assets/${name}.glb`,import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));const box=new THREE.Box3();let triangles=0;
  const visit=(i,parent)=>{const n=d.nodes[i],local=new THREE.Matrix4();if(n.matrix)local.fromArray(n.matrix);else local.compose(new THREE.Vector3(...(n.translation||[0,0,0])),new THREE.Quaternion(...(n.rotation||[0,0,0,1])),new THREE.Vector3(...(n.scale||[1,1,1])));const world=parent.clone().multiply(local);if(n.mesh!==undefined)for(const p of d.meshes[n.mesh].primitives){const a=d.accessors[p.attributes.POSITION];box.union(new THREE.Box3(new THREE.Vector3(...a.min),new THREE.Vector3(...a.max)).applyMatrix4(world));triangles+=d.accessors[p.indices].count/3;}for(const c of n.children||[])visit(c,world);};for(const n of d.scenes[d.scene||0].nodes)visit(n,new THREE.Matrix4());return {box,triangles,materials:d.materials.length};}
 const high=asset('sculpture'),low=asset('sculpture-distant');assert.equal(low.materials,high.materials);assert.ok(low.triangles<high.triangles*.16);assert.ok(low.box.min.distanceTo(high.box.min)<.015);assert.ok(low.box.max.distanceTo(high.box.max)<.015);
});
test('close view uses full sculpture, distant view uses LOD, and transforms survive both',()=>{
 const high=new THREE.Group(),low=new THREE.Group(),camera=new THREE.PerspectiveCamera(43,1);
 for(const root of [high,low]){const m=new THREE.Mesh(new THREE.BoxGeometry(1,1.9,1),new THREE.MeshStandardMaterial());m.position.set(0,2.85,-8.6);root.add(m);}
 const lod=createSculptureLOD(high,low,camera,748);lod.updateMatrixWorld(true);
 const before=high.children[0].getWorldPosition(new THREE.Vector3());assert.ok(before.distanceTo(new THREE.Vector3(0,2.85,-8.6))<1e-8);
 camera.position.set(0,3,-2.9);camera.updateMatrixWorld();lod.update(camera);assert.ok(high.visible&&!low.visible);
 camera.position.set(20,12,37);camera.updateMatrixWorld();lod.update(camera);assert.ok(low.visible&&!high.visible);
 const threshold=lod.levels[1].distance;lod.resize(1496);assert.ok(Math.abs(lod.levels[1].distance-threshold*2)<1e-8);
});
