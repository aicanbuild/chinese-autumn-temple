import {createHash} from 'node:crypto';
import test from 'node:test';import assert from 'node:assert/strict';import * as T from '../dist/vendor/three/three.module.js';import fs from 'node:fs';
const source=fs.readFileSync(new URL('../dist/hall-occlusion.js',import.meta.url),'utf8').replace(/^import.*$/gm,'').replaceAll('export function','function');const {rectangleHidesBox,createHallOcclusion}=new Function('THREE',source+';return {rectangleHidesBox,createHallOcclusion}')(T);
const rect={axis:2,lo:[-2,-2,-2],hi:[2,2,-2]},eye=new T.Vector3();
test('occlusion requires every point in the box to lie behind an actual rectangle',()=>{
 const behind=new T.Box3(new T.Vector3(-.5,-.5,-6),new T.Vector3(.5,.5,-5));assert.ok(rectangleHidesBox(eye,behind,rect));
 for(const b of [new T.Box3(new T.Vector3(-5,-.5,-6),new T.Vector3(5,.5,-5)),new T.Box3(new T.Vector3(-.5,-.5,-3),new T.Vector3(.5,.5,-1)),new T.Box3(new T.Vector3(-.5,-.5,1),new T.Vector3(.5,.5,2))])assert.equal(rectangleHidesBox(eye,b,rect),false);
 assert.equal(rectangleHidesBox(new T.Vector3(0,0,-2),behind,rect),false);
 for(let i=0;i<1000;i++){const p=new T.Vector3(-.5+(i%17)/16,-.5+(i%29)/28,-6+(i%31)/30),t=-2/p.z;assert.ok(Math.abs(p.x*t)<2&&Math.abs(p.y*t)<2);}
});
test('hidden draws restore shared geometry and preserve shadows, other cameras and previous callbacks',()=>{
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(),mesh=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial());mesh.position.z=-5;mesh.userData.waterMotionPadding=.01;mesh.castShadow=true;scene.add(mesh);scene.updateMatrixWorld(true);let calls=0;mesh.onBeforeRender=()=>calls++;const shadow=mesh.onBeforeShadow;
 const c=createHallOcclusion(scene,camera,[rect],{isInside:()=>true}),g=mesh.geometry,original=g.drawRange.count;
 mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,0);assert.equal(mesh.visible,true);assert.equal(mesh.onBeforeShadow,shadow);assert.equal(mesh.castShadow,true);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,original);assert.equal(calls,1);
 mesh.onBeforeRender(null,scene,new T.PerspectiveCamera(),g,mesh.material,null);assert.equal(g.drawRange.count,original);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
 mesh.position.z=-1;scene.updateMatrixWorld(true);mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,original);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
});
test('flat scenery behind the camera is omitted and restored when the view turns',()=>{
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(60,1,.1,100),mesh=new T.Mesh(new T.BoxGeometry(20,.2,1),new T.MeshStandardMaterial());mesh.position.set(0,0,3);mesh.userData.waterMotionPadding=.01;scene.add(mesh);scene.updateMatrixWorld(true);camera.updateMatrixWorld();
 const c=createHallOcclusion(scene,camera,[],{isInside:()=>true}),g=mesh.geometry;mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,0);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
 camera.rotation.y=Math.PI;camera.updateMatrixWorld();mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,Infinity);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
});
test('changing an instance transform invalidates cached hidden bounds',()=>{
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(60,1,.1,100),mesh=new T.InstancedMesh(new T.BoxGeometry(.2,.2,.2),new T.MeshStandardMaterial(),1),m=new T.Matrix4();mesh.setMatrixAt(0,m.makeTranslation(0,0,-5));mesh.instanceMatrix.needsUpdate=true;mesh.userData.waterMotionPadding=.01;scene.add(mesh);scene.updateMatrixWorld(true);camera.updateMatrixWorld();createHallOcclusion(scene,camera,[rect],{isInside:()=>true});const g=mesh.geometry;
 mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,0);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
 mesh.setMatrixAt(0,m.makeTranslation(0,0,-1));mesh.instanceMatrix.needsUpdate=true;mesh.onBeforeRender(null,scene,camera,g,mesh.material,null);assert.equal(g.drawRange.count,Infinity);mesh.onAfterRender(null,scene,camera,g,mesh.material,null);
});

test('occluder data matches current original sanctuary and replacement caisson geometry',()=>{
 const metadata=JSON.parse(fs.readFileSync(new URL('../dist/assets/hall-occluders.json',import.meta.url)));for(const file of ['sanctuary.glb','fine-caisson.glb'])assert.equal(metadata.geometryBindings[file],createHash('sha256').update(fs.readFileSync(new URL('../dist/assets/'+file,import.meta.url))).digest('hex'));
});
