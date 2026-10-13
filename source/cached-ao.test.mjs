import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {AOSceneState} from '../dist/ao-scene-state.js';
const code=fs.readFileSync(new URL('../dist/cached-ao.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export class','class');
class Pass{
 static OUTPUT={Default:0,Normal:1};
 constructor(scene,camera,width,height){this.width=width;this.height=height;this.scene=scene;this.camera=camera;this.output=0;this.copyMaterial={uniforms:{tDiffuse:{}}};this.blurRenderTarget={texture:{}};this.full=0;this.composites=[];}
 setSize(){}
 render(){this.full++;}
 _renderPass(renderer,material,target){this.composites.push(target);}
}
const CachedSSAOPass=new Function('Matrix4','Frustum','Box3','CustomBlending','SSAOPass','AOSceneState',code+';return CachedSSAOPass;')(THREE.Matrix4,THREE.Frustum,THREE.Box3,THREE.CustomBlending,Pass,AOSceneState);
test('unchanged AO stays cached while camera, resize and prop changes refresh immediately',()=>{
 let time=0;const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),pass=new CachedSSAOPass(scene,camera,100,100,16,()=>time),target={};
 const prop=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());scene.add(prop);scene.updateMatrixWorld(true);
 pass.render({},null,target);assert.equal(pass.full,1);
 time=40;pass.render({},null,target);assert.equal(pass.full,1);assert.equal(pass.reuses,1);assert.equal(pass.composites[0],target);
 time=10000;pass.render({},null,target);assert.equal(pass.full,1);
 prop.position.x=1;scene.updateMatrixWorld(true);pass.render({},null,target);assert.equal(pass.full,2);
 camera.position.x=1;camera.updateMatrixWorld();pass.render({},null,target);assert.equal(pass.full,3);
 camera.fov=60;camera.updateProjectionMatrix();pass.render({},null,target);assert.equal(pass.full,4);
 pass.setSize(200,200);pass.render({},null,target);assert.equal(pass.full,5);
 pass.output=Pass.OUTPUT.Normal;pass.render({},null,target);pass.render({},null,target);assert.equal(pass.full,7);
});

test('AO state follows contributor transforms, topology, attributes, visibility and membership',()=>{
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),state=new AOSceneState(),group=new THREE.Group();scene.add(group);
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());group.add(mesh);
 function scan(){scene.updateMatrixWorld(true);return state.changed(scene,camera);}
 assert.equal(scan(),true);assert.equal(scan(),false);
 for(const change of [()=>group.position.y++,()=>mesh.geometry.attributes.position.needsUpdate=true,()=>mesh.geometry.attributes.normal.needsUpdate=true,
  ()=>mesh.geometry.setIndex([0,1,2]),()=>mesh.geometry.setDrawRange(0,3),()=>mesh.material.visible=false,()=>mesh.material.visible=true,
  ()=>group.visible=false,()=>group.visible=true,()=>mesh.geometry=mesh.geometry.clone()]){
  change();assert.equal(scan(),true);assert.equal(scan(),false);
 }
 const replacement=mesh.clone();group.remove(mesh);group.add(replacement);assert.equal(scan(),true);assert.equal(scan(),false);
 group.remove(replacement);assert.equal(scan(),true);assert.equal(state.records.size,0);
});

test('excluded animated subtrees do not invalidate architectural AO',()=>{
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),state=new AOSceneState(),group=new THREE.Group();group.userData.noAO=true;scene.add(group);
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());group.add(mesh);
 const scan=()=>{scene.updateMatrixWorld(true);return state.changed(scene,camera,o=>o.userData.noAO);};
 assert.equal(scan(),false);mesh.position.x=2;mesh.geometry.attributes.position.needsUpdate=true;assert.equal(scan(),false);
 group.userData.noAO=false;assert.equal(scan(),true);
 mesh.morphTargetInfluences=[0];assert.equal(scan(),true);mesh.morphTargetInfluences[0]=.5;assert.equal(scan(),true);
});

test('interleaved buffer updates, AO settings and untracked shader animation invalidate correctly',()=>{
 let time=0;const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),pass=new CachedSSAOPass(scene,camera,100,100,16,()=>time);
 const buffer=new THREE.InterleavedBuffer(new Float32Array([0,0,0,1,0,0,0,1,0]),3),g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.InterleavedBufferAttribute(buffer,3,0));
 const mesh=new THREE.Mesh(g,new THREE.MeshStandardMaterial());mesh.position.z=-3;scene.add(mesh);scene.updateMatrixWorld(true);pass.render({},null,{});assert.equal(pass.full,1);
 buffer.needsUpdate=true;pass.render({},null,{});assert.equal(pass.full,2);
 pass.kernelRadius=.3;pass.render({},null,{});assert.equal(pass.full,3);
 mesh.userData.aoAnimated=true;time=81;pass.render({},null,{});assert.equal(pass.full,4);time=90;pass.render({},null,{});assert.equal(pass.full,4);
 time=162;pass.render({},null,{});assert.equal(pass.full,5);
});

test('offscreen bounded shader animation reuses AO, then refreshes while visible',()=>{
 let time=0;const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(50,1,.1,100),pass=new CachedSSAOPass(scene,camera,100,100,16,()=>time),plant=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());plant.position.set(0,0,5);plant.userData.aoAnimated=true;scene.add(plant);scene.updateMatrixWorld(true);camera.updateMatrixWorld();pass.render({},null,{});time=100;pass.render({},null,{});assert.equal(pass.full,1);camera.rotation.y=Math.PI;camera.updateMatrixWorld();pass.render({},null,{});assert.equal(pass.full,2);time=200;pass.render({},null,{});assert.equal(pass.full,3);camera.rotation.y=0;camera.updateMatrixWorld();pass.render({},null,{});time=1000;pass.render({},null,{});assert.equal(pass.full,4);
});

test('known slow plant motion refreshes distant AO less often while close views shorten the interval',()=>{
 let time=0;const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(50,1,.1,100),pass=new CachedSSAOPass(scene,camera,700,700,16,()=>time),plant=new THREE.Mesh(new THREE.BoxGeometry(.4,.4,.4),new THREE.MeshStandardMaterial());plant.userData.aoAnimated=true;plant.userData.aoMotionSpeed=.021;plant.position.z=-30;scene.add(plant);scene.updateMatrixWorld(true);camera.updateMatrixWorld();pass.render({},null,{});const distant=pass.refreshAt;assert.ok(distant>300);time=200;pass.render({},null,{});assert.equal(pass.full,1);plant.position.z=-3;scene.updateMatrixWorld(true);pass.render({},null,{});assert.ok(pass.refreshAt-time<80);time=pass.refreshAt+1;pass.render({},null,{});assert.equal(pass.full,3);
});
