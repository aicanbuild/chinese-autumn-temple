import {createWoodenFish} from './wooden-fish.js';
import * as THREE from 'three';
import {createTempleBell} from './temple-bell.js';
import {IncenseCycle} from './ritual-state.js';
import {createIncenseSmoke} from './incense-smoke.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

// Separate the original Blender bell and sticks from the material batches.
// Triangles are classified in world space; all other geometry stays untouched.
export function extractRegion(root,materialMatch,inside,triangleInside=null){
 const result=new THREE.Group();root.updateMatrixWorld(true);
 root.traverse(o=>{
  if(!o.isMesh||!materialMatch(o.material?.name||''))return;
  const g=o.geometry,index=g.index,position=g.attributes.position,keep=[],take=[],v=new THREE.Vector3();
  for(let n=0;n<(index?index.count:position.count);n+=3){
   const ids=[0,1,2].map(k=>index?index.getX(n+k):n+k);v.set(0,0,0);
   for(const id of ids)v.add(new THREE.Vector3().fromBufferAttribute(position,id));v.multiplyScalar(1/3).applyMatrix4(o.matrixWorld);
   const selected=inside(v)&&(!triangleInside||triangleInside(ids.map(id=>new THREE.Vector3().fromBufferAttribute(position,id).applyMatrix4(o.matrixWorld))));
   (selected?take:keep).push(...ids);
  }
  if(!take.length)return;
  const piece=new THREE.BufferGeometry();
  for(const [name,attr]of Object.entries(g.attributes)){
   const data=new attr.array.constructor(take.length*attr.itemSize);
   take.forEach((id,i)=>{for(let c=0;c<attr.itemSize;c++)data[i*attr.itemSize+c]=attr.array[id*attr.itemSize+c];});
   piece.setAttribute(name,new THREE.BufferAttribute(data,attr.itemSize,attr.normalized));
  }
  piece.applyMatrix4(o.matrixWorld);piece.computeBoundingSphere();
  const mesh=new THREE.Mesh(piece,o.material);mesh.castShadow=true;mesh.receiveShadow=true;result.add(mesh);
  // Bounds must describe the surviving faces, not discarded bridge/bell vertices.
  // Keep every attribute and share vertices through a fresh compact index.
  const remap=new Map(),used=[],compact=keep.map(id=>{if(!remap.has(id)){remap.set(id,used.length);used.push(id);}return remap.get(id);});
  for(const [name,attr]of Object.entries(g.attributes)){
   const data=new attr.array.constructor(used.length*attr.itemSize);
   used.forEach((id,i)=>{for(let c=0;c<attr.itemSize;c++)data[i*attr.itemSize+c]=attr.array[id*attr.itemSize+c];});
   g.setAttribute(name,new THREE.BufferAttribute(data,attr.itemSize,attr.normalized));
  }
  g.setIndex(compact);g.computeBoundingBox();g.computeBoundingSphere();
 });return result;
}

