import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/candlelight.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installCandleWaxGeometry,finishCandleWax}=new Function('THREE',code+';return {installCandleWaxGeometry,finishCandleWax};')(THREE);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary.json',import.meta.url)));
test('continuous wax export has two untextured geometry batches with all four supported candles',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/candle-wax.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.equal(d.meshes.length,2);assert.equal((d.images??[]).length,0);assert.equal((d.materials??[]).length,0);assert.ok(b.length<150000);
 assert.deepEqual(new Set(d.nodes.filter(n=>n.mesh!==undefined).map(n=>n.extras.sourceMaterial)),new Set(['Sanctuary | vermilion beeswax','Sanctuary | charred cotton wick']));
 assert.equal(layout.continuousWax.length,4);
 for(const c of layout.continuousWax){assert.equal(c.runs,7);assert.ok(c.radius>.046&&c.radius<.076);assert.equal(c.triangles,19200);assert.ok(Math.abs(layout.flames[c.index][1]-.015-c.pool)<1e-9);assert.ok(Math.abs(c.bottom+c.height-c.pool-.012)<1e-8);}
});
test('replacement preserves original materials, geometry world placement and surrounding altar',()=>{
 const root=new THREE.Group(),asset=new THREE.Group();root.position.x=2;const original=[];
 for(const name of ['wax','wick']){const material=new THREE.MeshStandardMaterial();material.name=name;const mesh=new THREE.Mesh(new THREE.BoxGeometry(),material);root.add(mesh);original.push(material);const replacement=new THREE.Mesh(new THREE.SphereGeometry(.1));replacement.position.set(3,2,1);replacement.userData.sourceMaterial=name;asset.add(replacement);}
 const altar=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());root.add(altar);const altarGeometry=altar.geometry;
 assert.equal(installCandleWaxGeometry(root,asset),2);root.updateMatrixWorld(true);
 for(let i=0;i<2;i++){assert.equal(root.children[i].material,original[i]);assert.ok(new THREE.Box3().setFromObject(root.children[i]).getCenter(new THREE.Vector3()).distanceTo(new THREE.Vector3(3,2,1))<1e-6);}
 assert.equal(altar.geometry,altarGeometry);assert.equal(root.children.length,3);
});
test('liquid-wax gloss follows each authored melt-pool radius and height',()=>{
 const material=finishCandleWax(new THREE.MeshStandardMaterial(),layout),shader={uniforms:{},vertexShader:'#include <project_vertex>',fragmentShader:'#include <roughnessmap_fragment>\n#include <emissivemap_fragment>'};material.onBeforeCompile(shader);
 for(const c of layout.continuousWax){assert.ok(Math.abs(shader.uniforms.waxTips.value[c.index].y-c.pool)<1e-9);assert.ok(Math.abs(shader.uniforms.waxPoolRadii.value[c.index]-c.radius*.68)<1e-9);}
 assert.ok(shader.uniforms.waxPoolRadii.value[0]>shader.uniforms.waxPoolRadii.value[1]);
});
