import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const read=name=>fs.readFileSync(new URL('../dist/'+name,import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createFallenLeafGeometry}=new Function('THREE',read('leaf-surfaces.js')+';return {createFallenLeafGeometry}')(THREE);
const {lowestLeafPoint,setLeafRotation,leafInstanceColor}=new Function('THREE',read('leaf-settling.js')+';return {lowestLeafPoint,setLeafRotation,leafInstanceColor}')(THREE);
test('all six leaf shapes have distinct curvature, valid triangles and a physical zero support plane',()=>{
 const shapes=[];for(let kind=0;kind<2;kind++)for(let variant=0;variant<3;variant++){
  const g=createFallenLeafGeometry(kind,variant),p=g.attributes.position;assert.ok(g.index.count/3<=180);assert.equal(g.boundingBox.min.z,0);assert.ok(g.boundingBox.max.z<.2);const a=new THREE.Vector3(),b=a.clone(),c=a.clone();
  for(let j=0;j<g.index.count;j+=3){a.fromBufferAttribute(p,g.index.getX(j));b.fromBufferAttribute(p,g.index.getX(j+1));c.fromBufferAttribute(p,g.index.getX(j+2));assert.ok(b.sub(a).cross(c.sub(a)).length()>1e-9);}
  for(const x of g.attributes.normal.array)assert.ok(Number.isFinite(x));for(const x of g.attributes.uv.array)assert.ok(x>=0&&x<=1);shapes.push([...p.array].join(','));
 }
 assert.equal(new Set(shapes).size,6);
});
test('selective curl refinement remains a connected disk with one boundary and no hanging edges',()=>{
 for(let kind=0;kind<2;kind++)for(let variant=0;variant<3;variant++){
  const g=createFallenLeafGeometry(kind,variant),p=g.attributes.position,edges=new Map(),used=new Set(),boundary=new Map();
  for(let i=0;i<g.index.count;i+=3){
   const ids=[0,1,2].map(k=>g.index.getX(i+k)),v=ids.map(k=>new THREE.Vector3().fromBufferAttribute(p,k));
   assert.ok(v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0])).z>0,'front-face winding');
   for(let j=0;j<3;j++){const a=ids[j],b=ids[(j+1)%3],key=[Math.min(a,b),Math.max(a,b)].join(':');used.add(a);const e=edges.get(key)||{a,b,count:0,orientation:0};e.count++;e.orientation+=a<b?1:-1;edges.set(key,e);}
  }
  assert.equal(used.size,p.count,'no orphaned vertices');assert.equal(p.count-edges.size+g.index.count/3,1,'disk Euler characteristic');
  for(const e of edges.values()){
   assert.ok(e.count===1||e.count===2);if(e.count===2)assert.equal(e.orientation,0,'opposite shared-edge winding');
   else for(const [a,b] of [[e.a,e.b],[e.b,e.a]]){const list=boundary.get(a)||[];list.push(b);boundary.set(a,list);}
   const a=new THREE.Vector2(p.getX(e.a),p.getY(e.a)),b=new THREE.Vector2(p.getX(e.b),p.getY(e.b)),ab=b.clone().sub(a);
   for(let k=0;k<p.count;k++){if(k===e.a||k===e.b)continue;const ap=new THREE.Vector2(p.getX(k),p.getY(k)).sub(a),t=ap.dot(ab)/ab.lengthSq();if(t>1e-6&&t<1-1e-6)assert.ok(Math.abs(ab.cross(ap))/ab.length()>1e-8,'no T-junction');}
  }
  for(const neighbors of boundary.values())assert.equal(neighbors.length,2);
  const seen=new Set(),queue=[boundary.keys().next().value];while(queue.length){const i=queue.pop();if(seen.has(i))continue;seen.add(i);queue.push(...boundary.get(i));}assert.equal(seen.size,boundary.size,'one boundary loop');
 }
});
test('landing starts at the incoming pose and reaches a stable horizontal pose at 0.8 seconds',()=>{
 for(let i=0;i<30;i++){
  const leaf={state:'falling',tilt:i*.29,rot:i*.21},a=new THREE.Euler(),b=new THREE.Euler();setLeafRotation(leaf,10,a);leaf.state='rest';leaf.contactTilt=leaf.tilt;leaf.landedAt=10;setLeafRotation(leaf,10,b);assert.ok(new THREE.Quaternion().setFromEuler(a).angleTo(new THREE.Quaternion().setFromEuler(b))<1e-7);
  setLeafRotation(leaf,10.8,a);setLeafRotation(leaf,25,b);assert.deepEqual(a.toArray(),b.toArray());assert.equal(a.x,-Math.PI/2);assert.ok(Math.abs(a.y)<1e-12);
 }
});
test('tilted leaves maintain 2 mm support contact throughout settling on any horizontal landing plane',()=>{
 for(let kind=0;kind<2;kind++)for(let variant=0;variant<3;variant++){
  const g=createFallenLeafGeometry(kind,variant),p=g.attributes.position,leaf={state:'rest',contactTilt:2.4,landedAt:0,rot:.83},rotation=new THREE.Euler(),matrix=new THREE.Matrix4(),point=new THREE.Vector3();
  for(let i=0;i<=80;i++){const time=i*.01;setLeafRotation(leaf,time,rotation);const support=lowestLeafPoint(g,rotation,.205);matrix.makeRotationFromEuler(rotation);let min=Infinity;
   for(let j=0;j<p.count;j++){point.fromBufferAttribute(p,j).applyMatrix4(matrix).multiplyScalar(.205);min=Math.min(min,point.y+.505+.002-support);}
   assert.ok(Math.abs(min-.507)<1e-8);
  }
 }
});
test('settling is determined by absolute contact age and leaf tint is stable and bounded',()=>{
 const leaf={state:'rest',contactTilt:1.5,landedAt:2,rot:1},a=new THREE.Euler(),b=new THREE.Euler();
 for(const step of [1/30,1/60,1/144]){for(let t=2;t<2.5;t+=step)setLeafRotation(leaf,t,a);setLeafRotation(leaf,2.5,a);setLeafRotation(leaf,2.5,b);assert.deepEqual(a.toArray(),b.toArray());}
 const colors=[];for(let i=0;i<100;i++){const c=leafInstanceColor(i);assert.deepEqual(c.toArray(),leafInstanceColor(i).toArray());for(const n of c.toArray())assert.ok(n>=.55&&n<=1);colors.push(c.getHex());}assert.ok(new Set(colors).size>95);
});
