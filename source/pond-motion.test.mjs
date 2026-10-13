import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {POND_CURRENT} from '../dist/water-current.js';
const code=fs.readFileSync(new URL('../dist/pond-motion.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const {createPondMotion,advanceFloatingLeaf,impactWaterFragment,impactWaterVertex,createPondGeometry,sampleImpactHeight,CLICK_RIPPLE_CAPACITY,RIPPLE_CAPACITY,RIPPLE_LIFETIME}=new Function('THREE','POND_CURRENT',code+';return {createPondMotion,advanceFloatingLeaf,impactWaterFragment,impactWaterVertex,createPondGeometry,sampleImpactHeight,CLICK_RIPPLE_CAPACITY,RIPPLE_CAPACITY,RIPPLE_LIFETIME};')(THREE,POND_CURRENT);
const surface=(x,z)=>Math.abs(x)<1.2&&z>-.92&&z<12.5?.7:(x/11.5)**2+((z-5.8)/6.9)**2<.97?-.005:.4;
test('floating leaves drift slowly while staying off the bank and bridge through ten minutes of current',()=>{
 for(const [x,z] of [[2,5],[10.9,5.8],[-5,11],[-1.21,6],[4,.5]]){
  const l={x,z,rot:0,id:41};let travel=0;
  for(let i=0;i<6000;i++){const px=l.x,pz=l.z;advanceFloatingLeaf(l,.1,i*.1,surface);assert.ok(surface(l.x,l.z)<0);const step=Math.hypot(l.x-px,l.z-pz);assert.ok(step<.014);travel+=step;}
  assert.ok(travel>.15);
 }
});
test('float drift is consistent at 30 and 60 FPS and leaves pause when time does not advance',()=>{
 const a={x:4,z:6,rot:0,id:1},b={...a};advanceFloatingLeaf(a,0,0,surface);assert.deepEqual(a,b);
 for(let i=0;i<1800;i++)advanceFloatingLeaf(a,1/30,i/30,surface);
 for(let i=0;i<3600;i++)advanceFloatingLeaf(b,1/60,i/60,surface);
 assert.ok(Math.hypot(a.x-b.x,a.z-b.z)<.001);assert.ok(Math.abs(a.rot-b.rot)<.001);
});
test('impact pool expires and reuses a bounded set while glints track the real sun',()=>{
 const material={uniforms:{}},sun=new THREE.DirectionalLight('#ffe7c2',5.2);sun.position.set(-24,21,10);sun.target.position.set(0,0,-1);const motion=createPondMotion(material,sun);
 assert.equal(motion.stats.active,0);motion.impact(3,4,1,.15);motion.update(1);assert.equal(motion.stats.active,1);
 motion.update(1+RIPPLE_LIFETIME);assert.equal(motion.stats.active,0);
 for(let i=0;i<40;i++)motion.impact(3,i,8,.2);motion.update(8);assert.equal(motion.stats.active,RIPPLE_CAPACITY-CLICK_RIPPLE_CAPACITY);assert.equal(motion.events.length,RIPPLE_CAPACITY);
 assert.ok(material.uniforms.waterSunDirection.value.equals(sun.position.clone().sub(sun.target.position).normalize()));sun.position.set(1,8,2);motion.update(9);assert.ok(material.uniforms.waterSunDirection.value.equals(sun.position.clone().sub(sun.target.position).normalize()));
});

test('click waves propagate outwards, contain multiple crests, and settle without an abrupt cutoff',()=>{
 const strength=.075;
 assert.equal(sampleImpactHeight(0,0,strength),0);assert.ok(sampleImpactHeight(0,.035,strength)<-.025,'initial surface depression');
 for(const age of [1,2,3]){
  const radius=.08+age*1.4;assert.ok(sampleImpactHeight(radius,age,strength)>.005);
  assert.ok(sampleImpactHeight(radius-Math.PI/11.5,age,strength)<0,'trough behind the advancing crest');
  assert.ok(sampleImpactHeight(radius-2*Math.PI/11.5,age,strength)>0,'following crest');
 }
 assert.ok(Math.abs(sampleImpactHeight(.08+5*1.4,5,strength))<sampleImpactHeight(1.48,1,strength));
 assert.equal(sampleImpactHeight(2,RIPPLE_LIFETIME,strength),0);assert.ok(Math.abs(sampleImpactHeight(9,RIPPLE_LIFETIME-.001,strength))<1e-7);
});
test('falling leaves cannot erase clicked wave trains, and surface samples remain on the pond',()=>{
 const m=createPondMotion({uniforms:{}},new THREE.DirectionalLight());m.disturb(3,5,0);
 const first=m.events[0].clone();for(let i=0;i<80;i++)m.impact(i/10,5,.1,.15);
 assert.ok(m.events[0].equals(first));assert.ok(Math.abs(m.heightAt(4.48,5,1))>.005);
 assert.equal(m.heightAt(20,5,1),0);assert.equal(m.heightAt(0,12.68,1),0);assert.equal(m.heightAt(4,5,8),0);
});
test('pond is a fine indexed ellipse with world-scale UVs for real displaced crests',()=>{
 const g=createPondGeometry(),p=g.attributes.position,uv=g.attributes.uv;
 assert.ok(p.count>20000&&p.count<30000);assert.ok(g.index.count>120000);assert.ok(g.index.count<150000);
 for(let i=0;i<p.count;i++){assert.ok((p.getX(i)/11.48)**2+(p.getY(i)/6.88)**2<1.000001);assert.equal(uv.getX(i),p.getX(i));assert.equal(uv.getY(i),p.getY(i));assert.equal(p.getZ(i),0);}
 const vertex=impactWaterVertex('#include <common>\nvoid main(){vec4 worldPosition=modelMatrix*vec4(position,1.);vToEye = cameraPosition - worldPosition.xyz;}');
 assert.ok(vertex.includes('worldPosition.y+=pondImpactField(worldPosition.xz).x'));
});