export function createRituals({scene,model,camera,controls,broom,ringSound,bellAsset,woodenFishAsset,knockSound,candlePositions=[],onEnter=()=>{},onLeave=()=>{}}){
 const woodenFish=createWoodenFish(woodenFishAsset,scene,camera,knockSound);
 const cycle=new IncenseCycle(),ray=new THREE.Raycaster();
 const root=new THREE.Group();root.name='Temple rituals';scene.add(root);
 const oldBell=extractRegion(model,n=>/gilded|gold/i.test(n),p=>p.x>-9.7&&p.x<-8.3&&p.y>1.60&&p.y<3.48&&p.z>-4.85&&p.z<-3.35);
 oldBell.traverse(o=>o.geometry?.dispose());
 const oldHammer=extractRegion(model,n=>/cedar/i.test(n),p=>p.x>-8.43&&p.x<-8.17&&p.y>2.22&&p.y<2.48&&p.z>-4.73&&p.z<-3.08);
 oldHammer.traverse(o=>o.geometry?.dispose());
 const oldRopes=extractRegion(model,n=>/deep dark wood/i.test(n),p=>p.x>-8.33&&p.x<-8.27&&p.y>2.32&&p.y<3.62&&p.z>-4.65&&p.z<-3.25);
 oldRopes.traverse(o=>o.geometry?.dispose());
 const bell=createTempleBell(bellAsset,root,ringSound);
 const oldSticks=extractRegion(model,n=>/cedar/i.test(n),p=>Math.abs(p.x)<.24&&p.y>1.50&&p.y<2.03&&p.z>-6.8&&p.z<-6.4);
 oldSticks.traverse(o=>o.geometry?.dispose());
 // Batch the many straw strands so the parked broom is cheap to render.
 const batches=new Map();broom.updateMatrixWorld(true);
 for(const mesh of [...broom.children]){
  const key=mesh.material.color.getHexString()+':'+mesh.material.roughness;
  if(!batches.has(key))batches.set(key,{material:mesh.material,geometries:[]});
  batches.get(key).geometries.push(mesh.geometry.clone().applyMatrix4(mesh.matrix));broom.remove(mesh);mesh.geometry.dispose();
 }
 for(const {material,geometries}of batches.values()){const mesh=new THREE.Mesh(mergeGeometries(geometries),material);mesh.castShadow=true;broom.add(mesh);geometries.forEach(g=>g.dispose());}
 const parked=broom.clone();parked.visible=true;parked.position.set(1.06,.66,11.9);parked.rotation.set(-.08,0,-.23);root.add(parked);
 parked.name='Broom resting against the bridge rail';
 const sticks=[],wood=new THREE.MeshStandardMaterial({color:'#91632c',roughness:.9}),char=new THREE.MeshStandardMaterial({color:'#8b8274',roughness:1});
 const ember=new THREE.MeshStandardMaterial({color:'#f67a25',emissive:'#ff4608',emissiveIntensity:4,roughness:.6});
 for(let i=0;i<3;i++){
  const group=new THREE.Group();group.position.set((i-1)*.095,1.52,-6.6+(i===1?-.07:.03));root.add(group);
  const body=new THREE.Mesh(new THREE.CylinderGeometry(.006,.006,1,12),wood);group.add(body);
  const tip=new THREE.Mesh(new THREE.SphereGeometry(.007,10,8),ember);group.add(tip);
  const ashTip=new THREE.Mesh(new THREE.CylinderGeometry(.0065,.0065,.018,12),char);group.add(ashTip);
  const smoke=createIncenseSmoke(root,i*2.1);sticks.push({group,body,tip,ashTip,smoke,smokeTip:new THREE.Vector3()});
 }
 const glow=new THREE.PointLight('#ff6a20',0,1.3,2);glow.position.set(0,2,-6.6);root.add(glow);
 const invisible=new THREE.MeshBasicMaterial({visible:false});
 const targets=[];
 function target(id,pos,size){const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),invisible);mesh.position.set(...pos);mesh.userData.action=id;root.add(mesh);targets.push(mesh);}
 target('wooden-fish',[-.95,1.82,-6.45],[.68,.48,.56]);target('bell',[-8.5,2.25,-4.1],[3.0,2.65,1.8]);target('temple',[0,4.65,-6.6],[13.5,8.0,9.0]);target('incense',[0,1.85,-6.6],[.85,1,.8]);target('broom',[1.23,1.55,11.9],[.95,2.1,.8]);
 candlePositions.forEach(([x,y,z],i)=>target(`candle-${i}`,[x,y-.20,z],[.28,.60,.28]));
 const indoorTarget=t=>['incense','wooden-fish'].includes(t.userData.action)||t.userData.action.startsWith('candle-');
 const layer=document.querySelector('#ritual-hotspots');
 let inside=false,tween=null,saved=null,bellHeld=false,bellSaved=null;
 const returnButton=document.querySelector('#leave-hall');
 function ring(){return bell.ring();}
 function focusBell(){
  if(bellHeld)return;bellHeld=true;bellSaved={position:camera.position.clone(),target:controls.target.clone(),min:controls.minDistance,max:controls.maxDistance};
  tween={time:0,from:camera.position.clone(),look:controls.target.clone(),to:new THREE.Vector3(-5.9,3.4,-.5),target:new THREE.Vector3(-8.9,2.6,-4.1)};
  controls.enabled=false;controls.minDistance=1.1;controls.maxDistance=7.5;
 }
 function leaveBell(){if(!bellHeld)return;bellHeld=false;tween=null;camera.position.copy(bellSaved.position);controls.target.copy(bellSaved.target);controls.minDistance=bellSaved.min;controls.maxDistance=bellSaved.max;controls.enabled=true;controls.update();}
 function light(){return cycle.light();}
 function enter(){
  if(inside)return;inside=true;onEnter();
  saved={position:camera.position.clone(),target:controls.target.clone(),min:controls.minDistance,max:controls.maxDistance,minPolar:controls.minPolarAngle,maxPolar:controls.maxPolarAngle,fov:camera.fov,screenPan:controls.screenSpacePanning};
  tween={time:0,from:camera.position.clone(),look:controls.target.clone(),to:new THREE.Vector3(.08,2.72,-4.02),target:new THREE.Vector3(0,2.90,-8.35)};
  controls.enabled=false;controls.minDistance=.65;controls.maxDistance=8.5;controls.minPolarAngle=.40;controls.maxPolarAngle=2.25;controls.screenSpacePanning=true;camera.fov=66;camera.updateProjectionMatrix();
  returnButton.classList.remove('hidden');document.querySelector('#view-mode').classList.add('hidden');document.querySelector('#broom-mode').classList.add('hidden');document.querySelector('.divider').classList.add('hidden');
 }
 function leave(){
  if(!inside)return;woodenFish.putBack();inside=false;tween=null;onLeave();
  camera.position.copy(saved.position);controls.target.copy(saved.target);controls.minDistance=saved.min;controls.maxDistance=saved.max;controls.minPolarAngle=saved.minPolar;controls.maxPolarAngle=saved.maxPolar;controls.screenSpacePanning=saved.screenPan;camera.fov=saved.fov;camera.updateProjectionMatrix();controls.enabled=true;controls.update();
  returnButton.classList.add('hidden');document.querySelector('#view-mode').classList.remove('hidden');document.querySelector('#broom-mode').classList.remove('hidden');document.querySelector('.divider').classList.remove('hidden');
 }
 function pick(mouse,sweeping){
  if(sweeping||tween)return null;if(bellHeld)return 'bell';if(inside&&woodenFish.held)return 'wooden-fish-strike';ray.setFromCamera(mouse,camera);root.updateMatrixWorld(true);
  const active=targets.filter(t=>inside?indoorTarget(t):!indoorTarget(t));
  return ray.intersectObjects(active,false)[0]?.object.userData.action||null;
 }
 function update(dt,time,{sweeping}){
  cycle.update(dt);bell.update(dt);woodenFish.update(dt);
  parked.visible=!sweeping;
  if(tween){tween.time+=dt;const t=Math.min(1,tween.time/.95),s=t*t*(3-2*t);camera.position.lerpVectors(tween.from,tween.to,s);controls.target.lerpVectors(tween.look,tween.target,s);camera.lookAt(controls.target);if(t===1){tween=null;controls.enabled=true;controls.update();}}
  const replacing=cycle.phase==='replacing',newStick=replacing?Math.max(0,(cycle.time-1)/2):0;
  const height=replacing?(cycle.time<1?.08*Math.max(0,1-cycle.time/.65):.52):.08+.44*cycle.remaining;
  const insertEase=newStick*newStick*(3-2*newStick);
  for(const [i,s]of sticks.entries()){
   s.body.visible=!replacing||cycle.time<.65||cycle.time>=1;s.body.scale.y=Math.max(.001,height);s.body.position.y=height/2;
   s.group.position.y=1.52+(replacing&&cycle.time>=1?.7*(1-insertEase):0);
   s.tip.position.y=height;s.tip.visible=cycle.phase==='burning';s.ashTip.position.y=height-.008;s.ashTip.visible=cycle.phase==='burning';
   s.smokeTip.copy(s.group.position);s.smokeTip.y+=height;
   s.smoke.update(time,cycle.phase==='burning',s.smokeTip);
  }
  glow.intensity=cycle.phase==='burning'?.09+.015*Math.sin(time*9):0;
  layer.dataset.state=JSON.stringify({inside,woodenFish:woodenFish.stats,incense:cycle.phase,remaining:Math.round(cycle.remaining*100),completed:cycle.completed,bellRings:bell.rings,bellParts:bell.parts,removedSticks:oldSticks.children.length,broomParked:parked.visible,transition:!!tween});

 }
 return {pick,ring,focusBell,leaveBell,light,enter,leave,update,woodenFish,get bellHeld(){return bellHeld;},get inside(){return inside;},get moving(){return !!tween;}};
}
