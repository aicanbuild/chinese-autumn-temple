import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/water-refraction.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const {waterSurfaceExit,installWaterRefraction}=new Function('THREE',source+';return {waterSurfaceExit,installWaterRefraction};')(T);
test('surface exit satisfies Snell across shallow, deep, near-vertical and grazing rays',()=>{
 for(const height of [.01,.1,1,3,20])for(const depth of [.005,.2,1.53,3])for(const distance of [.00001,.1,1,10,40]){
  const eye=new T.Vector3(1,height-.025,2),p=new T.Vector3(1+distance,-.025-depth,2),s=waterSurfaceExit(p,eye);
  const a=s.clone().sub(eye).normalize(),b=p.clone().sub(s).normalize();
  assert.equal(s.y,-.025);assert.ok(s.x>=eye.x&&s.x<=p.x);assert.ok(Math.abs(Math.abs(a.x)-1.333*Math.abs(b.x))<.002);
  // Independent high-precision minimization of optical path length.
  let lo=eye.x,hi=p.x;for(let i=0;i<70;i++){const x=(lo+hi)/2;const derivative=(x-eye.x)/Math.hypot(x-eye.x,height)-1.333*(p.x-x)/Math.hypot(p.x-x,depth);if(derivative>0)hi=x;else lo=x;}
  assert.ok(Math.abs(s.x-(lo+hi)/2)<.0005);
 }
});
test('surface exit remains within half a millimeter against independent optical-path minimization over eight thousand logarithmic cases',()=>{
 let seed=4781,worst=0;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;},log=(a,b)=>Math.exp(Math.log(a)+random()*Math.log(b/a));
 for(let i=0;i<8192;i++){
  const L=log(.000001,150),H=log(.0011,80),D=log(.00001,8),eye=new T.Vector3(0,H,0),point=new T.Vector3(L,-D,0);let lo=0,hi=L;
  for(let j=0;j<80;j++){const x=(lo+hi)/2,gradient=x/Math.hypot(x,H)-1.333*(L-x)/Math.hypot(L-x,D);if(gradient>0)hi=x;else lo=x;}
  const actual=waterSurfaceExit(point,eye,0);assert.ok(Number.isFinite(actual.x)&&actual.x>=-1e-12&&actual.x<=L+1e-12);worst=Math.max(worst,Math.abs(actual.x-(lo+hi)/2));
 }
 assert.ok(worst<.0005,`maximum exit error ${worst} m`);
});
test('capture flags and original frustum states restore, preserving existing material hooks and maps',()=>{
 const scene=new T.Scene(),m=new T.MeshPhysicalMaterial(),texture=new T.Texture();m.map=texture;let called=0;m.onBeforeCompile=s=>{called++;s.vertexShader='// custom deformation\n'+s.vertexShader;};m.customProgramCacheKey=()=> 'authored';
 const a=new T.Mesh(new T.BoxGeometry(),m),b=new T.Mesh(new T.BoxGeometry(),m);b.frustumCulled=false;scene.add(a,b);
 const installed=installWaterRefraction(scene);assert.equal(installed.materials,1);const shader={uniforms:{},vertexShader:'#include <project_vertex>'};m.onBeforeCompile(shader);assert.equal(called,1);assert.equal(m.map,texture);assert.equal(shader.uniforms.waterRefractionPass.value,0);assert.match(shader.vertexShader,/custom deformation/);
 installed.capture('reflection')();assert.equal(shader.uniforms.waterRefractionPass.value,0);assert.equal(a.frustumCulled,true);
 const restore=installed.capture('refraction');assert.equal(shader.uniforms.waterRefractionPass.value,1);assert.equal(a.frustumCulled,false);assert.equal(b.frustumCulled,false);
 const nested=installed.capture('refraction');nested();assert.equal(shader.uniforms.waterRefractionPass.value,1);restore();assert.equal(shader.uniforms.waterRefractionPass.value,0);assert.equal(a.frustumCulled,true);assert.equal(b.frustumCulled,false);
 assert.ok(m.customProgramCacheKey().startsWith('authored|'));assert.match(shader.vertexShader,/gl_Position.xy=/);assert.doesNotMatch(shader.vertexShader,/gl_Position.z\s*=/);
});
