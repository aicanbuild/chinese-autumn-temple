import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/candlelight.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createCandlelight,finishCandleWax}=new Function('THREE',code+';return {createCandlelight,finishCandleWax}')(THREE);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary.json',import.meta.url)));
test('four lit flames enclose actual wick tips and carry independent bounded light',()=>{
 const scene=new THREE.Scene(),c=createCandlelight(layout,scene);assert.equal(c.flames.length,4);assert.equal(c.lights.length,4);assert.equal(new Set(c.flames.map(f=>f.geometry)).size,1);
 c.enter();for(let i=0;i<4;i++)c.light(i);c.update(0,1);
 const allocations=scene.children.length;
 for(let i=0;i<4;i++){
  const [x,y,z]=layout.flames[i],f=c.flames[i];f.geometry.computeBoundingBox();f.updateMatrixWorld();
  const box=f.geometry.boundingBox.clone().applyMatrix4(f.matrixWorld);
  assert.ok(box.containsPoint(new THREE.Vector3(x+.004,y-.008,z)),'actual native wick tip lies inside flame volume');
  assert.ok(f.geometry.boundingBox.max.y<.11);assert.equal(f.material.depthWrite,false);assert.equal(f.material.side,THREE.BackSide);
 }
 for(let t=0;t<600;t+=.31){
  c.update(t);
  for(let i=0;i<4;i++){
   const f=c.flames[i],m=f.material.uniforms.motion.value,l=c.lights[i];
   assert.ok(m.z>.93&&m.z<1.07);assert.ok(l.intensity>.58&&l.intensity<.72);assert.ok(Math.abs(l.position.y-f.position.y-.028*m.z)<1e-10);
   assert.ok(Math.abs(m.x)<1&&Math.abs(m.y)<1);assert.equal(l.castShadow,false);
  }
 }
 assert.equal(scene.children.length,allocations);assert.notDeepEqual(c.flames[0].material.uniforms.motion.value,c.flames[1].material.uniforms.motion.value);
 c.update(12);const first=c.flames.map(f=>f.material.uniforms.motion.value.clone());c.update(12);assert.deepEqual(c.flames.map(f=>f.material.uniforms.motion.value),first,'paused time keeps fire stable');
});
test('wax finish preserves source pigment and binds all four real crown positions',()=>{
 const source=new THREE.MeshStandardMaterial({color:'#ab1510',roughness:.48}),before=source.color.clone(),finished=finishCandleWax(source,layout);
 const shader={uniforms:{},vertexShader:'#include <project_vertex>',fragmentShader:'#include <roughnessmap_fragment>\n#include <emissivemap_fragment>'};finished.onBeforeCompile(shader);
 assert.notEqual(finished,source);assert.deepEqual(finished.color,before);assert.equal(source.roughness,.48);
 assert.deepEqual(shader.uniforms.waxTips.value.map(v=>v.toArray()),layout.flames.map(([x,y,z])=>[x,y-.015,z]));
});

test('each visit starts dark; individual candle light ramps up and cannot be counted twice',()=>{
 const scene=new THREE.Scene(),c=createCandlelight(layout,scene),children=scene.children.length;
 assert.equal(c.stats.count,0);assert.ok(c.flames.every(f=>!f.visible));assert.ok(c.lights.every(l=>l.intensity===0));
 assert.equal(c.light(0),false,'cannot light from outside');c.enter();
 for(const invalid of [-1,4,1.5,NaN])assert.equal(c.light(invalid),false);
 for(let i=0;i<4;i++){
  assert.equal(c.light(i),true);assert.equal(c.light(i),false);assert.equal(c.stats.count,i+1);
  c.update(i,.325);assert.ok(c.levels.value[i]>.49&&c.levels.value[i]<.51);
  assert.ok(c.flames[i].visible);assert.ok(c.lights[i].intensity>0);
  for(let j=i+1;j<4;j++){assert.equal(c.flames[j].visible,false);assert.equal(c.lights[j].intensity,0);}
  c.update(i+.325,.325);assert.equal(c.strength,(i+1)/4);
 }
 c.leave();assert.equal(c.strength,0);assert.ok(c.flames.every(f=>!f.visible));assert.ok(c.lights.every(l=>l.intensity===0));
 c.enter();assert.deepEqual(c.stats.lit,[false,false,false,false]);c.update(100,10);assert.equal(c.strength,0);
 assert.equal(scene.children.length,children,'visits reuse the same flame and light objects');
});
test('unlit wax has no residual emission and shares the live per-candle levels',()=>{
 const c=createCandlelight(layout,new THREE.Scene());const wax=finishCandleWax(new THREE.MeshStandardMaterial(),layout,c.levels);
 const shader={uniforms:{},vertexShader:'#include <project_vertex>',fragmentShader:'#include <roughnessmap_fragment>\n#include <emissivemap_fragment>'};wax.onBeforeCompile(shader);
 assert.equal(shader.uniforms.candleLevels,c.levels);assert.deepEqual([...shader.uniforms.candleLevels.value],[0,0,0,0]);
 c.enter();c.light(2);c.update(1,1);assert.deepEqual([...shader.uniforms.candleLevels.value],[0,0,1,0]);
 c.leave();assert.deepEqual([...shader.uniforms.candleLevels.value],[0,0,0,0]);
});
