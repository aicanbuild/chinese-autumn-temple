import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const ritual=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extractRegion=new Function('THREE',ritual.slice(ritual.indexOf('export function extractRegion'),ritual.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(THREE);
const source=fs.readFileSync(new URL('../dist/incense-vessel.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const install=new Function('extractRegion',source+';return installIncenseVessel;')(extractRegion);
test('replacing the incense vessel preserves altar gold and any boundary-crossing triangle',()=>{
 const model=new THREE.Group(),scene=new THREE.Scene(),asset=new THREE.Group();
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.Float32BufferAttribute([-.2,1.3,-6.6,.2,1.3,-6.6,0,1.6,-6.6, -.5,1.2,-6.6,.7,1.2,-6.6,0,1.5,-6.6, -1,1.8,-8.6,1,1.8,-8.6,0,2,-8.6],3));g.setIndex([0,1,2,3,4,5,6,7,8]);
 const m=new THREE.MeshStandardMaterial();m.name='Satin gilded bronze';model.add(new THREE.Mesh(g,m));
 const result=install(model,asset,scene);assert.equal(result.removedTriangles,1);assert.equal(g.index.count,6);assert.equal(g.attributes.position.count,6);assert.equal(g.attributes.position.getX(1),Math.fround(.7));assert.ok(g.boundingBox.min.z<-8.5);assert.equal(scene.children[0],asset);
});
test('portable incense vessel has packed finishes and stays within its physical footprint',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/incense-vessel.glb',import.meta.url));assert.ok(b.length<6*1024*1024);
 const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.equal(d.materials.length,4);assert.equal(d.meshes.length,4);assert.ok(d.images.length>=6&&d.images.every(i=>i.bufferView!==undefined));
 const bounds=new THREE.Box3();let triangles=0;
 function visit(i,parent){const n=d.nodes[i],local=new THREE.Matrix4();if(n.matrix)local.fromArray(n.matrix);else local.compose(new THREE.Vector3(...(n.translation||[0,0,0])),new THREE.Quaternion(...(n.rotation||[0,0,0,1])),new THREE.Vector3(...(n.scale||[1,1,1])));const world=parent.clone().multiply(local);
 if(n.mesh!==undefined)for(const p of d.meshes[n.mesh].primitives){const a=d.accessors[p.attributes.POSITION];bounds.union(new THREE.Box3(new THREE.Vector3(...a.min),new THREE.Vector3(...a.max)).applyMatrix4(world));triangles+=d.accessors[p.indices].count/3;}
 for(const child of n.children||[])visit(child,world);}
 for(const n of d.scenes[d.scene||0].nodes)visit(n,new THREE.Matrix4());
 assert.ok(bounds.min.y>1.09&&bounds.max.y<1.71);assert.ok(bounds.min.x>-.56&&bounds.max.x<.56);assert.ok(bounds.min.z>-7&&bounds.max.z<-6.2);assert.ok(triangles>50000&&triangles<250000);
});
