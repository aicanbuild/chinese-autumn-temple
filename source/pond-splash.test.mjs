import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/pond-splash.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');const create=new Function('THREE',source+';return createPondSplash')(THREE);
test('rapid pond clicks reuse the particle pool, finite water droplets expire and no meshes accumulate',()=>{const scene=new THREE.Scene(),s=create(scene,(x,z)=>Math.abs(x)<10&&Math.abs(z)<10);assert.equal(scene.children.length,1);for(let i=0;i<1000;i++)s.splash(2,3);s.update(.08);assert.equal(s.stats.clicks,1000);assert.equal(scene.children.length,1);const m=scene.children[0];assert.equal(m.count,96);assert.ok(m.visible);assert.ok(Array.from(m.instanceMatrix.array).every(Number.isFinite));for(let i=0;i<100;i++)s.update(1/60);assert.ok(scene.children.every(o=>!o.visible));assert.equal(s.stats.active,0);s.update(100);assert.ok(scene.children.every(o=>!o.visible));});

test('one impact makes only twelve small low droplets and no separate crown mesh',()=>{
 const scene=new THREE.Scene(),s=create(scene,()=>true);s.splash(0,0);s.update(.05);
 assert.equal(s.stats.active,12);assert.equal(scene.children.length,1);assert.ok(scene.children[0].material.opacity<.3);
 const matrix=new THREE.Matrix4(),pos=new THREE.Vector3(),q=new THREE.Quaternion(),scale=new THREE.Vector3();
 for(let i=0;i<12;i++){scene.children[0].getMatrixAt(i,matrix);matrix.decompose(pos,q,scale);assert.ok(pos.y<.10);assert.ok(scale.x<.012&&scale.y<.016);}
});
