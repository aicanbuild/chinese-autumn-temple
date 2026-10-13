import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';import {installDoorBacks} from '../dist/door-backs.js';
test('door lining export has four reusable material batches and no duplicate textures',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/door-backs.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.ok(b.length<2*1024*1024);assert.equal(d.meshes.length,4);assert.equal((d.materials??[]).length,0);assert.equal((d.images??[]).length,0);
 assert.deepEqual(new Set(d.nodes.filter(n=>n.mesh!==undefined).map(n=>n.extras.sourceMaterial)),new Set(['Sanctuary | oxblood lacquer','Sanctuary | carved rosewood','Sanctuary | hand burnished gold','Sanctuary | antique gilt bronze']));
 let triangles=0;for(const m of d.meshes)for(const p of m.primitives){triangles+=d.accessors[p.indices].count/3;assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);}
 assert.ok(triangles>100000&&triangles<300000);
});
test('door linings share actual finished sanctuary materials without changing them',()=>{
 const scene=new T.Scene(),sanctuary=new T.Group(),asset=new T.Group(),materials=[];
 for(let i=0;i<4;i++){const m=new T.MeshPhysicalMaterial({clearcoat:.3});m.name='original '+i;m.normalMap=new T.Texture();materials.push(m);sanctuary.add(new T.Mesh(new T.BoxGeometry(),m));const n=new T.Mesh(new T.BoxGeometry());n.userData.sourceMaterial=m.name;n.position.set(i,2,-5.2);asset.add(n);}
 const geometries=asset.children.map(o=>o.geometry);assert.equal(installDoorBacks(asset,sanctuary,scene).batches,4);
 asset.children.forEach((o,i)=>{assert.equal(o.material,materials[i]);assert.equal(o.geometry,geometries[i]);assert.equal(o.material.clearcoat,.3);assert.ok(o.material.normalMap);assert.equal(o.castShadow,true);assert.equal(o.receiveShadow,true);assert.equal(o.userData.waterSide,'above');assert.equal(o.userData.waterClipStatic,true);assert.deepEqual(o.position.toArray(),[i,2,-5.2]);});
});
