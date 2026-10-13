import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {sampleKoiMotion} from '../dist/koi-motion.js';

// Read bounds from the shipped Blender export, including every fin and barbel.
const bytes=fs.readFileSync(new URL('../dist/assets/koi/koi.glb',import.meta.url));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
const rest=new THREE.Box3();
function boundsOf(i,parent=new THREE.Matrix4()){
 const n=gltf.nodes[i],m=new THREE.Matrix4();
 if(n.matrix)m.fromArray(n.matrix);
 else m.compose(new THREE.Vector3().fromArray(n.translation??[0,0,0]),new THREE.Quaternion().fromArray(n.rotation??[0,0,0,1]),new THREE.Vector3().fromArray(n.scale??[1,1,1]));
 m.premultiply(parent);
 if(n.mesh!==undefined)for(const p of gltf.meshes[n.mesh].primitives){
  const a=gltf.accessors[p.attributes.POSITION];
  rest.union(new THREE.Box3(new THREE.Vector3().fromArray(a.min),new THREE.Vector3().fromArray(a.max)).applyMatrix4(m));
 }
 for(const j of n.children??[])boundsOf(j,m);
}
for(const i of gltf.scenes[0].nodes)boundsOf(i);
const piers=[];
for(const x of [-1.04,1.04])for(let i=0;i<5;i++)piers.push([x,11.8-i*2.6]);
const pose=new THREE.Object3D(),envelope=new THREE.Box3();
function posedBounds(f,m){
 envelope.copy(rest);
 // Conservative shader envelope: all vertices can receive maximum tail bend
 // and maximum pectoral flap. Transform its eight corners after scaling.
 const bend=m.tailAmplitude+Math.abs(m.turnBend);
 const flap=(Math.max(Math.abs(rest.min.x),Math.abs(rest.max.x))-.115)**2/.0625*.035;
 envelope.min.x-=bend;envelope.max.x+=bend;
 envelope.min.y-=flap;envelope.max.y+=flap;
 pose.scale.setScalar(f.group.scale.x);pose.position.set(m.x,m.y,m.z);
 pose.rotation.set(m.pitch,m.yaw,m.roll,'YXZ');pose.updateMatrix();
 return envelope.applyMatrix4(pose.matrix);
}
test('the complete animated Blender fish envelope clears all ten bridge piers',t=>{
 let minimum=Infinity,samples=0,closest;
 // Include every radius and size extreme, with different phase and drift.
 for(let i=0;i<32;i++){
  const f={phase:i*.71,speed:.055+(i%5)*.00875,rx:i%2?8.1:3.2,rz:i%4<2?2.2:4.5,depth:-.33,drift:i*.41,group:{scale:{x:1.05}}};
  for(let time=0;time<1800;time+=.19){
   const b=posedBounds(f,sampleKoiMotion(f,time));samples++;
   for(const [x,z]of piers){
    const dx=Math.max(b.min.x-x-.105,x-.105-b.max.x,0);
    const dz=Math.max(b.min.z-z-.105,z-.105-b.max.z,0);
    const clearance=Math.hypot(dx,dz);
    if(clearance<minimum){minimum=clearance;closest={fish:i,time,pier:[x,z]};}
    assert.ok(clearance>.03,`fish ${i}, time ${time}, pier ${x},${z}, clearance ${clearance}`);
   }
  }
 }
 assert.ok(Number.isFinite(minimum));
 t.diagnostic(JSON.stringify({samples,minimumConservativeClearanceMeters:minimum,closest}));
});

test('bridge gap coordinates still match the editable Blender bridge builder',()=>{
 const source=fs.readFileSync(new URL('./build_bridge.py',import.meta.url),'utf8');
 assert.ok(source.includes("y=-11.8+j*2.6;box('Pier timber',(side*1.04"));
 assert.ok(source.includes('(.21,.21,bz(y)+.65)'));
});
