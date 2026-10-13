import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const streamCode=fs.readFileSync(new URL('../dist/temple-stream.js',import.meta.url),'utf8');
const streamCore=streamCode.slice(streamCode.indexOf('export const STREAM_START'),streamCode.indexOf('export function installTempleStream')).replaceAll('export ','');
const {streamContains}=new Function(streamCore+';return {streamContains};')();
import * as THREE from '../dist/vendor/three/three.module.js';
const read=name=>fs.readFileSync(new URL('../dist/'+name,import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {supportHeight,collectSupportVertices,advanceSweptLeaf}=new Function('THREE',read('sweep-motion.js')+';return {supportHeight,collectSupportVertices,advanceSweptLeaf}')(THREE);
const {createFallenLeafGeometry}=new Function('THREE',read('leaf-surfaces.js')+';return {createFallenLeafGeometry}')(THREE);
const {setLeafRotation}=new Function('THREE',read('leaf-settling.js')+';return {setLeafRotation}')(THREE);
const app=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8');
const surfaceAt=new Function('gardenGround','streamContains','handwash',app.slice(app.indexOf('function poolAt('),app.indexOf('function spawnLeaf('))+';return surfaceAt')(null,streamContains,null);
function assertContact(p,rotation,size,x,z,surface){
 const height=supportHeight(p,rotation,size,x,z,surface),matrix=new THREE.Matrix4().makeRotationFromEuler(rotation),v=new THREE.Vector3();let min=Infinity;
 for(let i=0;i<p.count;i++){
  v.fromBufferAttribute(p,i).multiplyScalar(size).applyMatrix4(matrix);const floor=surface(x+v.x,z+v.z);const gap=height+v.y-floor;
  assert.ok(gap>=.002-1e-7,`vertex ${i} penetrated its support: ${gap}`);min=Math.min(min,gap);
 }
 assert.ok(Math.abs(min-.002)<1e-7,'at least one vertex makes contact');
}
test('curled swept leaves touch actual board heights, edges and stone floor at every sampled pose and size',()=>{
 for(let kind=0;kind<2;kind++)for(let variant=0;variant<3;variant++){
  const p=createFallenLeafGeometry(kind,variant).attributes.position;
  for(let i=0;i<35;i++){
   const r=new THREE.Euler(-Math.PI/2+Math.sin(i)*.4,Math.cos(i)*.25,i*.31),size=.205*(1-i/36);
   for(const [x,z]of[[0,12.4-i*.3],[1.19,5.6],[-.1,-6],[1.45,12.55],[4,5]])assertContact(p,r,size,x,z,surfaceAt);
  }
 }
});
test('actual broom mesh supports every bristle during tilt across bridge boards and entrance step',()=>{
 const section=app.slice(app.indexOf('const broom=new THREE.Group()'),app.indexOf('const broomHit='));
 let n=1;const range=(a,b)=>{n=(n*16807)%2147483647;return a+(b-a)*(n/2147483647);};
 const broom=new Function('THREE','scene','worldUp','range',section+';return broom')(THREE,new THREE.Scene(),new THREE.Vector3(0,1,0),range);
 const p=collectSupportVertices(broom);assert.ok(p.count>2000);
 for(let i=0;i<50;i++)for(const [x,z]of[[0,12.5],[1.18,5.75],[0,-3.48],[0,-6]])assertContact(p,new THREE.Euler(.3,i*.15,Math.sin(i*.2)*.2),1,x,z,surfaceAt);
 // The collector must preserve child transforms and exclude the root's world pose.
 broom.position.set(2,3,5);broom.rotation.set(.1,.7,-.2);const moved=collectSupportVertices(broom);
 for(let i=0;i<p.array.length;i++)assert.ok(Math.abs(p.array[i]-moved.array[i])<1e-6);
});
test('a swept leaf retains its current settled or settling pose exactly on pickup',()=>{
 for(const landedAt of [-Infinity,9.7])for(let i=0;i<20;i++){
  const l={state:'rest',landedAt,contactTilt:i*.32,rot:i*.27},before=new THREE.Euler(),after=new THREE.Euler();setLeafRotation(l,10,before);
  l.sweepPose=[before.x,before.y,before.z];l.sweepSpin=2.3;l.life=0;l.state='swept';setLeafRotation(l,10,after);
  for(const axis of ['x','y','z'])assert.ok(after[axis]===before[axis]);
  l.life=.8;setLeafRotation(l,10.8,after);assert.ok(Math.abs(after.x-before.x)<.045);assert.ok(Math.abs(after.y-before.y)<.028);
 }
});
test('free flight drag and gravity have the same result at 30, 60 and 144 Hz',()=>{
 const simulate=steps=>{const l={x:1,y:2,z:3,vx:2.8,vy:.3,vz:-1.7,life:0};for(let i=0;i<steps;i++)advanceSweptLeaf(l,.6/steps);return l;};
 const exact=simulate(1);for(const steps of[18,36,86]){const result=simulate(steps);for(const key of Object.keys(exact))assert.ok(Math.abs(exact[key]-result[key])<1e-12,key);}
});
test('hall contact height matches the exported stone floor throughout its bounds',()=>{
 const floor=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary-floor.json',import.meta.url),'utf8'));
 const [left,right,front,back]=floor.boundsNative;
 for(let i=0;i<=10;i++)for(let j=0;j<=10;j++)assert.equal(surfaceAt(left+(right-left)*i/10,-front-(back-front)*j/10),floor.topMeters);
});
