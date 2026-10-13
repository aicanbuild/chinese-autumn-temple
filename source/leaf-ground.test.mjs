import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=n=>fs.readFileSync(new URL('../dist/'+n,import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createFallenLeafGeometry}=new Function('THREE',code('leaf-surfaces.js')+';return {createFallenLeafGeometry}')(THREE);
const {setLeafRotation,lowestLeafPoint}=new Function('THREE',code('leaf-settling.js')+';return {setLeafRotation,lowestLeafPoint}')(THREE);
const {supportHeight,advanceSweptLeaf}=new Function('THREE',code('sweep-motion.js')+';return {supportHeight,advanceSweptLeaf}')(THREE);
const app=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8'),update=app.slice(app.indexOf('function updateLeaves('),app.indexOf('// A real twig broom'));
function fixture(surfaceAt,overrides={}){
 const leaf={id:0,index:0,batch:0,active:true,state:'rest',landedAt:-Infinity,contactTilt:0,rot:.3,tilt:0,size:.18,x:0,y:0,z:0,water:false,...overrides};
 return new Function('THREE','createFallenLeafGeometry','setLeafRotation','lowestLeafPoint','supportHeight','advanceSweptLeaf','surfaceAt','leaf',`
 const leaves=[leaf],entered=false,leafDrawCounts=new Uint16Array(6),dummy=new THREE.Object3D(),SWEEP_CLEAR_TIME=1.05;
 const fallenLeafGeometries=Array.from({length:6},(_,i)=>createFallenLeafGeometry(i%2,Math.floor(i/2))),leafMeshes=fallenLeafGeometries.map(g=>new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial(),1));
 const range=(a,b)=>(a+b)/2,clamp=THREE.MathUtils.clamp,poolAt=()=>true;let impacts=0;
 const pondMotion={impact(){impacts++;}},advanceFloatingLeaf=()=>{};
 ${update};return {updateLeaves,leaf,dummy,leafMeshes,geometry:fallenLeafGeometries[0],get impacts(){return impacts}};`)(THREE,createFallenLeafGeometry,setLeafRotation,lowestLeafPoint,supportHeight,advanceSweptLeaf,surfaceAt,leaf);
}
test('stationary dry leaves conform to sloping negative terrain once, then reuse their contact height',()=>{
 let calls=0;const floor=(x,z)=>{calls++;return -.21+x*.15+z*.08;},f=fixture(floor);f.updateLeaves(0,0);const height=f.leaf.y,initial=calls;assert.ok(height<-.17);assert.ok(initial>10);
 const matrix=new THREE.Matrix4().makeRotationFromEuler(f.dummy.rotation),p=new THREE.Vector3();let min=Infinity;
 for(let i=0;i<f.geometry.attributes.position.count;i++){p.fromBufferAttribute(f.geometry.attributes.position,i).multiplyScalar(.18).applyMatrix4(matrix);min=Math.min(min,height+p.y-floor(p.x,p.z));}assert.ok(Math.abs(min-.002)<1e-7);
 const before=calls;f.updateLeaves(.016,1);f.updateLeaves(.016,2);assert.equal(calls,before);assert.equal(f.leaf.y,height);
});
test('a falling leaf whose curled edge reaches a bridge settles on that solid even with its center over water',()=>{
 const f=fixture(x=>x>0?.8:-.025,{state:'falling',landedAt:-Infinity,x:-.02,y:.75,rot:0,tilt:0});f.updateLeaves(0,1);
 assert.equal(f.leaf.state,'rest');assert.equal(f.leaf.water,false);assert.equal(f.impacts,0);assert.ok(f.leaf.y>.75);
});
test('initial leaves straddling a solid bank do not become floating water leaves',()=>{
 const f=fixture(x=>x>0?.25:-.025,{x:-.02,water:true});f.updateLeaves(0,0);assert.equal(f.leaf.water,false);assert.ok(f.leaf.y>.23);
});
test('8 fps leaf substeps preserve one second of falling and upload matrices only once per displayed frame',()=>{
 const a=fixture(()=>0,{state:'falling',y:5}),b=fixture(()=>0,{state:'falling',y:5});
 for(let i=0;i<60;i++)a.updateLeaves(1/60,(i+1)/60);
 const before=b.leafMeshes.map(m=>m.instanceMatrix.version);
 for(let i=0;i<8;i++)for(let j=0;j<3;j++)b.updateLeaves(1/24,i/8+(j+1)/24,j===2);
 assert.ok(Math.abs(a.leaf.y-4.56)<1e-10);assert.ok(Math.abs(b.leaf.y-a.leaf.y)<1e-10);
 b.leafMeshes.forEach((m,i)=>assert.equal(m.instanceMatrix.version-before[i],8));
 const matrix=new THREE.Matrix4();b.leafMeshes[0].getMatrixAt(0,matrix);assert.ok(Math.abs(matrix.elements[13]-b.leaf.y)<1e-6);
});
