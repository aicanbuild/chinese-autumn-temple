import * as THREE from 'three';
import {HandwashMotion,ladleAngles,constrainLadleTarget,ladleTravel} from './handwash-motion.js';
const CENTER=new THREE.Vector3(-3.7,1.23,15.6),REST=new THREE.Vector3(-3.58,1.505,15.88),RADIUS=.39;
const rippleCode=`uniform vec4 washRipples[16];uniform float washTime;
float washHeight(vec2 p){float h=0.;for(int i=0;i<16;i++){vec4 e=washRipples[i];float age=washTime-e.z;if(age<0.||age>2.8)continue;float r=length(p-e.xy);float band=r-age*.43;h+=sin(band*63.)*exp(-band*band/.012)*e.w*exp(-age*1.4);}return h;}
vec2 washSlope(vec2 p){return vec2(washHeight(p+vec2(.003,0.))-washHeight(p-vec2(.003,0.)),washHeight(p+vec2(0.,.003))-washHeight(p-vec2(0.,.003)))/.006;}`;
function disk(radius){const p=[0,0,0],uv=[.5,.5],idx=[],rings=32,n=96;for(let j=1;j<=rings;j++)for(let k=0;k<n;k++){const a=k/n*Math.PI*2,r=radius*j/rings;p.push(r*Math.cos(a),0,r*Math.sin(a));uv.push(.5+.5*r/radius*Math.cos(a),.5+.5*r/radius*Math.sin(a));}for(let k=0;k<n;k++)idx.push(0,1+(k+1)%n,1+k);for(let j=0;j<rings-1;j++)for(let k=0;k<n;k++){const a=1+j*n+k,b=1+j*n+(k+1)%n;idx.push(a,b+n,a+n,a,b,b+n);}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();return g;}
export function createHandwash(asset,scene,camera,controls,{stoneNormal,woodMap,splash=()=>{}}={}){
 const root=new THREE.Group(),staticRoot=new THREE.Group(),ladle=new THREE.Group();root.name='Entrance handwashing fountain';scene.add(root);root.add(staticRoot,ladle);ladle.position.copy(REST);scene.updateMatrixWorld(true);asset.updateMatrixWorld(true);
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 for(const o of meshes){const part=o.userData.handwashAssembly;if(part==='water'){o.removeFromParent();continue;}
  (part==='ladle'?ladle:staticRoot).attach(o);o.castShadow=o.receiveShadow=true;o.userData.waterSide='above';o.material.envMapIntensity=.45;
  if(o.material.name.includes('green bamboo')){o.material.color.set('#7b843f');o.material.roughness=.65;}
  if(o.material.name.includes('granite')&&stoneNormal){o.material.normalMap=stoneNormal;o.material.normalScale.set(.22,.22);}
  if(o.material.name.includes('hinoki')&&woodMap){o.material.map=woodMap;o.material.color.set('#ffffff');o.material.roughness=.45;}
  if(o.material.map)o.material.map.anisotropy=8;
 }
 const events=Array.from({length:16},()=>new THREE.Vector4(0,0,-100,0)),time={value:0};let next=0,rippleCount=0,lastRipple=-1,nextDrop=0,now=0;
 function ripple(x,z,amplitude=.009){events[next].set(x,z,now,amplitude);next=(next+1)%events.length;rippleCount++;}
 const waterMat=new THREE.MeshPhysicalMaterial({color:'#b4d5ce',roughness:.07,metalness:0,clearcoat:1,clearcoatRoughness:.06,transparent:true,opacity:.3,depthWrite:false,envMapIntensity:.8});
 waterMat.onBeforeCompile=s=>{s.uniforms.washRipples={value:events};s.uniforms.washTime=time;s.vertexShader=rippleCode+'\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <beginnormal_vertex>','#include <beginnormal_vertex>\nvec2 slope=washSlope(position.xz);objectNormal=normalize(vec3(-slope.x,1.,-slope.y));');s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.y+=washHeight(position.xz);');s.fragmentShader=s.fragmentShader.replace('#include <opaque_fragment>','diffuseColor.a=.18+.68*pow(1.-abs(dot(normal,normalize(vViewPosition))),3.);\n#include <opaque_fragment>');};waterMat.customProgramCacheKey=()=> 'handwash-causal-waves-v1';
 const water=new THREE.Mesh(disk(.53),waterMat);water.position.copy(CENTER);water.isWater=true;water.receiveShadow=true;root.add(water);
 const cupWater=new THREE.Mesh(new THREE.CircleGeometry(.096,48),waterMat.clone());cupWater.rotation.x=-Math.PI/2;cupWater.position.y=-.025;cupWater.visible=false;cupWater.userData.waterSide='above';ladle.add(cupWater);
 // Fine transparent jet and travelling droplets are actual local geometry.
 const jetMat=new THREE.MeshPhysicalMaterial({color:'#d9eee7',roughness:.11,metalness:.15,transparent:true,opacity:.43,depthWrite:false,clearcoat:1});
 const inlet=new THREE.Vector3(-3.90,1.70,15.41),impact=new THREE.Vector3(-3.87,1.23,15.47);
 const inletCurve=new THREE.QuadraticBezierCurve3(inlet,new THREE.Vector3(-3.85,1.49,15.47),impact);
 const inletJet=new THREE.Mesh(new THREE.TubeGeometry(inletCurve,30,.007,8,false),jetMat);root.add(inletJet);inletJet.userData.waterSide='above';
 const pourJet=new THREE.Mesh(new THREE.CylinderGeometry(.006,.003,1,9,1,true),jetMat);pourJet.visible=false;pourJet.userData.waterSide='above';root.add(pourJet);
 const drops=new THREE.InstancedMesh(new THREE.SphereGeometry(.005,6,4),jetMat,18);drops.instanceMatrix.setUsage(THREE.DynamicDrawUsage);drops.userData.waterSide='above';root.add(drops);drops.frustumCulled=false;
 const target=new THREE.Vector3(0,0,-.22),current=target.clone(),last=current.clone(),ray=new THREE.Raycaster(),plane=new THREE.Plane(new THREE.Vector3(0,1,0),-CENTER.y),point=new THREE.Vector3(),dummy=new THREE.Object3D(),up=new THREE.Vector3(0,1,0);
 const state=new HandwashMotion();let saved=null,pickup=0,moveCount=0,returning=null;
 const button=document.querySelector('#return-ladle');
 function publish(){button.dataset.state=JSON.stringify({held:state.held,phase:state.phase,water:Math.round(state.water*100),scoops:state.scoops,pours:state.pours,ripples:rippleCount,moves:moveCount,position:ladle.position.toArray()});}
 function take(){if(returning||!state.take())return false;saved={position:camera.position.clone(),target:controls.target.clone(),enabled:controls.enabled};pickup=0;target.set(0,0,-.22);current.copy(target);last.copy(target);controls.enabled=false;button.classList.remove('hidden');publish();return true;}
 function putBack(){if(!state.held)return;returning={from:ladle.position.clone(),rotation:ladle.quaternion.clone(),time:0};state.putBack();cupWater.visible=pourJet.visible=false;camera.position.copy(saved.position);controls.target.copy(saved.target);controls.enabled=saved.enabled;controls.update();button.classList.add('hidden');publish();}
 button.addEventListener('click',putBack);
 function move(mouse){if(!state.held||pickup<1||state.phase==='pour')return;ray.setFromCamera(mouse,camera);if(!ray.ray.intersectPlane(plane,point))return;point.sub(CENTER);const p=constrainLadleTarget(point.x,point.z);target.set(p.x,0,p.z);moveCount++;}
 function pick(mouse){if(state.held)return 'handwash-use';ray.setFromCamera(mouse,camera);root.updateMatrixWorld(true);return ray.intersectObjects([ladle,staticRoot],true).length?'handwash':null;}
 function click(){if(!state.click())return false;splash();ripple(current.x,current.z,.017);publish();return true;}
 function update(dt,t){now=t;time.value=t;state.update(dt);const was=pickup;pickup=Math.min(1,pickup+dt/.95);
  if(returning){returning.time+=dt;const u=Math.min(1,returning.time/.85),p=ladleTravel(returning.from,REST,u);ladle.position.set(p.x,p.y,p.z);ladle.quaternion.copy(returning.rotation).slerp(new THREE.Quaternion(),Math.min(1,u/.45));if(u===1)returning=null;}
  if(state.held){
   if(pickup<1||was<1){const e=pickup*pickup*(3-2*pickup);camera.position.lerpVectors(saved.position,new THREE.Vector3(-2.95,2.65,17.55),e);controls.target.lerpVectors(saved.target,new THREE.Vector3(-3.7,1.28,15.63),e);camera.lookAt(controls.target);}
   current.lerp(target,1-Math.exp(-dt*12));const pose=state.pose,side=Math.max(0,Math.min(1,pose.tilt/1.5));const goal=CENTER.clone().add(new THREE.Vector3(current.x*(1-side)-.24*side,.105+pose.lift,current.z*(1-side)-.24*side));const travel=ladleTravel(REST,goal,pickup);ladle.position.set(travel.x,travel.y,travel.z);const angles=ladleAngles(pose.tilt),orient=Math.min(1,pickup/.22);ladle.rotation.set(angles.x*orient,0,angles.z*orient);
   if((state.phase==='stir'||state.phase==='scoop')&&pickup===1&&current.distanceTo(last)>.026&&t-lastRipple>.055){ripple(current.x,current.z,.008+Math.min(.008,current.distanceTo(last)*.08));last.copy(current);lastRipple=t;}
   cupWater.visible=state.water>.02;cupWater.position.y=-.082+.059*state.water;cupWater.rotation.set(-Math.PI/2,pose.tilt*.35,0);cupWater.scale.setScalar(1-side*.45);
   const pouring=state.phase==='pour'&&state.water>.01&&state.time>.17;
   pourJet.visible=pouring;
   if(pouring){ladle.updateMatrixWorld(true);const lip=new THREE.Vector3(.112,-.006,0).applyMatrix4(ladle.matrixWorld),end=new THREE.Vector3(lip.x+.035,CENTER.y,lip.z),d=end.clone().sub(lip);pourJet.position.copy(lip).add(end).multiplyScalar(.5);pourJet.scale.set(Math.sqrt(state.water),d.length(),Math.sqrt(state.water));pourJet.quaternion.setFromUnitVectors(up,d.normalize());if(t-lastRipple>.095){ripple(end.x-CENTER.x,end.z-CENTER.z,.016*state.water);lastRipple=t;}}
  }
  if(t>nextDrop){ripple(impact.x-CENTER.x,impact.z-CENTER.z,.005);nextDrop=t+.55;}
  for(let i=0;i<18;i++){const f=(t*1.8+i/18)%1;dummy.position.copy(inletCurve.getPoint(f));dummy.position.x+=Math.sin(i*2.3+t*4)*.003;dummy.scale.set(.55,1.6,.55);dummy.updateMatrix();drops.setMatrixAt(i,dummy.matrix);}drops.instanceMatrix.needsUpdate=true;
  publish();
 }
 publish();return {root,staticRoot,ladle,water,take,putBack,move,pick,click,update,get held(){return state.held;},get stats(){return {phase:state.phase,held:state.held,scoops:state.scoops,pours:state.pours,ripples:rippleCount};}};
}
