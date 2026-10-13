import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/creek-rapids.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const api=new Function('THREE',code+';return {subdivideCreekSurface,jetPoint,createCreekBreakers,installRapidUniforms,rapidWaterVertex,rapidWaterFragment,bindCreekBreakerWater};')(THREE);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/creek-rapids.json',import.meta.url)));
test('every overflowing sheet launches above a real stone and rejoins the creek downstream',()=>{
 assert.ok(layout.jets.length>=8);for(const j of layout.jets){const a=api.jetPoint(j,0,0,0),b=api.jetPoint(j,0,1,0);assert.ok(a.y>j.top);assert.ok(b.z>j.z+j.rz*1.05);assert.ok(Math.abs(b.y+.025)<1e-6);for(let t=0;t<1;t+=.05)for(let v=0;v<=1;v+=.02){const p=api.jetPoint(j,.5,v,t);assert.ok(p.toArray().every(Number.isFinite));assert.ok(p.y>-.05&&p.y<.4);}}
});
test('bank vertices remain fixed and the channel has interior vertices with upward facing triangles',()=>{
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([14,-.025,0,16,-.025,0,14.2,-.025,.1,16.2,-.025,.1],3));const dense=api.subdivideCreekSurface(g);assert.equal(dense.attributes.position.count,111);const p=dense.attributes.position;assert.equal(p.getX(0),14);assert.equal(p.getX(36),16);assert.ok(Math.abs(p.getX(37)-14.1)<1e-5);for(let i=0;i<dense.attributes.normal.count;i++)assert.ok(dense.attributes.normal.getY(i)>.99);
});
test('breakers deform in 3D and droplets follow time without growing mesh or instance counts',()=>{
 const scene=new THREE.Scene(),b=api.createCreekBreakers(scene,layout,new THREE.Texture());const before=b.sheets.geometry.attributes.position.array.slice(),count=b.drops.count;for(const t of [.1,.25,1,100])b.update(t);const after=b.sheets.geometry.attributes.position.array;assert.ok(after.some((v,i)=>Math.abs(v-before[i])>.004));assert.equal(b.drops.count,count);assert.ok(after.every(Number.isFinite));assert.equal(scene.children.length,1);assert.ok(b.sheets.material.transparent);assert.equal(b.sheets.material.depthWrite,false);
});
test('rapids texture is linear data with the same uniform on both shader stages',()=>{
 const m={uniforms:{}},t=new THREE.Texture();api.installRapidUniforms(m,t);assert.equal(t.colorSpace,THREE.NoColorSpace);assert.equal(t.flipY,false);assert.equal(t.generateMipmaps,false);assert.equal(m.uniforms.creekRelief.value,t);const vertex=api.rapidWaterVertex('#include <common>\nvToEye = cameraPosition - worldPosition.xyz;');assert.ok(vertex.includes('worldPosition.y+=rapidHeight'));const frag=api.rapidWaterFragment('#include <common>\n// calculate the fresnel term');assert.ok(frag.includes('normal=normalize(normal+vec3(-slope.x'));
});


test('overflow shares the pond optical uniforms and has no pale diffuse foam layer',()=>{
 const b=api.createCreekBreakers(new THREE.Scene(),layout,new THREE.Texture());
 const material=new THREE.ShaderMaterial({uniforms:{pondTime:{value:3},tReflectionMap:{value:new THREE.Texture()}},vertexShader:api.rapidWaterVertex('vCoord = textureMatrix * vec4( position, 1.0 );\nvToEye = cameraPosition - worldPosition.xyz;'),fragmentShader:api.rapidWaterFragment('float foam=creek?(creekFlow.b*.72+.075)*movingCrest:0.;\ngl_FragColor=vec4(mix(waterRadiance,vec3(.76,.82,.78),foam),1.);\n#include <tonemapping_fragment>')});
 const water=new THREE.Mesh(new THREE.PlaneGeometry(),material),bound=api.bindCreekBreakerWater(b,water);
 assert.equal(bound.uniforms,material.uniforms);material.uniforms.pondTime.value=7;assert.equal(bound.uniforms.pondTime.value,7);
 assert.ok(!bound.vertexShader.includes('worldPosition.y+=rapidHeight'));assert.ok(!bound.fragmentShader.includes('vec3(.76,.82,.78)'));assert.ok(bound.fragmentShader.includes('gl_FragColor=vec4(waterRadiance,1.)'));assert.ok(b.sheets.renderOrder>water.renderOrder);
});

test('shared water sheets are excluded from both capture passes and visibility is restored',()=>{
 const app=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8'),fn=app.slice(app.indexOf('function waterCapture(mode){'),app.indexOf('function installWaterMetrics()'));
 for(const mode of ['reflection','refraction'])for(const visible of [true,false]){
  const creekBreakers={root:{visible}},seen=[];
  const capture=()=>{seen.push(creekBreakers.root.visible);return ()=>{};};
  const waterCapture=new Function('creekBreakers','waterVisibility','waterRefraction',`const gpuProfiler=null,renderer={info:{render:{calls:0,triangles:0}}},captureCounters={reflection:{count:0,calls:0,triangles:0,cpuMs:0},refraction:{count:0,calls:0,triangles:0,cpuMs:0}};let waterPassMode=null;${fn};return waterCapture;`)(creekBreakers,{capture},{capture});
  const restore=waterCapture(mode);assert.equal(creekBreakers.root.visible,false);assert.deepEqual(seen,[false]);restore();assert.equal(creekBreakers.root.visible,visible);
 }
});
