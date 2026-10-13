import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const helper=fs.readFileSync(new URL('../dist/water-visibility.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
const {createWaterVisibility}=new Function('THREE',helper+';return {createWaterVisibility}')(THREE);
test('water captures conservatively preserve crossing geometry and restore hidden states',()=>{
 const scene=new THREE.Scene(),material=new THREE.MeshBasicMaterial();
 const add=y=>{const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),material);m.position.y=y;scene.add(m);return m;};
 const above=add(2),below=add(-2),crossing=add(0),hidden=add(2);hidden.visible=false;
 const near=add(.7);near.userData.waterMotionPadding=.25; // A deformed plant keeps a conservative bound.
 const shifted=new THREE.Group();shifted.position.y=6;const child=add(-3);shifted.add(child);scene.add(shifted);
 const water=add(0);water.isWater=true;
 const f=createWaterVisibility(scene,0);assert.equal(f.above,3);assert.equal(f.below,1);
 const restore=f.capture('refraction');assert.equal(above.visible,false);assert.equal(child.visible,false);assert.ok(below.visible&&crossing.visible&&near.visible&&water.visible);restore();assert.ok(above.visible&&child.visible);assert.equal(hidden.visible,false);
 const end=f.capture('reflection');assert.equal(below.visible,false);assert.ok(above.visible&&crossing.visible);end();assert.ok(below.visible);
});
test('instances use world transforms and dynamic fish/leaf pools retain explicit sides',()=>{
 const scene=new THREE.Scene(),mat=new THREE.MeshBasicMaterial(),geo=new THREE.BoxGeometry(1,1,1);
 const grove=new THREE.InstancedMesh(geo,mat,2);grove.setMatrixAt(0,new THREE.Matrix4().makeTranslation(0,4,0));grove.setMatrixAt(1,new THREE.Matrix4().makeTranslation(0,8,0));scene.add(grove);
 const fish=new THREE.InstancedMesh(geo,mat,4);fish.frustumCulled=false;fish.userData.waterSide='below';scene.add(fish);
 const unknown=new THREE.InstancedMesh(geo,mat,1);unknown.frustumCulled=false;scene.add(unknown);
 const f=createWaterVisibility(scene,0);assert.equal(f.above,1);assert.equal(f.below,1);const restore=f.capture('refraction');assert.equal(grove.visible,false);assert.ok(fish.visible&&unknown.visible);restore();
});
test('static low fixtures are omitted underwater while a moving plant keeps its safety margin',()=>{
 const scene=new THREE.Scene(),material=new THREE.MeshBasicMaterial();
 const lamp=new THREE.InstancedMesh(new THREE.BoxGeometry(.5,1,.5),material,1);lamp.setMatrixAt(0,new THREE.Matrix4().makeTranslation(0,.65,0));lamp.userData.waterMotionPadding=.005;scene.add(lamp);
 const plant=new THREE.InstancedMesh(lamp.geometry,material,1);plant.setMatrixAt(0,new THREE.Matrix4().makeTranslation(2,.65,0));scene.add(plant);
 const f=createWaterVisibility(scene,0),restore=f.capture('refraction');assert.equal(lamp.visible,false);assert.equal(plant.visible,true);restore();assert.equal(lamp.visible,true);
});
test('batched trees classify transformed instances and never partition their shared prototype indices',()=>{
 const scene=new THREE.Scene(),geometry=new THREE.BoxGeometry(1,2,1),material=new THREE.MeshBasicMaterial();
 const make=ys=>{const mesh=new THREE.BatchedMesh(ys.length,geometry.attributes.position.count,geometry.index.count,material);const id=mesh.addGeometry(geometry);for(const y of ys)mesh.setMatrixAt(mesh.addInstance(id),new THREE.Matrix4().makeTranslation(0,y,0));mesh.userData.waterClipStatic=true;scene.add(mesh);return mesh;};
 const above=make([4,8]),crossing=make([-4,4]);above.position.y=1;const index=crossing.geometry.index;
 const f=createWaterVisibility(scene,0);assert.equal(f.above,1);assert.equal(f.below,0);assert.equal(f.splitMeshes,0);
 const restore=f.capture('refraction');assert.equal(above.visible,false);assert.equal(crossing.visible,true);assert.equal(crossing.geometry.index,index);restore();assert.equal(above.visible,true);
});
test('static crossing meshes keep crossing faces in both captures and restore original indices',()=>{
 const scene=new THREE.Scene(),g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([0,1,0,1,1,0,0,2,0,0,-2,0,1,-2,0,0,-1,0,0,-1,0,1,1,0,0,1,0],3));g.setIndex([0,1,2,3,4,5,6,7,8]);
 const mesh=new THREE.Mesh(g,new THREE.MeshBasicMaterial());mesh.userData.waterClipStatic=true;scene.add(mesh);const original=g.index,position=g.attributes.position,f=createWaterVisibility(scene,0);assert.equal(f.splitMeshes,1);
 const restore=f.capture('refraction');assert.deepEqual([...g.index.array],[3,4,5,6,7,8]);assert.equal(g.attributes.position,position);restore();assert.equal(g.index,original);
 const end=f.capture('reflection');assert.deepEqual([...g.index.array],[0,1,2,6,7,8]);end();assert.equal(g.index,original);
});
test('shared and animated geometries are never partitioned by one instance world transform',()=>{
 const scene=new THREE.Scene(),g=new THREE.BoxGeometry(1,2,1),m=new THREE.MeshBasicMaterial();
 for(let i=0;i<2;i++){const o=new THREE.Mesh(g,m);o.userData.waterClipStatic=true;o.position.y=i*.1;scene.add(o);}
 const animated=new THREE.Mesh(new THREE.BoxGeometry(1,2,1),m);scene.add(animated);const f=createWaterVisibility(scene,0);assert.equal(f.splitMeshes,0);
});
test('water restores scene visibility even if an offscreen capture throws',()=>{
 const code=fs.readFileSync(new URL('../dist/vendor/three/addons/objects/Water2.js',import.meta.url),'utf8').replace(/import[\s\S]*?from ['"][^'"]+['"];\n/g,'').replace(/export\s*\{[^}]+\};?/g,'');
 const calls=[];class Capture{constructor(){this.matrixWorld=new THREE.Matrix4();}getRenderTarget(){return {texture:new THREE.Texture()};}onBeforeRender(){calls.push('capture');throw new Error('simulated context loss');}}
 const names=['Clock','Color','Matrix4','Mesh','RepeatWrapping','ShaderMaterial','TextureLoader','UniformsLib','UniformsUtils','Vector2','Vector4'];
 const Water=new Function(...names,'Reflector','Refractor',code+';return Water;')(...names.map(n=>THREE[n]),Capture,Capture);
 const water=new Water(new THREE.PlaneGeometry(2,2),{normalMap0:new THREE.Texture(),normalMap1:new THREE.Texture(),captureFilter(mode){calls.push(mode);return ()=>calls.push('restore');}});
 const camera=new THREE.PerspectiveCamera();camera.updateMatrixWorld();
 assert.throws(()=>water.onBeforeRender({},new THREE.Scene(),camera),/simulated context loss/);assert.equal(water.visible,true);assert.deepEqual(calls,['reflection','capture','restore']);
});

