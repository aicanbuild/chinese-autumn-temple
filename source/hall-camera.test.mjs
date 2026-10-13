import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/hall-camera.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createHallCamera,sweepHallCamera}=new Function('THREE',code+';return {createHallCamera,sweepHallCamera}')(THREE);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/hall-navigation.json',import.meta.url)));
const v=(x,y,z)=>new THREE.Vector3(x,y,z),box=(min,max)=>new THREE.Box3(v(...min),v(...max));
function setup(){const camera=new THREE.PerspectiveCamera(66,16/9,.09,420);camera.position.set(.08,2.72,-4.02);const controls={target:v(0,2.9,-8.35)},hall=createHallCamera(camera,controls,()=>1.07);hall.setLayout(layout);hall.constrain();return {camera,controls,hall};}
test('swept camera cannot tunnel through a thin object during a fast zoom',()=>{
 const obstacle=box([-1,1,-7.02],[1,3,-7]).expandByScalar(.16);
 const result=sweepHallCamera(v(0,2,-4),v(0,2,-30),[obstacle]);assert.ok(result.z> -6.84&&result.z< -6.83);assert.ok(!obstacle.containsPoint(result));
});
test('oblique dragging retains tangential movement along a contacted surface',()=>{
 const obstacle=box([-2,1,-8],[2,3,-7]).expandByScalar(.16),result=sweepHallCamera(v(-3,2,-4),v(3,2,-9),[obstacle]);
 assert.ok(result.x>2.9);assert.ok(result.z> -6.84);assert.ok(!obstacle.containsPoint(result));
});
test('overlapping obstacles and a restored camera inside a proxy recover to free space',()=>{
 const obstacles=[box([-1,1,-8],[1,3,-6]),box([.8,1,-8],[2,3,-6])];
 const result=sweepHallCamera(v(0,2,-7),v(0,2,-7),obstacles);assert.ok(obstacles.every(b=>!b.containsPoint(result)));
});
test('authored bounds are tight enough to inspect vases, incense and both mural bays',()=>{
 assert.ok(layout.sourceUnchanged);assert.equal(layout.boxes.filter(b=>b.name!=='wooden-fish-stand').length,26);
 const stand=layout.boxes.find(b=>b.name==='wooden-fish-stand');assert.ok(stand);assert.ok(stand.max[0]-stand.min[0]<.7);assert.ok(stand.max[2]-stand.min[2]<.6);
 const instrument=box(stand.min,stand.max).expandByScalar(.16),x=(stand.min[0]+stand.max[0])/2;assert.ok(sweepHallCamera(v(x,1.92,-4),v(x,1.92,-8),[instrument]).z>stand.max[2]+.159);
 const vessel=layout.boxes.find(b=>b.name==='incense-vessel');assert.ok(vessel.max[0]-vessel.min[0]<1.4);
 for(const name of ['left-vase','right-vase']){const b=layout.boxes.find(b=>b.name===name);assert.ok(b.max[0]-b.min[0]<.5);}
 const {camera,controls,hall}=setup();
 for(const sign of [-1,1]){hall.reset();camera.position.set(sign*4.4,2.8,-7.5);controls.target.set(sign*5.15,2.8,-7.87);hall.constrain();assert.ok(Math.abs(camera.position.x-sign*4.4)<.001);assert.ok(Math.abs(controls.target.x-sign*5.15)<.001);}
});
test('thousands of pan and zoom requests stay outside furniture and retain correct aim',()=>{
 const {camera,controls,hall}=setup(),radius=.09*Math.sqrt(1+Math.tan(66*Math.PI/360)**2*(1+(16/9)**2))+.015;
 const obstacles=layout.boxes.map(b=>box(b.min,b.max).expandByScalar(radius));let seed=21934;const random=()=>((seed=Math.imul(seed,1664525)+1013904223|0)>>>0)/4294967296;
 for(let i=0;i<3000;i++){
  camera.position.add(v((random()-.5)*8,(random()-.5)*4,(random()-.5)*8));
  if(i%3===0)controls.target.add(v((random()-.5)*3,(random()-.5)*2,(random()-.5)*3));
  hall.constrain();assert.ok(camera.position.y>=1.92-1e-8);assert.ok(camera.position.y<=4+1e-8);assert.ok(camera.position.x>=-5.08&&camera.position.x<=5.08);assert.ok(camera.position.z>=-9.95&&camera.position.z<=-4.02);
  assert.ok(obstacles.every(b=>!b.containsPoint(camera.position)),JSON.stringify({i,position:camera.position.toArray(),hits:layout.boxes.filter((_,j)=>obstacles[j].containsPoint(camera.position)).map(b=>b.name)}));
  const direction=camera.getWorldDirection(v(0,0,0)),expected=controls.target.clone().sub(camera.position).normalize();assert.ok(direction.dot(expected)>.999999);
 }
 assert.ok(hall.stats.contacts>0);
});
test('very wide viewports receive extra near-plane clearance',()=>{
 const {camera,controls,hall}=setup();camera.aspect=3.5;camera.updateProjectionMatrix();camera.position.set(100,8,-7);controls.target.set(5.15,5.6,-7);hall.constrain();assert.ok(camera.position.x<5.05);assert.ok(camera.position.y<4);
});
test('all four opaque door leaves block a fast camera move while the central entry stays open',()=>{
 const leaves=layout.boxes.filter(b=>b.name.startsWith('door-leaf-'));assert.equal(leaves.length,4);
 const obstacles=leaves.map(b=>box(b.min,b.max).expandByScalar(.16));
 for(const leaf of leaves){const x=(leaf.min[0]+leaf.max[0])/2,result=sweepHallCamera(v(x,2.7,-8),v(x,2.7,-4),obstacles);assert.ok(result.z<leaf.min[2]-.159);}
 const entry=sweepHallCamera(v(0,2.7,-8),v(0,2.7,-4),obstacles);assert.equal(entry.z,-4);
});
