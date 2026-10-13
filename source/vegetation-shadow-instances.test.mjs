import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/vegetation-shadow-instances.js',import.meta.url),'utf8').replace(/^import.*$/gm,'').replaceAll('export function','function');const {createVegetationShadowInstances}=new Function('THREE',code+';return {createVegetationShadowInstances}')(T);
function light(x){const l=new T.DirectionalLight();l.castShadow=true;l.position.set(x,0,10);l.target.position.set(x,0,0);Object.assign(l.shadow.camera,{left:-2,right:2,top:2,bottom:-2,near:.1,far:30});l.shadow.camera.updateProjectionMatrix();return l;}
function mesh(xs){const m=new T.InstancedMesh(new T.BoxGeometry(.2,.2,.2),new T.MeshStandardMaterial(),xs.length);m.castShadow=true;m.userData.waterMotionPadding=.01;xs.forEach((x,i)=>{m.setMatrixAt(i,new T.Matrix4().makeTranslation(x,0,-5));m.setColorAt(i,new T.Color().setRGB((x+1)/20,.1,.2));});m.instanceMatrix.needsUpdate=true;m.instanceColor.needsUpdate=true;m.updateMatrixWorld();return m;}
function begin(m,l){m.onBeforeShadow(null,m,null,l.shadow.camera,m.geometry,m.material,null);}
function end(m,l){m.onAfterShadow(null,m,null,l.shadow.camera,m.geometry,m.material,null);}
function xs(m){const a=new T.Matrix4(),r=[];for(let i=0;i<m.count;i++){m.getMatrixAt(i,a);r.push(a.elements[12]);}return r;}
test('non-nested light regions retain every required instance and restore full color count',()=>{
 const a=light(5),b=light(0),m=mesh([10,0,5,1]),color=m.onBeforeRender;let before=0,after=0;m.onBeforeShadow=()=>before++;m.onAfterShadow=()=>after++;
 const c=createVegetationShadowInstances([m],[a,b]);assert.deepEqual(xs(m),[5,0,1,10]);assert.equal(m.onBeforeRender,color);const col=new T.Color();xs(m).forEach((x,i)=>{m.getColorAt(i,col);assert.ok(Math.abs(col.r-(x+1)/20)<1e-7);});
 begin(m,a);assert.deepEqual(xs(m),[5]);end(m,a);assert.equal(m.count,4);begin(m,b);assert.deepEqual(xs(m),[5,0,1]);end(m,b);assert.equal(m.count,4);assert.equal(before,2);assert.equal(after,2);assert.equal(c.stats.skippedInstances,4);
 const other=light(20);begin(m,other);assert.equal(m.count,4);end(m,other);c.enabled=false;begin(m,a);assert.equal(m.count,4);end(m,a);
});
test('wind envelope, light movement and matrix edits invalidate cached shadow prefixes',()=>{
 const l=light(0),m=mesh([0,2.5,10]);m.userData.waterMotionPadding=.5;const c=createVegetationShadowInstances([m],[l]);begin(m,l);assert.equal(m.count,2);end(m,l);
 l.position.x=10;l.target.position.x=10;l.updateWorldMatrix(true,false);l.target.updateWorldMatrix(true,false);l.shadow.updateMatrices(l);begin(m,l);assert.equal(m.count,3);end(m,l);c.update();begin(m,l);assert.deepEqual(xs(m),[10]);end(m,l);
 m.setMatrixAt(2,new T.Matrix4().makeTranslation(10,0,-5));m.instanceMatrix.needsUpdate=true;begin(m,l);assert.equal(m.count,3);end(m,l);c.update();begin(m,l);assert.equal(m.count,2);end(m,l);
});
test('geometry edits and displacement do not use stale visibility decisions',()=>{
 const l=light(0),m=mesh([0,10]),c=createVegetationShadowInstances([m],[l]);m.geometry.attributes.position.setX(0,20);m.geometry.attributes.position.needsUpdate=true;begin(m,l);assert.equal(m.count,2);end(m,l);c.update();
 m.material.displacementMap=new T.Texture();begin(m,l);assert.equal(m.count,2);end(m,l);c.beginFrame();assert.equal(c.stats.savedTriangles,0);
});
test('batches with reflection prefixes or custom per-instance attributes are left untouched',()=>{
 const l=light(0),a=mesh([10,0]),b=mesh([10,0]);a.userData.waterReflectionCount=1;b.geometry.setAttribute('phase',new T.InstancedBufferAttribute(new Float32Array([1,2]),1));const previous=a.onBeforeShadow,c=createVegetationShadowInstances([a,b],[l]);assert.equal(c.stats.batches,0);assert.equal(a.onBeforeShadow,previous);assert.deepEqual(xs(a),[10,0]);assert.deepEqual(xs(b),[10,0]);
});
test('order-preserving mode culls light prefixes without disturbing pond reflection layout or instance colors',()=>{
 const a=light(5),b=light(0),empty=light(50),m=mesh([10,0,5,1]);m.userData.waterReflectionCount=2;
 const matrices=m.instanceMatrix.array.slice(),colors=m.instanceColor.array.slice(),matrixVersion=m.instanceMatrix.version;
 const c=createVegetationShadowInstances([m],[a,b,empty],{reorder:false});assert.equal(c.stats.batches,1);assert.deepEqual(xs(m),[10,0,5,1]);assert.equal(m.instanceMatrix.version,matrixVersion);
 begin(m,a);assert.equal(m.count,3);end(m,a);begin(m,b);assert.equal(m.count,4);end(m,b);begin(m,empty);assert.equal(m.count,0);end(m,empty);assert.equal(m.count,4);
 assert.deepEqual(m.instanceMatrix.array,matrices);assert.deepEqual(m.instanceColor.array,colors);assert.equal(m.userData.waterReflectionCount,2);
 // A temporary water-capture count cannot use prefixes computed for a full draw.
 m.count=2;begin(m,a);assert.equal(m.count,2);end(m,a);assert.equal(m.count,2);
});
