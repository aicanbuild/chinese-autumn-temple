import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {pondTransmittanceGLSL} from '../dist/water-medium.js';
const source=fs.readFileSync(new URL('../dist/pond-optics.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installPondOptics,refractedPondRay,pondDirectionalLighting}=new Function('THREE','pondTransmittanceGLSL',source+';return {installPondOptics,refractedPondRay,pondDirectionalLighting}')(THREE,pondTransmittanceGLSL);
test('underwater optics keeps existing fish animation hooks and does not alter dry fixtures',()=>{
 const scene=new THREE.Scene(),fishMaterial=new THREE.MeshStandardMaterial(),dryMaterial=new THREE.MeshStandardMaterial();
 let called=0;fishMaterial.onBeforeCompile=s=>{called++;s.uniforms.koiTime={value:3};s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=.1;');};fishMaterial.customProgramCacheKey=()=> 'existing-koi-deformation';
 for(let i=0;i<2;i++){const fish=new THREE.InstancedMesh(new THREE.SphereGeometry(),fishMaterial,4);fish.userData.waterSide='below';scene.add(fish);}
 const dry=new THREE.Mesh(new THREE.BoxGeometry(),dryMaterial);scene.add(dry);const original=dryMaterial.onBeforeCompile;
 const time={value:10},maps=[new THREE.Texture(),new THREE.Texture()];const result=installPondOptics(scene,maps,time);assert.equal(result.materials,1);assert.equal(dryMaterial.onBeforeCompile,original);
 const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};fishMaterial.onBeforeCompile(shader);
 assert.equal(called,1);assert.equal(shader.uniforms.koiTime.value,3);assert.equal(shader.uniforms.pondTime,time);assert.equal(shader.uniforms.pondLight0.value,maps[0]);assert.ok(shader.vertexShader.includes('transformed.x+=.1;'));assert.ok(shader.vertexShader.includes('instanceMatrix*pondPoint'));assert.ok(fishMaterial.customProgramCacheKey().startsWith('existing-koi-deformation|'));
 assert.ok(shader.fragmentShader.includes(pondTransmittanceGLSL()));assert.ok(shader.fragmentShader.includes('pondBeamTransmittance(path)*focus'));assert.ok(!shader.fragmentShader.includes('vec3(.25,.075,.045)'));
});
test('pond receivers share baked maps without new meshes or modifications to basic materials',()=>{
 const scene=new THREE.Scene();for(const name of ['Riverbed sediment','Continuous granite with wet waterline']){const m=new THREE.MeshStandardMaterial();m.name=name;scene.add(new THREE.Mesh(new THREE.BoxGeometry(),m));}
 const unlit=new THREE.Mesh(new THREE.PlaneGeometry(),new THREE.MeshBasicMaterial());unlit.userData.waterSide='below';scene.add(unlit);const original=unlit.material.onBeforeCompile;
 const count=scene.children.length,maps=[new THREE.Texture(),new THREE.Texture()];assert.equal(installPondOptics(scene,maps,{value:0}).materials,2);assert.equal(scene.children.length,count);assert.equal(unlit.material.onBeforeCompile,original);for(const t of maps){assert.equal(t.colorSpace,THREE.NoColorSpace);assert.equal(t.wrapS,THREE.RepeatWrapping);}
});

test('mean-surface refraction satisfies Snell and remains finite at grazing incidence',()=>{
 for(const angle of [0,.3,.8,Math.PI/2]){
  const ray=refractedPondRay(new THREE.Vector3(Math.sin(angle),Math.cos(angle),0));
  assert.ok(Math.abs(ray.length()-1)<1e-12);assert.ok(ray.y<0);
  assert.ok(Math.abs(-ray.x-Math.sin(angle)/1.333)<1e-12);
 }
 const ray=refractedPondRay(new THREE.Vector3());assert.ok(ray.distanceTo(new THREE.Vector3(0,-1,0))<1e-12);
});
test('moving or parented sunlight updates the shared refracted direction without recompilation',()=>{
 const scene=new THREE.Scene(),group=new THREE.Group(),sun=new THREE.DirectionalLight();scene.add(group);group.add(sun,sun.target);group.position.set(3,2,1);sun.position.set(-24,21,10);sun.target.position.set(0,0,-1);
 const m=new THREE.MeshStandardMaterial();const fish=new THREE.Mesh(new THREE.SphereGeometry(),m);fish.userData.waterSide='below';scene.add(fish);
 const optics=installPondOptics(scene,[new THREE.Texture(),new THREE.Texture()],{value:0},sun);const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};m.onBeforeCompile(shader);
 const version=m.version,first=shader.uniforms.pondSunDirection.value.clone();sun.position.set(7,18,-9);optics.update();
 const expected=sun.position.clone().sub(sun.target.position).normalize();assert.ok(shader.uniforms.pondSunDirection.value.distanceTo(expected)<1e-12);assert.ok(first.distanceTo(expected)>.5);assert.equal(m.version,version);
 const ray=refractedPondRay(expected);assert.ok(shader.uniforms.pondRefractedUp.value.distanceTo(ray.clone().negate())<1e-12);
 assert.ok(Math.abs(shader.uniforms.pondRaySlope.value.x-ray.x/-ray.y)<1e-12);
});
test('caustic modulation touches only directional light evaluation and preserves local lights and shadow calls',()=>{
 const before=THREE.ShaderChunk.lights_fragment_begin,after=pondDirectionalLighting(before),start=before.indexOf('#if ( NUM_DIR_LIGHTS'),end=before.indexOf('#if ( NUM_RECT_AREA_LIGHTS',start);
 assert.equal(after.slice(0,start),before.slice(0,start));assert.ok(after.endsWith(before.slice(end)));
 assert.equal((after.match(/getShadow\(/g)||[]).length,(before.match(/getShadow\(/g)||[]).length);
 assert.equal((after.match(/RE_Direct\(/g)||[]).length,(before.match(/RE_Direct\(/g)||[]).length);
});
