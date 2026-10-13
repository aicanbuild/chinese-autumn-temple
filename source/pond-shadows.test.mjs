import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/pond-shadows.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');const {pondShadowSlope,refractedShadowPoint,installPondShadows}=new Function('THREE',source+';return {pondShadowSlope,refractedShadowPoint,installPondShadows}')(T);
test('a straight ray in shadow space follows two-medium Snell paths in world space',()=>{
 for(let i=0;i<500;i++){
  const s=new T.Vector3(Math.sin(i*.83),.12+(i%31)/31,Math.cos(i*.39)).normalize(),n=1.333,w=new T.Vector3(-s.x/n,-Math.sqrt(1-(s.x*s.x+s.z*s.z)/(n*n)),-s.z/n),h=-.025,depth=.05+(i%23)*.09;
  const p=new T.Vector3(2*Math.sin(i),h-depth,4+Math.cos(i)),virtual=refractedShadowPoint(p,s),entry=p.clone().addScaledVector(w,-depth/-w.y),entryViaAir=virtual.clone().addScaledVector(s,depth/s.y);
  assert.ok(entry.distanceTo(entryViaAir)<1e-12);
  const travel=.1+(i%17)*.03,q=p.clone().addScaledVector(w,travel),vq=refractedShadowPoint(q,s),delta=vq.sub(virtual);assert.ok(delta.clone().cross(s).length()<1e-12);
 }
});
test('air-side points and a vertical sun retain their original shadow coordinates',()=>{
 const s=new T.Vector3(-.8,.6,0);for(const y of [-.025,0,1,10]){const p=new T.Vector3(1,y,4);assert.deepEqual(refractedShadowPoint(p,s).toArray(),p.toArray());}
 assert.deepEqual(pondShadowSlope(new T.Vector3(0,1,0)).toArray(),[0,0]);
});
test('shadow patch preserves existing deformation, isolates sunlight from other lights, and pads shifted bounds',()=>{
 const scene=new T.Scene(),sun=new T.DirectionalLight();sun.position.set(-8,6,0);scene.add(sun,sun.target);const sphere=new T.Mesh(new T.SphereGeometry(.1),new T.MeshStandardMaterial());sphere.position.set(0,-.5,5.8);sphere.castShadow=true;const original=new T.MeshDepthMaterial();let prior=0;original.onBeforeCompile=()=>prior++;sphere.customDepthMaterial=original;scene.add(sphere);
 const system=installPondShadows(scene,sun),shader={uniforms:{},vertexShader:'#include <project_vertex>'};sphere.customDepthMaterial.onBeforeCompile(shader);assert.equal(prior,1);assert.notEqual(sphere.customDepthMaterial,original);assert.ok(shader.vertexShader.includes('pondShadowPoint'));assert.equal(sphere.userData.pondStaticShadow,undefined);
 sphere.onBeforeShadow(null,sphere,null,sun.shadow.camera);assert.equal(shader.uniforms.pondShadowPass.value,1);sphere.onAfterShadow();assert.equal(shader.uniforms.pondShadowPass.value,0);sphere.onBeforeShadow(null,sphere,null,new T.PerspectiveCamera());assert.equal(shader.uniforms.pondShadowPass.value,0);sphere.onAfterShadow();
 const padding=sphere.userData.refractedShadowPadding;assert.ok(padding>0);sun.position.set(-8,3,0);system.update();assert.ok(sphere.userData.refractedShadowPadding>padding);
});
test('only opted-in ordinary stationary casters expose the sunlight cache contract',()=>{
 const scene=new T.Scene(),sun=new T.DirectionalLight();sun.position.set(-8,6,0);scene.add(sun,sun.target);const low=new T.Mesh(new T.BoxGeometry(1,1,1),new T.MeshStandardMaterial()),high=low.clone();low.position.set(0,-.6,5.8);high.position.set(0,2,5.8);low.castShadow=high.castShadow=true;scene.add(low,high);const state=installPondShadows(scene,sun);assert.equal(state.casters.length,1);assert.equal(low.userData.pondStaticShadow.depth,low.customDepthMaterial);assert.equal(high.customDepthMaterial,undefined);assert.equal(low.userData.pondStaticShadow.state().at(-1),1);state.enabled=false;assert.equal(low.userData.pondStaticShadow.state().at(-1),0);
});
