import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const read=n=>fs.readFileSync(new URL('../dist/'+n,import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createGroundSurface}=new Function('THREE',read('ground-surface.js')+';return {createGroundSurface}')(THREE);
const {supportHeight}=new Function('THREE',read('sweep-motion.js')+';return {supportHeight}')(THREE);
test('ground sampler matches actual sloped transformed triangles and retains negative terrain',()=>{
 const root=new THREE.Group(),geometry=new THREE.PlaneGeometry(4,4,2,2);geometry.rotateX(-Math.PI/2);for(let i=0;i<geometry.attributes.position.count;i++)geometry.attributes.position.setY(i,geometry.attributes.position.getX(i)*.2-.3);geometry.computeVertexNormals();root.add(new THREE.Mesh(geometry));root.position.set(3,.05,2);
 const surface=createGroundSurface([{root}]),ray=new THREE.Raycaster(new THREE.Vector3(),new THREE.Vector3(0,-1,0));
 for(let x=1.1;x<4.9;x+=.23)for(let z=.1;z<3.9;z+=.27){ray.ray.origin.set(x,3,z);const hit=ray.intersectObject(root,true)[0];assert.ok(Math.abs(surface.heightAt(x,z)-hit.point.y)<1e-7);}
 assert.ok(surface.heightAt(2,2)<0);assert.equal(surface.heightAt(10,10),null);assert.equal(surface.heightAt(18,0),null);
});
test('overlapping paving wins above soil, while vertical sides and high roofs are excluded',()=>{
 const soil=new THREE.Mesh(new THREE.PlaneGeometry(8,8).rotateX(-Math.PI/2));soil.position.y=.1;
 const model=new THREE.Group(),paving=new THREE.Mesh(new THREE.BoxGeometry(1,.2,1)),roof=new THREE.Mesh(new THREE.BoxGeometry(5,.2,5));paving.position.y=.3;roof.position.y=3;model.add(paving,roof);
 const sampler=createGroundSurface([{root:soil},{root:model,maxHeight:1.5}]);assert.ok(Math.abs(sampler.heightAt(0,0)-.4)<1e-7);assert.ok(Math.abs(sampler.heightAt(.6,0)-.1)<1e-7);assert.equal(sampler.stats.triangles,4);
});
test('support contact preserves below-zero dry ground and the highest point of a sloped footprint',()=>{
 const p=new THREE.Float32BufferAttribute([-.1,0,0,.1,0,0,0,0,.1],3),surface=(x,z)=>-.2+x*.2;
 const height=supportHeight(p,new THREE.Euler(),1,0,0,surface);assert.ok(Math.abs(height-(-.178))<1e-7);
 for(let i=0;i<p.count;i++)assert.ok(height+p.getY(i)>=surface(p.getX(i),p.getZ(i))+.002-1e-7);
});
