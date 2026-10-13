import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/water-surface.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const create=new Function('THREE',code+';return createWaterSurfaceVisibility;')(THREE);
function pond(){const shape=new THREE.Shape();shape.absellipse(0,0,11.48,6.88,0,Math.PI*2,false,0);const mesh=new THREE.Mesh(new THREE.ShapeGeometry(shape,128));mesh.rotation.x=-Math.PI/2;mesh.position.set(0,-.025,5.8);return mesh;}
function camera(x,y,z,tx,ty,tz){const c=new THREE.PerspectiveCamera(43,846/748,.09,420);c.position.set(x,y,z);c.lookAt(tx,ty,tz);c.updateMatrixWorld(true);return c;}
test('hall camera rejects the entirely hidden pond that sphere culling incorrectly retains',()=>{
 const water=pond(),c=camera(.12,3.12,-2.45,0,2.3,-7.2);water.updateMatrixWorld(true);
 const frustum=new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(c.projectionMatrix,c.matrixWorldInverse));
 assert.equal(frustum.intersectsObject(water),true);assert.equal(create(water).update(c),false);assert.equal(water.visible,false);
});
test('returning outside immediately restores water for overview and the bridge',()=>{
 const water=pond(),visibility=create(water);visibility.update(camera(.12,3.12,-2.45,0,2.3,-7.2));
 assert.ok(visibility.update(camera(14,8.5,26,0,2,0)));
 assert.ok(visibility.update(camera(0,2.18,13.3,0,1.6,4)));
 assert.ok(visibility.update(camera(4.6,3.5,16.4,1,1.3,11.9)));
});
test('partly visible water is never culled across camera directions, aspect ratios and near-plane crossings',()=>{
 const water=pond(),visibility=create(water),point=new THREE.Vector3();water.updateMatrixWorld(true);
 let visibleSamples=0;
 for(const aspect of [.5,1,2])for(let i=0;i<64;i++){
  const angle=i*Math.PI*2/64,c=camera(Math.sin(angle)*14,1.2+i%8,5.8+Math.cos(angle)*14,Math.sin(angle+.9)*8,0,5.8+Math.cos(angle+.9)*8);c.aspect=aspect;c.updateProjectionMatrix();
  const visible=visibility.update(c),frustum=new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(c.projectionMatrix,c.matrixWorldInverse));
  for(let j=0;j<water.geometry.attributes.position.count;j++){
   point.fromBufferAttribute(water.geometry.attributes.position,j).applyMatrix4(water.matrixWorld);
   if(frustum.containsPoint(point)){visibleSamples++;assert.equal(visible,true);break;}
  }
 }
 assert.ok(visibleSamples>100);
 const group=new THREE.Group();group.position.set(20,3,-15);group.rotation.y=.7;group.add(water);
 const c=camera(20,12,20,20,3,-9);assert.ok(visibility.update(c));
});
