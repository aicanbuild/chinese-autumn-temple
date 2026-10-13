import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {sampleKoiMotion} from '../dist/koi-motion.js';
import {applyKoiReaction} from '../dist/koi-reaction.js';
const threeURL=new URL('../dist/vendor/three/three.module.js',import.meta.url).href;
const utility=fs.readFileSync(new URL('../dist/vendor/three/addons/utils/BufferGeometryUtils.js',import.meta.url),'utf8').replace("from 'three'",`from '${threeURL}'`);
const {mergeGeometries}=await import('data:text/javascript;base64,'+Buffer.from(utility).toString('base64'));
const source=fs.readFileSync(new URL('../dist/koi.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createKoi,updateKoi}=new Function('THREE','mergeGeometries','sampleKoiMotion','applyKoiReaction',`${source};return {createKoi,updateKoi};`)(THREE,mergeGeometries,sampleKoiMotion,applyKoiReaction);
test('batching preserves 16 independent fish and all supplied body/fin triangles',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene();let expectedTriangles=0;
 for(const kind of ['kohaku','sanke','yamabuki','platinum']){
  const variant=new THREE.Group();variant.name='Koi_'+kind;
  for(const [name,geometry]of [['Body',new THREE.SphereGeometry(.15,24,12)],['Pectoral',new THREE.PlaneGeometry(.2,.1,6,4)]]){
   const material=new THREE.MeshStandardMaterial();material.name=name;
   const mesh=new THREE.Mesh(geometry,material);mesh.name=name;variant.add(mesh);expectedTriangles+=geometry.index.count/3*4;
  }
  root.add(variant);
 }
 const fish=createKoi(root,scene,()=>.5);assert.equal(fish.length,16);
 assert.equal(scene.children.length,8,'two render batches per skin, not per fish');
 let actualTriangles=0;for(const mesh of scene.children){assert.ok(mesh.isInstancedMesh);assert.equal(mesh.count,4);actualTriangles+=mesh.geometry.index.count/3*mesh.count;assert.equal(new Set([0,1,2,3].map(i=>mesh.geometry.attributes.koiMotion.getX(i))).size,4);}
 assert.equal(actualTriangles,expectedTriangles);
 const before=fish[0].group.position.clone();updateKoi(fish,12);assert.ok(before.distanceTo(fish[0].group.position)>1);
 const batch=scene.children[0],a=new THREE.Matrix4(),b=new THREE.Matrix4();batch.getMatrixAt(0,a);batch.getMatrixAt(1,b);assert.notDeepEqual(a.elements,b.elements);
 const stored=new THREE.Matrix4();fish[0].meshes[0].getMatrixAt(fish[0].index,stored);assert.ok(new THREE.Vector3().setFromMatrixPosition(stored).distanceTo(fish[0].group.position)<1e-5);
});
