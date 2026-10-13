import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {HandwashMotion,ladleAngles,constrainLadleTarget,ladleTravel} from '../dist/handwash-motion.js';
const native=JSON.parse(fs.readFileSync(new URL('./handwash-clearance.json',import.meta.url)));
const code=fs.readFileSync(new URL('../dist/handwash.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
function fixture(){
 const button={dataset:{},classList:{add(){},remove(){}},addEventListener(){}};
 const create=new Function('THREE','HandwashMotion','ladleAngles','constrainLadleTarget','ladleTravel','document',code+';return createHandwash')(THREE,HandwashMotion,ladleAngles,constrainLadleTarget,ladleTravel,{querySelector:()=>button});
 const asset=new THREE.Group(),g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(native.vertices.flatMap(p=>p.map((v,k)=>v+native.rest[k])),3));const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial());m.userData.handwashAssembly='ladle';asset.add(m);
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(45,1,.1,100);camera.position.set(-2.95,2.65,17.55);camera.lookAt(-3.7,1.23,15.6);camera.updateMatrixWorld(true);
 const controls={enabled:true,target:new THREE.Vector3(-3.7,1.23,15.6),update(){camera.lookAt(this.target);camera.updateMatrixWorld(true);}};
 return create(asset,scene,camera,controls);
}
function check(h){h.ladle.updateMatrixWorld(true);const v=new THREE.Vector3();let minimum=Infinity;
 for(const p of native.vertices){v.fromArray(p).applyMatrix4(h.ladle.matrixWorld);
  for(const [a,b] of native.railSegments){const x=Math.max(a[0],Math.min(b[0],v.x)),d=Math.hypot(v.x-x,v.y-a[1],v.z-a[2]);minimum=Math.min(minimum,d);}
  const r=Math.hypot(v.x+3.7,v.z-15.6);if(v.y<1.34&&v.y>1.14)assert.ok(r<.535||r>.78,`ladle vertex enters stone rim: ${v.toArray()}`);
 }
 assert.ok(minimum>native.railRadius+.002,`ladle intersects bamboo rest: ${minimum}`);return minimum;
}
test('actual native cup and handle clear both rails and bowl during pickup, scoop, side pour and return',()=>{
 for(const pointer of [null,new THREE.Vector2(-1,-1),new THREE.Vector2(1,1),new THREE.Vector2(1,-1)]){
  const h=fixture();let t=0;check(h);h.take();for(let i=0;i<110;i++){t+=.01;h.update(.01,t);check(h);}if(pointer)h.move(pointer);
  for(let i=0;i<70;i++){t+=.01;h.update(.01,t);check(h);}h.click();for(let i=0;i<100;i++){t+=.01;h.update(.01,t);check(h);}h.click();for(let i=0;i<130;i++){t+=.01;h.update(.01,t);check(h);}h.putBack();for(let i=0;i<100;i++){t+=.01;h.update(.01,t);check(h);}assert.ok(h.ladle.position.distanceTo(new THREE.Vector3(...native.rest))<1e-10);assert.equal(h.held,false);
 }
});
