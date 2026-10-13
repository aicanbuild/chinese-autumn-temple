import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {createHash} from 'node:crypto';
import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/hall-contact.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {installHallContact}=new Function('THREE',source+';return {installHallContact}')(THREE);
function floor(){const root=new THREE.Group();for(const name of ['honed limestone','smoked stone border','recessed lime joint']){const material=new THREE.MeshStandardMaterial();material.name='Sanctuary floor | '+name;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([-6.1275,1.07,-3.475,6.1175,1.07,-10.725,0,1.07,-7.1],3));g.setAttribute('uv',new THREE.Float32BufferAttribute([1,4,7,10,13,16],2));root.add(new THREE.Mesh(g,material));}return root;}
test('floor contact preserves stone maps, primary UVs and geometry while mapping native XY',()=>{
 const root=floor(),before=root.children.map(o=>({material:o.material,uv:o.geometry.attributes.uv,position:o.geometry.attributes.position})),map=new THREE.Texture({width:1536,height:1024});const result=installHallContact(root,map);
 assert.equal(result.meshes.length,3);assert.equal(result.stats.intensity,.8);assert.equal(map.channel,1);assert.equal(map.flipY,true);assert.equal(map.colorSpace,THREE.NoColorSpace);
 root.children.forEach((o,k)=>{assert.equal(o.geometry.attributes.uv,before[k].uv);assert.equal(o.geometry.attributes.position,before[k].position);assert.notEqual(o.material,before[k].material);assert.equal(before[k].material.aoMap,null);assert.equal(o.material.aoMap,map);const u=o.geometry.attributes.uv1;assert.ok(Math.abs(u.getX(0))<1e-6&&Math.abs(u.getY(0))<1e-6);assert.ok(Math.abs(u.getX(1)-1)<1e-6&&Math.abs(u.getY(1)-1)<1e-6);});
});
test('floor contact uses world positions and rejects incomplete or occupied maps before edits',()=>{
 const root=floor();root.position.set(2,0,3);const map=new THREE.Texture({width:1,height:1});installHallContact(root,map);assert.ok(Math.abs(root.children[0].geometry.attributes.uv1.getX(0)-2/12.245)<1e-6);assert.ok(Math.abs(root.children[0].geometry.attributes.uv1.getY(0)+3/7.25)<1e-6);
 assert.throws(()=>installHallContact(new THREE.Group(),map),/Missing three/);assert.throws(()=>installHallContact(root,map),/already has/);
 const conflict=floor();conflict.children[2].material.aoMap=map;assert.throws(()=>installHallContact(conflict,map),/already has/);assert.equal(conflict.children[0].geometry.attributes.uv1,undefined);
});
test('baked floor contact is tied to current furnished temple geometry',{skip:'AO baseline predates removal of added Buddha hands; requires a fresh Blender bake/audit.'},()=>{
 const asset=n=>fs.readFileSync(new URL('../dist/assets/'+n,import.meta.url));const metadata=JSON.parse(asset('hall-contact-ao.json'));
 for(const [name,digest]of Object.entries(metadata.inputs))assert.equal(createHash('sha256').update(asset(name)).digest('hex'),digest,`${name} changed: rebake floor contact`);
 const png=asset('hall-contact-ao.png');assert.equal(createHash('sha256').update(png).digest('hex'),metadata.textureSha256);assert.equal(png.readUInt32BE(16),1536);assert.equal(png.readUInt32BE(20),1024);assert.equal(metadata.distance,1);assert.ok(png.length<2*1024*1024);
});