test('reflection instance prefixes preserve full refraction and restore current counts and visibility',()=>{
 const scene=new THREE.Scene(),geometry=new THREE.BoxGeometry(1,1,1),mesh=new THREE.InstancedMesh(geometry,new THREE.MeshBasicMaterial(),3);
 [0,-2,-3].forEach((y,i)=>mesh.setMatrixAt(i,new THREE.Matrix4().makeTranslation(0,y,0)));
 mesh.userData.waterReflectionCount=1;mesh.userData.waterMotionPadding=.005;scene.add(mesh);
 const f=createWaterVisibility(scene,0),matrices=mesh.instanceMatrix.array.slice();
 let restore=f.capture('reflection');assert.equal(mesh.count,1);assert.deepEqual(mesh.instanceMatrix.array,matrices);restore();assert.equal(mesh.count,3);
 restore=f.capture('refraction');assert.equal(mesh.count,3);restore();assert.equal(mesh.count,3);
 mesh.count=2;restore=f.capture('reflection');assert.equal(mesh.count,1);restore();assert.equal(mesh.count,2);
 mesh.visible=false;restore=f.capture('reflection');assert.equal(mesh.count,2);restore();assert.equal(mesh.visible,false);
});

test('dry forest valleys stay out of pond refraction while shore reflections remain',()=>{
 const landscapeCode=fs.readFileSync(new URL('../dist/landscape.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');
 const createLandscape=new Function('THREE',landscapeCode+';return createLandscape;')(THREE);
 const scene=new THREE.Scene(),terrain=new THREE.Group(),woodland=new THREE.Group();
 // A dry bank and remote low valley cross the water elevation, but this asset
 // has no geometry inside the pond. Elevation alone cannot classify it.
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute([12,.2,5,13,.2,6,12,.2,7,24,-.23,5,25,-.23,6,24,-.23,7],3));
 const ground=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial());terrain.add(ground);
 for(let species=0;species<3;species++)for(let lod=0;lod<2;lod++){const group=new THREE.Group();group.name=`Woodland_${species}_${lod}`;woodland.add(group);}
 createLandscape(terrain,woodland,{trees:[]},scene);
 const bed=new THREE.Mesh(new THREE.PlaneGeometry(10,6),new THREE.MeshBasicMaterial());bed.position.y=-1.5;bed.userData.waterSide='below';scene.add(bed);
 const visibility=createWaterVisibility(scene,-.025);const original=geometry.index;
 const restore=visibility.capture('refraction');assert.equal(ground.visible,false);assert.equal(bed.visible,true);assert.equal(geometry.index,original);restore();assert.equal(ground.visible,true);
 const reflect=visibility.capture('reflection');assert.equal(ground.visible,true);assert.equal(bed.visible,false);reflect();assert.equal(bed.visible,true);
});

