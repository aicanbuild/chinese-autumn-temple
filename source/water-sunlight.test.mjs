import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/water-sunlight.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installWaterSunlight}=new Function('THREE',code+';return {installWaterSunlight};')(THREE);
test('sun shadow resources bind after nested water captures, including map replacement and disabling',()=>{
 const sun=new THREE.DirectionalLight(),renderer={shadowMap:{enabled:true}},water=new THREE.Mesh(new THREE.PlaneGeometry(),new THREE.ShaderMaterial({fragmentShader:'#include <common>\n void main(){vec3 result=waterSunColor*glint;}'}));sun.castShadow=true;
 let map=new THREE.WebGLRenderTarget(512,256),invoked=0;const scene={},camera={};
 water.onBeforeRender=function(r,s,c){assert.equal(this,water);assert.equal(r,renderer);assert.equal(s,scene);assert.equal(c,camera);sun.shadow.map=map;invoked++;};
 const u=installWaterSunlight(water,sun).uniforms;assert.equal(u.waterSunShadowEnabled.value,0);
 water.onBeforeRender(renderer,scene,camera);assert.equal(invoked,1);assert.equal(u.waterSunShadowMap.value,map.texture);assert.deepEqual(u.waterSunShadowSize.value.toArray(),[512,256]);assert.equal(u.waterSunShadowMatrix.value,sun.shadow.matrix);assert.equal(u.waterSunShadowEnabled.value,1);
 sun.shadow.bias=-.002;sun.shadow.normalBias=.03;sun.shadow.radius=2;sun.shadow.intensity=.4;water.onBeforeRender(renderer,scene,camera);assert.deepEqual(u.waterSunShadowParams.value.toArray(),[-.002,.03,2,.4]);
 const oldMap=map;map=new THREE.WebGLRenderTarget(256,128);water.onBeforeRender(renderer,scene,camera);assert.equal(u.waterSunShadowMap.value,map.texture);assert.deepEqual(u.waterSunShadowSize.value.toArray(),[256,128]);oldMap.dispose();
 renderer.shadowMap.enabled=false;water.onBeforeRender(renderer,scene,camera);assert.equal(u.waterSunShadowEnabled.value,0);renderer.shadowMap.enabled=true;sun.castShadow=false;water.onBeforeRender(renderer,scene,camera);assert.equal(u.waterSunShadowEnabled.value,0);
 map.dispose();
});
const motionCode=fs.readFileSync(new URL('../dist/pond-motion.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const {createPondMotion}=new Function('THREE',motionCode+';return {createPondMotion};')(THREE);
test('water sunlight follows world light direction and hidden ancestor state',()=>{
 const parent=new THREE.Group(),sun=new THREE.DirectionalLight(0xffffff,3.7);parent.position.set(5,2,0);parent.add(sun);sun.position.set(1,2,3);sun.target.position.set(0,0,0);const material={uniforms:{}},motion=createPondMotion(material,sun);
 const direction=new THREE.Vector3(6,4,3).normalize();assert.ok(material.uniforms.waterSunDirection.value.distanceTo(direction)<1e-10);assert.equal(material.uniforms.waterSunColor.value.r,3.7);
 parent.visible=false;motion.update(1);assert.equal(material.uniforms.waterSunColor.value.r,0);parent.visible=true;sun.intensity=0;motion.update(2);assert.equal(material.uniforms.waterSunColor.value.r,0);
});
