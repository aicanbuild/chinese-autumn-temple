import test from 'node:test';import assert from 'node:assert/strict';import * as THREE from '../dist/vendor/three/three.module.js';import {applyCanopyWind,applyWoodlandWind,createWindShadows} from './foliage-test-utils.mjs';
for(const [name,deform,uniform] of [['canopy',applyCanopyWind,'uWind'],['woodland',applyWoodlandWind,'uWoodlandTime']])test(name+' shadows share the lit vertex deformation, clock and alpha silhouette',()=>{
 const time={value:3},map=new THREE.Texture(),material=new THREE.MeshStandardMaterial({map,alphaTest:.42,side:THREE.DoubleSide}),shadows=createWindShadows(material,time,deform,name),shader=()=>({uniforms:{},vertexShader:'#include <beginnormal_vertex>\n#include <begin_vertex>'});const lit=shader();deform(lit,time);
 for(const shadow of [shadows.depth,shadows.distance]){const s=shader();shadow.onBeforeCompile(s);assert.equal(s.vertexShader,lit.vertexShader);assert.equal(s.uniforms[uniform],time);assert.equal(shadow.map,map);assert.equal(shadow.alphaTest,.42);assert.equal(shadow.side,THREE.DoubleSide);time.value=8;assert.equal(s.uniforms[uniform].value,8);}
 assert.equal(shadows.depth.depthPacking,THREE.RGBADepthPacking);assert.ok(shadows.distance.isMeshDistanceMaterial);
});
test('woodland inverse-transpose normal is orthogonal to the deformed surface tangents',()=>{
 for(const [a,b] of [[.035,.0765],[-.035,-.0765],[0,.055]]){const n=new THREE.Vector3(.2,.5,.8).normalize(),t=new THREE.Vector3(1,0,0).cross(n).normalize(),u=n.clone().cross(t);const deform=v=>new THREE.Vector3(v.x+a*v.y,v.y,v.z+b*v.x);const corrected=n.clone();corrected.x-=b*corrected.z;corrected.y-=a*corrected.x;corrected.normalize();assert.ok(Math.abs(corrected.dot(deform(t)))<1e-12);assert.ok(Math.abs(corrected.dot(deform(u)))<1e-12);}
});
