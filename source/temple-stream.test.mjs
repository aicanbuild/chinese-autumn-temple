import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {CREEK_CURRENT_SCALE,CREEK_CURRENT_SPEED} from '../dist/water-current.js';
const source=fs.readFileSync(new URL('../dist/temple-stream.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const api=new Function('THREE','CREEK_CURRENT_SCALE','CREEK_CURRENT_SPEED',source+';return {streamCenter,streamWidth,streamContains,streamWaterFragment,installStreamUniforms,installTempleStream}')(THREE,CREEK_CURRENT_SCALE,CREEK_CURRENT_SPEED);
test('creek corridor stays outside koi pond and protects every wet cross-section',()=>{
 for(let z=-72;z<=20;z+=.04){const c=api.streamCenter(z),w=api.streamWidth(z);assert.ok(w>0&&c-w>11.7);assert.ok(api.streamContains(c,z));assert.ok(api.streamContains(c+w*.93,z));assert.ok(!api.streamContains(c+w*1.4+.3,z));}assert.ok(!api.streamContains(15,22));assert.ok(!api.streamContains(15,-74));
});
test('phase crossfade remains continuous when either flow phase wraps',()=>{
 const n=x=>Math.sin(x*2.2)+Math.cos(x*.7);const flow=t=>{const a=(t/1.25)%1,b=(t/1.25+.5)%1,m=Math.abs(2*a-1);return n(a)*(1-m)+n(b)*m;};
 for(const t of [.625,1.25,1.875,2.5,3.75])assert.ok(Math.abs(flow(t-1e-7)-flow(t+1e-7))<1e-6);
});
test('flow atlas is data, repeating ripples use independent textures',()=>{const material={uniforms:{}},map=new THREE.Texture(),normals=[new THREE.Texture(),new THREE.Texture()];api.installStreamUniforms(material,map,normals);assert.equal(map.flipY,false);assert.equal(map.wrapS,THREE.ClampToEdgeWrapping);for(const n of normals)assert.equal(n.wrapS,THREE.RepeatWrapping);assert.equal(material.uniforms.streamFlow.value,map);});
const glb=(name)=>{const b=fs.readFileSync(new URL('../dist/assets/'+name,import.meta.url));return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));};
test('authored water is flat and creek assemblies all export finite bounds',()=>{const j=glb('temple-stream.glb');assert.equal(j.meshes.length,5);const node=j.nodes.find(n=>n.extras?.streamAssembly==='water surface');assert.ok(node);const g=j.meshes[node.mesh].primitives[0],a=j.accessors[g.attributes.POSITION];assert.ok(a.max.every(Number.isFinite));assert.ok(Math.abs(a.max[1]-a.min[1])<1e-6);assert.ok(a.count>700);assert.ok(j.nodes.some(n=>n.extras?.streamAssembly.includes('pebbles')));});
test('carved terrain retains authored forest vertex colors',()=>{const j=glb('terrain.glb'),p=j.meshes[0].primitives[0];assert.equal(j.accessors[p.attributes.COLOR_0].componentType,5123);assert.ok(!('COLOR_1' in p.attributes));assert.equal(j.materials[0].pbrMetallicRoughness.roughnessFactor,.91);});

test('the headwater narrows into the distant hillside and meets the flat courtyard water',()=>{
 assert.ok(api.streamWidth(-55)<api.streamWidth(-35));assert.ok(api.streamWidth(-35)<api.streamWidth(-18));assert.ok(api.streamWidth(-71)<.1);
 const j=glb('temple-stream.glb'),node=j.nodes.find(n=>n.extras?.streamAssembly==='headwater surface');assert.ok(node);
 const a=j.accessors[j.meshes[node.mesh].primitives[0].attributes.POSITION];assert.ok(a.min[2]<=-71.99);assert.ok(Math.abs(a.max[2]+18)<.001);assert.ok(a.max[1]>25);assert.ok(Math.abs(a.min[1]+.025)<.001);
 const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/temple-stream.json',import.meta.url)));assert.deepEqual(layout.flowBounds,[12,18,-72,20]);assert.equal(layout.coreStart,-18);
});

test('sloped headwater keeps its own terrain-following mesh and moving transparent water material',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene();
 for(const assembly of ['water surface','headwater surface']){const m=new THREE.Mesh(new THREE.PlaneGeometry(),new THREE.MeshStandardMaterial());m.userData.streamAssembly=assembly;root.add(m);}
 const maps=Object.fromEntries(['normal','roughness','stoneColor','moss','sandNormal','waterNormal'].map(k=>[k,new THREE.Texture()]));
 const creek=api.installTempleStream(root,scene,maps);assert.ok(creek.headwater.parent===root);assert.equal(root.children.length,1);assert.ok(creek.waterGeometry);
 assert.equal(creek.headwater.material.normalMap,maps.waterNormal);assert.ok(creek.headwater.material.transparent);assert.ok(creek.headwater.material.opacity<.4);
 const shader={uniforms:{},fragmentShader:'#include <normal_fragment_maps>'};creek.headwater.material.onBeforeCompile(shader);creek.update(12);assert.equal(shader.uniforms.headwaterTime.value,12);assert.ok(shader.fragmentShader.includes(`headwaterTime*${(CREEK_CURRENT_SPEED*.7).toFixed(3)}`));
});
