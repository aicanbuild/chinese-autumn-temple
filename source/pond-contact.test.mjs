import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {createHash} from 'node:crypto';
import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/pond-contact.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installPondContact}=new Function('THREE',source+';return {installPondContact}')(THREE);
test('native XY atlas maps to Three XZ without changing photographic UVs or geometry',()=>{
 const root=new THREE.Group(),geometry=new THREE.BufferGeometry(),material=new THREE.MeshStandardMaterial();material.name='Riverbed sediment';
 geometry.setAttribute('position',new THREE.Float32BufferAttribute([-11.5,-1,12.7,11.5,-1,-1.1,0,-1,5.8],3));const uv=new THREE.Float32BufferAttribute([2,4,6,8,10,12],2);geometry.setAttribute('uv',uv);const mesh=new THREE.Mesh(geometry,material);root.add(mesh);
 const map=new THREE.Texture({width:2560,height:1536});const result=installPondContact(root,map);assert.equal(result.bed,mesh);assert.equal(mesh.geometry,geometry);assert.equal(geometry.attributes.uv,uv);
 const actual=geometry.attributes.uv1.array,expected=[0,0,1,1,.5,.5];for(let i=0;i<6;i++)assert.ok(Math.abs(actual[i]-expected[i])<1e-6);
 assert.equal(map.flipY,true);assert.equal(map.channel,1);assert.equal(map.colorSpace,THREE.NoColorSpace);assert.equal(map.wrapS,THREE.ClampToEdgeWrapping);assert.notEqual(mesh.material,material);assert.equal(material.aoMap,null);assert.equal(mesh.material.aoMap,map);
});
test('world placement, not mesh local origin, locates baked contact',()=>{
 const root=new THREE.Group(),material=new THREE.MeshStandardMaterial();material.name='Riverbed sediment';root.position.set(2,0,3);const mesh=new THREE.Mesh(new THREE.PlaneGeometry(1,1),material);mesh.position.set(-2,0,2.8);root.add(mesh);const map=new THREE.Texture({width:1,height:1});installPondContact(root,map);
 const p=mesh.geometry.attributes.position,u=mesh.geometry.attributes.uv1;
 for(let i=0;i<p.count;i++){assert.ok(Math.abs(u.getX(i)-(p.getX(i)+11.5)/23)<1e-6);assert.ok(Math.abs(u.getY(i)-.5)<1e-6);}
});
test('missing bed or pre-existing occlusion map is rejected rather than silently overwritten',()=>{
 const root=new THREE.Group();assert.throws(()=>installPondContact(root,new THREE.Texture()),/Missing sediment/);
 const m=new THREE.MeshStandardMaterial();m.name='Riverbed sediment';m.aoMap=new THREE.Texture();root.add(new THREE.Mesh(new THREE.BoxGeometry(),m));assert.throws(()=>installPondContact(root,new THREE.Texture()),/already has/);
});
test('baked atlas remains aligned with the shipped fixed geometry and layout',()=>{
 const asset=name=>fs.readFileSync(new URL('../dist/assets/'+name,import.meta.url));const meta=JSON.parse(asset('pond-contact-ao.json'));
 for(const [name,digest] of Object.entries(meta.inputs))assert.equal(createHash('sha256').update(asset(name)).digest('hex'),digest,`${name} changed: rebake and audit contact atlas`);
 const png=asset('pond-contact-ao.png');assert.equal(createHash('sha256').update(png).digest('hex'),meta.textureSha256);assert.equal(png.readUInt32BE(16),2560);assert.equal(png.readUInt32BE(20),1536);assert.ok(png.length<2*1024*1024);assert.equal(meta.stones,517);
});
