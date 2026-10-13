import {applyCanopyWind,createWindShadows} from './foliage-test-utils.mjs';
import test from 'node:test';
import {applyBarkJunctions} from '../dist/bark-junctions.js';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/garden-trees.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const {installGardenTrees}=new Function('THREE','applyBarkJunctions',code+';return {installGardenTrees}')(THREE,applyBarkJunctions);
test('tree replacement preserves other architecture and reuses loaded bark textures',()=>{
 const model=new THREE.Group(),trees=new THREE.Group(),scene=new THREE.Scene(),old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());old.material.name='Ridged maple bark';old.material.map=new THREE.Texture();model.add(old);
 const fixture=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());fixture.material.name='Honed silver granite';model.add(fixture);
 for(let i=0;i<36;i++){const part=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());part.name=`part-${i}`;trees.add(part);}
 const result=installGardenTrees(model,trees,trees.clone(),scene);assert.equal(result.trees,15);assert.equal(result.pines,6);assert.equal(old.visible,false);assert.equal(fixture.visible,true);assert.equal(scene.children[0].children.length,36);assert.equal(new Set(result.levels.map(l=>l.levels[0].object.material)).size,1);assert.equal(result.levels[0].levels[0].object.material.map,old.material.map);const camera=new THREE.PerspectiveCamera();camera.position.z=100;camera.updateMatrixWorld();result.update(camera);assert.equal(result.levels[0].getCurrentLevel(),1);camera.position.z=2;camera.updateMatrixWorld();result.update(camera);assert.equal(result.levels[0].getCurrentLevel(),0);
});
test('incomplete replacement leaves existing trees visible',()=>{
 const model=new THREE.Group(),old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());old.material.name='Ridged maple bark';model.add(old);assert.throws(()=>installGardenTrees(model,new THREE.Group(),new THREE.Group(),new THREE.Scene()),/36 tree meshes/);assert.equal(old.visible,true);
});
test('tree export retains shaped bases, UV-mapped twigs and every original planting position',()=>{
 const before=JSON.parse(fs.readFileSync(new URL('../dist/assets/garden.json',import.meta.url))),after=JSON.parse(fs.readFileSync(new URL('../dist/assets/garden-trees.json',import.meta.url)));assert.deepEqual(after.trees,before.trees);assert.equal(after.pines.length,6);assert.equal(after.anchors.length,2835);for(const a of after.anchors){assert.ok(a.every(Number.isFinite));assert.ok(a[4]>=.4&&a[4]<=.66);assert.ok(a[2]>1);}
 const b=fs.readFileSync(new URL('../dist/assets/garden-trees.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.ok(b.length<3*1024*1024);assert.equal(d.meshes.length,36);assert.equal(d.images?.length??0,0);for(const m of d.meshes)for(const p of m.primitives){assert.ok(p.attributes.NORMAL!==undefined);assert.ok(p.attributes.TEXCOORD_0!==undefined);}
});
test('distant foliage keeps the full crown extent and restores all leaves on approach',()=>{
 const app=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8'),segment=app.slice(app.indexOf('const canopyBatches=[]'),app.indexOf('function plantFerns'));
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),dummy=new THREE.Object3D(),canopyGeom=new THREE.PlaneGeometry(1,1),leafMaterials=[0,1,2].map(()=>new THREE.MeshStandardMaterial());let seed=13;const random=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296),range=(a,b)=>a+(b-a)*random();
 const f=new Function('THREE','scene','camera','dummy','canopyGeom','leafMaterials','random','range','innerWidth','canopyUniform','createWindShadows','applyCanopyWind',segment+';return {makeCanopies,updateCanopyDetail,canopyBatches};')(THREE,scene,camera,dummy,canopyGeom,leafMaterials,random,range,702,{value:0},createWindShadows,applyCanopyWind);
 const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/garden-trees.json',import.meta.url)));f.makeCanopies(layout.anchors,layout.trees);assert.equal(f.canopyBatches.length,15);camera.position.set(1000,1000,1000);f.updateCanopyDetail();
 for(const mesh of f.canopyBatches){const box=new THREE.Box3(),m=new THREE.Matrix4(),p=new THREE.Vector3();assert.ok(mesh.count<mesh.userData.fullCount);for(let i=0;i<mesh.count;i++){mesh.getMatrixAt(i,m);box.expandByPoint(p.setFromMatrixPosition(m));}assert.ok(box.getSize(p).y>mesh.boundingSphere.radius*.5);}
 const first=f.canopyBatches[0];camera.position.copy(first.boundingSphere.center);f.updateCanopyDetail();assert.equal(first.count,first.userData.fullCount);
});

test('fork charts use one shared blend shader across near/far trunks and preserve plain twigs',()=>{
 const model=new THREE.Group(),trees=new THREE.Group(),scene=new THREE.Scene(),old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());old.material.name='Ridged maple bark';old.material.map=new THREE.Texture();model.add(old);
 for(let i=0;i<36;i++){const part=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());part.name=`part-${i}`;if(i<15){const data=new Float32Array(part.geometry.attributes.position.count*3);data.fill(.25);part.geometry.setAttribute('_bark_blend',new THREE.BufferAttribute(data,3));}trees.add(part);}
 const result=installGardenTrees(model,trees,trees.clone(),scene);assert.equal(result.blendedTrunks,15);const near=result.levels[0].levels[0].object,far=result.levels[0].levels[1].object,twig=result.levels[15].levels[0].object;
 assert.equal(near.material,far.material);assert.notEqual(near.material,twig.material);assert.equal(near.material.map,old.material.map);assert.equal(near.material, result.levels[14].levels[0].object.material);assert.equal(near.geometry.getAttribute('barkBlend'),near.geometry.getAttribute('_bark_blend'));assert.ok(!trees.children[0].geometry.hasAttribute('barkBlend'));assert.notEqual(near.material.customProgramCacheKey(),twig.material.customProgramCacheKey());
});
test('both exported tree levels contain exactly 15 fork charts without extra texture payloads',()=>{
 for(const name of ['garden-trees.glb','garden-trees-distant.glb']){const b=fs.readFileSync(new URL('../dist/assets/'+name,import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));let count=0;for(const mesh of d.meshes)for(const p of mesh.primitives){if(p.attributes._BARK_BLEND!==undefined){count++;const a=d.accessors[p.attributes._BARK_BLEND];assert.equal(a.type,'VEC3');assert.equal(a.count,d.accessors[p.attributes.POSITION].count);assert.ok(p.extensions.KHR_draco_mesh_compression.attributes._BARK_BLEND!==undefined);}}assert.equal(count,15);assert.equal(d.images?.length??0,0);}
});
