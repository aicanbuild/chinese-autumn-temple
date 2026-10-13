import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/water-capture-region.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createWaterCaptureRegion}=new Function('THREE',code+';return {createWaterCaptureRegion};')(THREE);
function fixture(){
 const scene=new THREE.Scene(),water=new THREE.Mesh(new THREE.PlaneGeometry(2,2));water.isWater=true;scene.add(water);
 const camera=new THREE.PerspectiveCamera(60,1,.1,100);camera.position.z=10;camera.updateMatrixWorld();
 const target=new THREE.WebGLRenderTarget(1000,1000);
 function mesh(x,z=0){const m=new THREE.Mesh(new THREE.BoxGeometry(.1,.1,.1));m.position.set(x,0,z);scene.add(m);return m;}
 return {scene,water,camera,target,mesh};
}
test('captures only the pond footprint with distortion margin, preserving camera and visibility',()=>{
 const f=fixture(),inside=f.mesh(0),outside=f.mesh(4),hidden=f.mesh(0);hidden.visible=false;
 const r=createWaterCaptureRegion(f.water,f.scene),projection=f.camera.projectionMatrix.clone();
 const original=f.target.scissor.clone();const restore=r.capture('reflection',f.camera,f.target);
 assert.equal(inside.visible,true);assert.equal(outside.visible,false);assert.equal(hidden.visible,false);
 assert.ok(r.stats.reflection.pixelFraction<.06);assert.ok(f.target.scissor.z>190);assert.ok(f.camera.projectionMatrix.equals(projection));
 assert.equal(f.target.scissorTest,true);restore();
 assert.equal(outside.visible,true);assert.equal(hidden.visible,false);assert.ok(f.target.scissor.equals(original));assert.equal(f.target.scissorTest,false);
});
test('moving objects use current world transforms; procedural and instanced objects remain conservative',()=>{
 const f=fixture(),moving=f.mesh(4),dynamic=f.mesh(4);dynamic.frustumCulled=false;
 const instances=new THREE.InstancedMesh(new THREE.BoxGeometry(.1,.1,.1),new THREE.MeshBasicMaterial(),2);
 instances.setMatrixAt(0,new THREE.Matrix4().makeTranslation(0,0,0));instances.setMatrixAt(1,new THREE.Matrix4().makeTranslation(4,0,0));f.scene.add(instances);
 const r=createWaterCaptureRegion(f.water,f.scene);moving.position.x=0;f.scene.updateMatrixWorld(true);
 const restore=r.capture('refraction',f.camera,f.target);assert.equal(moving.visible,true);assert.equal(dynamic.visible,true);assert.equal(instances.visible,true);restore();
});
test('eye-plane crossing retains a full capture and restores prior enabled scissor',()=>{
 const f=fixture();f.water.rotation.y=Math.PI/3;f.water.position.z=10;f.target.scissor.set(4,5,900,800);f.target.scissorTest=true;
 const r=createWaterCaptureRegion(f.water,f.scene),restore=r.capture('reflection',f.camera,f.target);
 assert.equal(r.stats.reflection.fullCapture,true);assert.equal(r.stats.reflection.pixelFraction,1);assert.deepEqual(f.target.scissor.toArray(),[0,0,1000,1000]);restore();
 assert.equal(f.target.scissorTest,true);assert.deepEqual(f.target.scissor.toArray(),[4,5,900,800]);
});
test('batch capture bounds include transformed instances instead of only the prototype',()=>{
 const f=fixture(),prototype=new THREE.BoxGeometry(.1,.1,.1).translate(20,0,0);
 const batch=new THREE.BatchedMesh(1,prototype.attributes.position.count,prototype.index.count,new THREE.MeshBasicMaterial());
 const id=batch.addInstance(batch.addGeometry(prototype));batch.setMatrixAt(id,new THREE.Matrix4().makeTranslation(-20,0,0));f.scene.add(batch);
 const region=createWaterCaptureRegion(f.water,f.scene),restore=region.capture('reflection',f.camera,f.target);
 assert.equal(batch.visible,true);restore();batch.dispose();prototype.dispose();
});
test('partially offscreen pond is clamped to target pixel bounds',()=>{
 const f=fixture();f.water.position.x=5;
 const r=createWaterCaptureRegion(f.water,f.scene),restore=r.capture('reflection',f.camera,f.target),s=f.target.scissor;
 assert.ok(s.x>=0&&s.y>=0&&s.x+s.z<=1000&&s.y+s.w<=1000);assert.ok(s.z>0&&s.w>0);restore();
});
for(const name of ['Reflector','Refractor'])test(name+' invokes region after camera update and restores it on render errors',()=>{
 const code=fs.readFileSync(new URL('../dist/vendor/three/addons/objects/'+name+'.js',import.meta.url),'utf8').replace(/import\s*\{([\s\S]*?)\}\s*from 'three';/,'const {$1}=THREE;').replace(/export\s*\{[^}]+\};?/g,'');
 const Capture=new Function('THREE',code+';return '+name+';')(THREE);
 let called=false,restored=false;
 const plane=new Capture(new THREE.PlaneGeometry(10,10),{beforeCapture(camera,target){called=true;assert.ok(Math.abs(new THREE.Vector3().setFromMatrixPosition(camera.matrixWorld).y)>1);assert.ok(target.isWebGLRenderTarget);return()=>{restored=true;};}});
 plane.rotation.x=-Math.PI/2;plane.updateMatrixWorld();
 const camera=new THREE.PerspectiveCamera(50,1,.1,100);camera.position.set(3,5,10);camera.lookAt(0,0,0);camera.updateMatrixWorld();
 const renderer={xr:{enabled:false},shadowMap:{autoUpdate:false},state:{buffers:{depth:{setMask(){}}}},getRenderTarget:()=>null,setRenderTarget(){},render(){throw new Error('capture failed');},autoClear:true};
 assert.throws(()=>plane.onBeforeRender(renderer,new THREE.Scene(),camera),/capture failed/);assert.equal(called,true);assert.equal(restored,true);plane.dispose();
});

test('grazing-angle captures include displaced crests and the reflection distortion margin',()=>{
 const f=fixture();f.water.rotation.x=-Math.PI/2;f.water.userData.surfaceDisplacement=.55;f.water.updateMatrixWorld();
 const r=createWaterCaptureRegion(f.water,f.scene),point=new THREE.Vector3();let checked=0;
 for(const elevation of [.25,.65,1.2,3])for(let i=0;i<12;i++){
  const angle=i*Math.PI/6;f.camera.position.set(Math.cos(angle)*5,elevation,Math.sin(angle)*5);f.camera.lookAt(0,0,0);f.camera.updateMatrixWorld();
  const restore=r.capture('reflection',f.camera,f.target),rect=f.target.scissor;
  for(const x of [-1,0,1])for(const z of [-1,0,1])for(const y of [-.55,0,.55]){
   point.set(x,y,z).project(f.camera);if(Math.abs(point.x)>1||Math.abs(point.y)>1||Math.abs(point.z)>1)continue;
   for(const dx of [-.018,.018])for(const dy of [-.018,.018]){
    const px=Math.max(0,Math.min(1,(point.x+1)*.5+dx))*f.target.width,py=Math.max(0,Math.min(1,(point.y+1)*.5+dy))*f.target.height;
    assert.ok(px>=rect.x-1&&px<=rect.x+rect.z+1);assert.ok(py>=rect.y-1&&py<=rect.y+rect.w+1);checked++;
   }
  }
  restore();
 }
 assert.ok(checked>1000);
});
