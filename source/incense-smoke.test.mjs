import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/incense-smoke.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const {createIncenseSmoke,SMOKE_LIFETIME}=new Function('THREE',code+';return {createIncenseSmoke,SMOKE_LIFETIME}')(THREE);
test('lighting begins at the physical tip and plume does not rotate with the camera',()=>{
 const root=new THREE.Group(),smoke=createIncenseSmoke(root,2.1),tip=new THREE.Vector3(.1,1.8,-6.6);
 smoke.update(10,false,tip);assert.equal(smoke.mesh.visible,false);
 smoke.update(11,true,tip);assert.equal(smoke.mesh.visible,true);assert.deepEqual(smoke.mesh.position,tip);assert.equal(smoke.mesh.material.uniforms.uStart.value,11);
 tip.y-=.1;smoke.update(15,true,tip);assert.deepEqual(smoke.mesh.position,tip);assert.equal(smoke.mesh.material.uniforms.uStart.value,11);
 assert.deepEqual(smoke.mesh.quaternion.toArray(),new THREE.Quaternion().toArray());smoke.mesh.geometry.computeBoundingBox();const size=smoke.mesh.geometry.boundingBox.getSize(new THREE.Vector3());assert.ok(size.x>.3&&size.z>.27&&size.y>1.39);
 assert.equal(smoke.mesh.material.side,THREE.BackSide);assert.equal(smoke.mesh.material.depthWrite,false);assert.equal(smoke.mesh.userData.noAO,true);
});
test('remaining smoke stays at the extinguished tip while replacement incense moves, then disappears',()=>{
 const root=new THREE.Group(),smoke=createIncenseSmoke(root),tip=new THREE.Vector3(0,2,-6.6);smoke.update(0,true,tip);smoke.update(180,false,tip);
 const stopped=smoke.mesh.position.clone();tip.y=2.7;
 smoke.update(182,false,tip);assert.equal(smoke.mesh.visible,true);assert.deepEqual(smoke.mesh.position,stopped);assert.equal(smoke.mesh.material.uniforms.uStop.value,180);
 smoke.update(180+SMOKE_LIFETIME+.001,false,tip);assert.equal(smoke.mesh.visible,false);
 smoke.update(190,true,tip);assert.equal(smoke.mesh.visible,true);assert.deepEqual(smoke.mesh.position,tip);assert.equal(smoke.mesh.material.uniforms.uStart.value,190);assert.ok(smoke.mesh.material.uniforms.uStop.value>190);
 smoke.dispose();assert.equal(root.children.length,0);
});
test('quick relighting preserves the detached plume at its original height',()=>{
 const root=new THREE.Group(),smoke=createIncenseSmoke(root),tip=new THREE.Vector3(0,1.6,-6.6);smoke.update(0,true,tip);smoke.update(180,false,tip);
 tip.y=2.04;smoke.update(183,true,tip);assert.equal(smoke.tail.visible,true);assert.equal(smoke.tail.position.y,1.6);assert.equal(smoke.mesh.position.y,2.04);assert.equal(smoke.tail.material.uniforms.uStop.value,180);assert.equal(smoke.mesh.material.uniforms.uStart.value,183);
 smoke.update(186,true,tip);assert.equal(smoke.tail.visible,false);assert.equal(smoke.mesh.visible,true);assert.equal(root.children.length,2);
 smoke.dispose();assert.equal(root.children.length,0);
});
