import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {sampleKoiMotion} from '../dist/koi-motion.js';
const read=name=>{const b=fs.readFileSync(new URL('../dist/assets/'+name,import.meta.url));return {bytes:b.length,doc:JSON.parse(b.subarray(20,20+b.readUInt32LE(12)))};};
const basin=read('pond-basin.glb'),meta=JSON.parse(fs.readFileSync(new URL('../dist/assets/pond-basin.json',import.meta.url)));
const code=fs.readFileSync(new URL('../dist/pond-basin.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const installPondBasin=new Function('THREE',code+';return installPondBasin;')(THREE);
test('the exported basin has real depth, surface normals and UVs without duplicate texture downloads',()=>{
 assert.ok(basin.bytes<100000);assert.equal(basin.doc.meshes.length,1);assert.equal((basin.doc.images??[]).length,0);
 const p=basin.doc.meshes[0].primitives[0],a=basin.doc.accessors[p.attributes.POSITION];
 assert.ok(a.max[1]<=-.9799);assert.ok(a.min[1]<-1.8);assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);
 assert.equal(basin.doc.accessors[p.indices].count/3,18816);assert.equal(meta.stones,157);
 const stones=JSON.parse(fs.readFileSync(new URL('../dist/assets/pond-stones.json',import.meta.url)));
 assert.equal(stones.placements.filter(p=>p[8]==='bed'&&p[3]<-.9).length,517);
});
test('basin installation keeps the original sediment material and other architecture intact',()=>{
 const model=new THREE.Group(),asset=new THREE.Group(),material=new THREE.MeshStandardMaterial();material.name='Riverbed sediment';
 const original=new THREE.Mesh(new THREE.PlaneGeometry(),material),other=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());model.add(original,other);original.position.set(2,0,1);
 const source=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.MeshStandardMaterial());source.rotation.x=-Math.PI/2;source.position.set(0,-1.5,5.8);asset.add(source);
 const untouched=other.geometry;installPondBasin(model,asset);model.updateMatrixWorld(true);
 assert.equal(original.material,material);assert.equal(other.geometry,untouched);assert.equal(model.children.length,2);assert.equal(original.userData.waterSide,'below');
 const world=new THREE.Box3().setFromObject(original);assert.ok(Math.abs(world.min.y+1.5)<1e-7);assert.ok(Math.abs(world.getCenter(new THREE.Vector3()).z-5.8)<1e-7);
});
test('the entire animated fish envelope remains above the local sloping basin',t=>{
 const d=read('koi/koi.glb').doc,parts=[];
 function visit(i,parent=new THREE.Matrix4()){
  const n=d.nodes[i],m=new THREE.Matrix4();
  if(n.matrix)m.fromArray(n.matrix);else m.compose(new THREE.Vector3().fromArray(n.translation??[0,0,0]),new THREE.Quaternion().fromArray(n.rotation??[0,0,0,1]),new THREE.Vector3().fromArray(n.scale??[1,1,1]));m.premultiply(parent);
  if(n.mesh!==undefined)for(const p of d.meshes[n.mesh].primitives){const a=d.accessors[p.attributes.POSITION];parts.push(new THREE.Box3(new THREE.Vector3().fromArray(a.min),new THREE.Vector3().fromArray(a.max)).applyMatrix4(m));}
  for(const child of n.children??[])visit(child,m);
 }
 for(const i of d.scenes[0].nodes)visit(i);
 const unique=[...new Map(parts.map(b=>[JSON.stringify(b),b])).values()];
 const pose=new THREE.Object3D(),bounds=new THREE.Box3();let minimum=Infinity;
 for(let i=0;i<32;i++)for(let time=0;time<1800;time+=.37){
  const f={phase:i*.71,speed:.055+(i%5)*.00875,rx:i%2?8.1:3.2,rz:i%4<2?2.2:4.5,depth:-.58,drift:i*.41,group:{scale:{x:1.05}}},m=sampleKoiMotion(f,time);
  pose.position.set(m.x,m.y,m.z);pose.rotation.set(m.pitch,m.yaw,m.roll,'YXZ');pose.scale.setScalar(1.05);pose.updateMatrix();
  for(const rest of unique){
  bounds.copy(rest);const bend=(m.tailAmplitude+Math.abs(m.turnBend))*Math.max(0,Math.min(1,(.40-rest.min.z)/1.40))**2,flap=(Math.max(Math.abs(rest.min.x),Math.abs(rest.max.x))-.115)**2/.0625*.035;
  bounds.min.x-=bend;bounds.max.x+=bend;bounds.min.y-=flap;bounds.max.y+=flap;
  bounds.applyMatrix4(pose.matrix);
  // Bound the highest sediment anywhere under the entire deformed fish AABB.
  // The radial base is monotone; +22mm bounds all small undulations, with
  // another 2mm allowance for the triangulated surface and export precision.
  let radius=0;
  for(const x of [bounds.min.x,bounds.max.x])for(const z of [bounds.min.z,bounds.max.z])radius=Math.max(radius,Math.hypot(x/11.5,(z-5.8)/6.9)/.985);
  const u=Math.max(0,Math.min(1,(radius-.28)/.72));
  const bedUpper=-.98-.58*(1-u*u*(3-2*u))+.024;
  const clearance=bounds.min.y-bedUpper;
  minimum=Math.min(minimum,clearance);
  assert.ok(clearance>.02,JSON.stringify({i,time,clearance,fishBottom:bounds.min.y,bedUpper,radius}));
 }
 }
 t.diagnostic(JSON.stringify({minimumConservativeBedClearanceMeters:minimum,partBounds:unique.length}));
});
