import test from 'node:test';import assert from 'node:assert/strict';
import * as T from '../dist/vendor/three/three.module.js';
import {renderSceneFrame} from '../dist/scene-frame.js';

test('animated hierarchy updates each frame and all nested passes share current transforms',()=>{
 const scene=new T.Scene(),parent=new T.Group(),mesh=new T.Mesh(new T.BoxGeometry(),new T.MeshBasicMaterial());scene.add(parent);parent.add(mesh);
 let passes=0;const update=scene.updateMatrixWorld;scene.updateMatrixWorld=function(...args){passes++;return update.apply(this,args);};
 for(let frame=0;frame<4;frame++){
  parent.position.set(frame,2,3);parent.rotation.y=frame*.3;mesh.position.set(1,frame*.2,0);
  const expected=new T.Matrix4().compose(parent.position,parent.quaternion,parent.scale).multiply(new T.Matrix4().compose(mesh.position,mesh.quaternion,mesh.scale));
  const result=renderSceneFrame(scene,()=>{for(let pass=0;pass<4;pass++){if(scene.matrixWorldAutoUpdate)scene.updateMatrixWorld();assert.deepEqual(mesh.matrixWorld.elements,expected.elements);}return 42;});
  assert.equal(result,42);assert.equal(scene.matrixWorldAutoUpdate,true);assert.equal(passes,frame+1);
 }
});
test('an exception restores automatic updates for subsequent frames',()=>{
 const scene=new T.Scene();assert.throws(()=>renderSceneFrame(scene,()=>{throw new Error('render failed');}),/render failed/);assert.equal(scene.matrixWorldAutoUpdate,true);
});
test('manual scene matrices and nested frame boundaries retain their owner settings',()=>{
 const scene=new T.Scene();scene.matrixWorldAutoUpdate=false;scene.updateMatrixWorld=()=>{throw new Error('manual scene must not update');};
 renderSceneFrame(scene,()=>renderSceneFrame(scene,()=>assert.equal(scene.matrixWorldAutoUpdate,false)));assert.equal(scene.matrixWorldAutoUpdate,false);
});
