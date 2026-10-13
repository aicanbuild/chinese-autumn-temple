import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {IncenseCycle,BURN_SECONDS,REPLACE_SECONDS} from '../dist/ritual-state.js';
test('incense burns gradually, replaces once, and new incense waits unlit',()=>{
 const c=new IncenseCycle();assert.equal(c.phase,'ready');assert.equal(c.remaining,1);
 assert.ok(c.light());assert.equal(c.light(),false);c.update(BURN_SECONDS/2);assert.equal(c.remaining,.5);
 c.update(BURN_SECONDS/2);assert.equal(c.phase,'replacing');assert.equal(c.completed,1);assert.equal(c.light(),false);
 c.update(REPLACE_SECONDS);assert.equal(c.phase,'ready');assert.equal(c.remaining,1);c.update(600);assert.equal(c.phase,'ready');assert.equal(c.completed,1);
 assert.ok(c.light());c.update(BURN_SECONDS+REPLACE_SECONDS+.2);assert.equal(c.completed,2);assert.equal(c.phase,'ready');
});
const source=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extract=new Function('THREE',source.slice(source.indexOf('export function extractRegion'),source.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(THREE);
test('bell separation respects transforms and preserves every triangle and attribute',()=>{
 const root=new THREE.Group(),g=new THREE.BoxGeometry(1,1,1),m=new THREE.Mesh(g,new THREE.MeshStandardMaterial());m.material.name='gold';m.position.set(-9,2,-4);root.add(m);
 const triangles=g.index.count/3;const part=extract(root,n=>n==='gold',p=>p.y>2);
 assert.equal(part.children.length,1);const piece=part.children[0];assert.equal(piece.geometry.attributes.position.count/3+g.index.count/3,triangles);
 assert.ok(piece.geometry.attributes.normal);assert.ok(piece.geometry.attributes.uv);
 piece.geometry.computeBoundingBox();assert.ok(piece.geometry.boundingBox.min.x<-8.5);
 const other=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());root.add(other);const before=other.geometry.index.count;
 extract(root,n=>n==='gold',p=>p.x>0);assert.equal(other.geometry.index.count,before);
});
test('removed faces no longer widen the surviving mesh bounds, and UVs remain attached',()=>{
 const root=new THREE.Group(),geometry=new THREE.BufferGeometry(),material=new THREE.MeshStandardMaterial();material.name='gold';
 geometry.setAttribute('position',new THREE.Float32BufferAttribute([0,-4,0,1,-4,0,0,-3,0,0,3,0,1,3,0,0,4,0],3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,1,0,0,1,.2,.3,.4,.5,.6,.7],2));geometry.setIndex([0,1,2,3,4,5]);root.add(new THREE.Mesh(geometry,material));
 const piece=extract(root,()=>true,p=>p.y<0);assert.equal(piece.children[0].geometry.attributes.position.count,3);assert.equal(geometry.attributes.position.count,3);assert.equal(geometry.boundingBox.min.y,3);assert.ok(geometry.boundingSphere.center.y>3);assert.ok(Math.abs(geometry.attributes.uv.getX(0)-.2)<1e-6);assert.ok(Math.abs(geometry.attributes.uv.getY(2)-.7)<1e-6);
});
