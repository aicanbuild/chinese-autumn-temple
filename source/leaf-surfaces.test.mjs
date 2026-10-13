import {applyCanopyWind} from './foliage-test-utils.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {canopyLeafProfile,canopyLeafSurface} from '../dist/canopy-leaf-profile.js';
const source=fs.readFileSync(new URL('../dist/leaf-surfaces.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createLeafGeometry,createFallenLeafGeometry,applyLeafSurface}=new Function('THREE','applyCanopyWind','canopyLeafProfile',source+';return {createLeafGeometry,createFallenLeafGeometry,applyLeafSurface};')(THREE,applyCanopyWind,canopyLeafProfile);
test('curved canopy leaf keeps the root fixed, consistent UVs and a bounded eight-triangle profile',()=>{
 const g=createLeafGeometry(),p=g.attributes.position;assert.equal(g.index.count/3,8);assert.equal(p.count,9);assert.equal(p.getZ(1),0);assert.ok(g.boundingBox.max.z<.1);assert.ok(p.getZ(7)>0);
 for(let i=0;i<g.attributes.normal.count;i++){const n=new THREE.Vector3().fromBufferAttribute(g.attributes.normal,i);assert.ok(Number.isFinite(n.x));assert.ok(Math.abs(n.length()-1)<1e-6);}
 for(const v of g.attributes.uv.array)assert.ok(v>=0&&v<=1);
});
test('canopy analytic normals match the curved surface and the exported Blender profile',()=>{
 const profile=canopyLeafProfile();assert.deepEqual(JSON.parse(JSON.stringify(profile)),JSON.parse(fs.readFileSync(new URL('./canopy-leaf-profile.json',import.meta.url))));
 for(const x of [-.5,-.3,0,.23,.5])for(const y of [-.5,-.2,.1,.5]){const p=canopyLeafSurface(x,y),e=.000001;assert.ok(Math.abs(p.dx-(canopyLeafSurface(x+e,y).height-canopyLeafSurface(x-e,y).height)/(2*e))<1e-8);assert.ok(Math.abs(p.dy-(canopyLeafSurface(x,y+e).height-canopyLeafSurface(x,y-e).height)/(2*e))<1e-8);}
});
test('fallen leaves have curled edges and stay above the calibrated landing plane',()=>{
 const g=createLeafGeometry(true);assert.ok(g.index.count/3>=50&&g.index.count/3<=120);assert.ok(g.boundingBox.min.z>=0);assert.ok(g.boundingBox.max.z>.03);
 const p=g.attributes.position;assert.ok(p.getZ(0)!==p.getZ(2));
});
test('wind and settled surface variants retain independent programs and share detail maps',()=>{
 const normal=new THREE.Texture(),surface=new THREE.Texture(),wind={value:1};const moving=applyLeafSurface(new THREE.MeshStandardMaterial(),{normal,surface,wind});
 const settled=applyLeafSurface(moving.clone(),{normal,surface});assert.equal(settled.normalMap,normal);assert.equal(settled.roughnessMap,surface);assert.notEqual(moving.customProgramCacheKey(),settled.customProgramCacheKey());
 const shader=()=>({uniforms:{},vertexShader:'#include <uv_vertex>\n#include <beginnormal_vertex>\n#include <begin_vertex>',fragmentShader:'#include <lights_physical_pars_fragment>'});
 const a=shader(),b=shader();moving.onBeforeCompile(a);settled.onBeforeCompile(b);assert.equal(a.uniforms.uWind,wind);assert.equal(b.uniforms.uWind,undefined);assert.equal(b.uniforms.uLeafSurface.value,surface);
});