test('woody reflection exclusion preserves refraction, shadows and the active tree LOD',()=>{
 const scene=new THREE.Scene(),g=new THREE.BoxGeometry(1,2,1),m=new THREE.MeshBasicMaterial();
 const near=new THREE.Mesh(g,m),far=new THREE.Mesh(g,m),stone=new THREE.Mesh(g,m);
 for(const tree of [near,far]){tree.userData.waterReflection=false;tree.castShadow=true;scene.add(tree);}
 far.visible=false;scene.add(stone);
 const filter=createWaterVisibility(scene,0);
 assert.equal(filter.reflectionExcluded,2);
 for(const active of [near,far]){
  near.visible=active===near;far.visible=active===far;
  const end=filter.capture('reflection');
  assert.equal(near.visible,false);assert.equal(far.visible,false);assert.equal(stone.visible,true);
  assert.ok(near.castShadow&&far.castShadow);end();
  assert.equal(near.visible,active===near);assert.equal(far.visible,active===far);
  const refract=filter.capture('refraction');assert.equal(active.visible,true);refract();
  assert.equal(active.visible,true);
 }
});

test('instanced and batched branches are excluded without mutating their instance data',()=>{
 const scene=new THREE.Scene(),g=new THREE.BoxGeometry(1,2,1),m=new THREE.MeshBasicMaterial();
 const instanced=new THREE.InstancedMesh(g,m,2),batched=new THREE.BatchedMesh(2,g.attributes.position.count,g.index.count,m);
 const id=batched.addGeometry(g);batched.addInstance(id);batched.addInstance(id);
 for(const tree of [instanced,batched]){tree.userData.waterReflection=false;scene.add(tree);}
 const filter=createWaterVisibility(scene,0),matrices=instanced.instanceMatrix.array.slice();
 const end=filter.capture('reflection');assert.ok(!instanced.visible&&!batched.visible);end();
 assert.ok(instanced.visible&&batched.visible);assert.equal(instanced.count,2);assert.deepEqual(instanced.instanceMatrix.array,matrices);
});
