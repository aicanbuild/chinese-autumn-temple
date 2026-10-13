import * as THREE from 'three';

const EPS=.0002;
// Swept point versus expanded furniture boxes. Retain tangential motion on contact.
export function sweepHallCamera(start,desired,boxes){
 const point=start.clone(),remaining=desired.clone().sub(start),normal=new THREE.Vector3();
 // Recover a camera restored inside a newly loaded collision proxy.
 for(let pass=0;pass<boxes.length+1;pass++){
  let moved=false;
  for(const box of boxes){
   if(!box.containsPoint(point))continue;
   let distance=Infinity,axis='x',value=0;
   for(const a of ['x','y','z'])for(const [edge,sign]of [[box.min[a],-1],[box.max[a],1]]){
    const d=Math.abs(edge-point[a]);if(d<distance){distance=d;axis=a;value=edge+sign*EPS;}
   }
   point[axis]=value;moved=true;
  }
  if(!moved)break;
 }
 remaining.copy(desired).sub(point);
 for(let iteration=0;iteration<6&&remaining.lengthSq()>1e-12;iteration++){
  let earliest=1,hit=false;
  for(const box of boxes){
   let enter=-Infinity,exit=Infinity,axis=null,sign=0,miss=false;
   for(const a of ['x','y','z']){
    if(Math.abs(remaining[a])<1e-12){if(point[a]<box.min[a]||point[a]>box.max[a]){miss=true;break;}continue;}
    let lo=(box.min[a]-point[a])/remaining[a],hi=(box.max[a]-point[a])/remaining[a],s=-1;
    if(lo>hi){[lo,hi]=[hi,lo];s=1;}
    if(lo>enter){enter=lo;axis=a;sign=s;}exit=Math.min(exit,hi);
   }
   if(miss||enter>exit||exit<0||enter<0||enter>earliest||enter>1||!axis)continue;
   earliest=enter;normal.set(0,0,0);normal[axis]=sign;hit=true;
  }
  if(!hit){point.add(remaining);break;}
  point.addScaledVector(remaining,earliest).addScaledVector(normal,EPS);
  remaining.multiplyScalar(1-earliest);const into=remaining.dot(normal);if(into<0)remaining.addScaledVector(normal,-into);
 }
 return point;
}

export function createHallCamera(camera,controls,surfaceAt){
 let layout={cameraRadius:.16,targetMin:[-5.15,1.55,-10.02],targetMax:[5.15,5.6,-4.4],cameraMin:[-5.08,1.92,-9.95],cameraMax:[5.08,4,-4.02],boxes:[]};
 let boxes=[],radius=-1,previous=null,previousTarget=null;
 const stats={contacts:0,proxies:0};
 function setLayout(value){layout=value;radius=-1;previous=null;previousTarget=null;stats.proxies=layout.boxes.length;}
 function reset(){previous=previousTarget=null;}
 function constrain(){
  const targetBefore=controls.target.clone(),targetMin=new THREE.Vector3().fromArray(layout.targetMin),targetMax=new THREE.Vector3().fromArray(layout.targetMax);
  controls.target.clamp(targetMin,targetMax);camera.position.add(controls.target.clone().sub(targetBefore));
  // Enclose the near-plane corners as well as the lens, including wide screens.
  const corner=camera.near*Math.sqrt(1+Math.tan(THREE.MathUtils.degToRad(camera.fov/2))**2*(1+camera.aspect**2));
  const nextRadius=Math.max(layout.cameraRadius,corner+.015);
  if(Math.abs(nextRadius-radius)>1e-6){radius=nextRadius;boxes=layout.boxes.map(b=>new THREE.Box3(new THREE.Vector3().fromArray(b.min),new THREE.Vector3().fromArray(b.max)).expandByScalar(radius));}
  const lower=new THREE.Vector3().fromArray(layout.cameraMin),upper=new THREE.Vector3().fromArray(layout.cameraMax);
  const extra=Math.max(0,radius-layout.cameraRadius);lower.x+=extra;lower.z+=extra;upper.x-=extra;upper.z-=extra;upper.y-=extra;
  const floor=surfaceAt(THREE.MathUtils.clamp(camera.position.x,lower.x,upper.x),THREE.MathUtils.clamp(camera.position.z,lower.z,upper.z));lower.y=Math.max(lower.y,floor+Math.max(.85,radius));
  const attempted=camera.position.clone(),desired=attempted.clone().clamp(lower,upper);if(desired.z> -5.35)desired.y=Math.min(desired.y,3.78-extra);
  const initial=previous??desired;
  const resolved=sweepHallCamera(initial,desired,boxes).clamp(lower,upper);if(resolved.z> -5.35)resolved.y=Math.min(resolved.y,3.78-extra);
  const correction=resolved.clone().sub(attempted);if(correction.lengthSq()>1e-9)stats.contacts++;
  // While panning, slide the look-at point with the lens to avoid an unintended turn.
  if(previousTarget&&controls.target.distanceToSquared(previousTarget)>1e-10)controls.target.add(correction).clamp(targetMin,targetMax);
  camera.position.copy(resolved);camera.lookAt(controls.target);
  previous=resolved.clone();previousTarget=controls.target.clone();return correction.lengthSq()>1e-9;
 }
 return {setLayout,reset,constrain,stats};
}
