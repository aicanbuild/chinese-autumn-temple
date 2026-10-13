import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/camera-safety.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const hallSource=fs.readFileSync(new URL('../dist/hall-camera.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createHallCamera}=new Function('THREE',hallSource+';return {createHallCamera}')(THREE);
const {createCameraSafety}=new Function('THREE','createHallCamera',source+';return {createCameraSafety}')(THREE,createHallCamera);
test('camera stays above terrain and bridge even after an extreme pan',()=>{
 const camera=new THREE.PerspectiveCamera();const controls={target:new THREE.Vector3(0,2,0)};
 const safety=createCameraSafety(camera,controls,()=>1.2);
 camera.position.set(0,-5,8);safety.constrain();assert.ok(camera.position.y>=2.05);
 const terrain=new THREE.Mesh(new THREE.PlaneGeometry(500,500),new THREE.MeshBasicMaterial());terrain.rotation.x=-Math.PI/2;terrain.position.y=7;
 safety.setTerrain(terrain);camera.position.set(20,2,20);safety.constrain();assert.ok(camera.position.y>=7.85-1e-6);
 controls.target.set(100,99,100);safety.constrain();assert.ok(controls.target.x<=18&&controls.target.y<=5&&controls.target.z<=17);assert.ok(camera.position.y>=7.85-1e-6);
});
test('interior pan reaches the mural bays and never drops below its floor',()=>{
 const camera=new THREE.PerspectiveCamera();camera.position.set(0,-1,-5);
 const controls={target:new THREE.Vector3(-100,-90,30)};const safety=createCameraSafety(camera,controls,()=>1.095);
 safety.constrain(true);assert.deepEqual(controls.target.toArray(),[-5.15,1.55,-4.4]);assert.ok(camera.position.y>1.9);
});
test('looking up inside stays behind the entrance plaque and below the low doorway',()=>{
 const camera=new THREE.PerspectiveCamera();camera.position.set(12,9,2);
 const controls={target:new THREE.Vector3(0,4.8,-7.8)};const safety=createCameraSafety(camera,controls,()=>1.095);
 safety.constrain(true);assert.ok(camera.position.x<=5.08);assert.ok(camera.position.z<=-4.02);assert.ok(camera.position.y<=3.78);
 controls.target.y=99;safety.constrain(true);assert.ok(controls.target.y<=5.6);assert.ok(camera.position.y<=4.0);
});
