import * as THREE from 'three';

// Keep the capture's projection and texel density unchanged. Only pixels/objects
// outside the projected pond (plus a conservative normal-distortion margin) leave.
export function createWaterCaptureRegion(water,scene){
 const worldPoints=[];
 water.geometry.computeBoundingBox();water.updateWorldMatrix(true,false);
 const regions=water.geometry.userData.surfaceRegions??[water.geometry.boundingBox];
 // Capture the whole animated height envelope, not just the undeformed plane.
 // Regional boxes also avoid projecting tens of thousands of water vertices.
 const displacement=water.userData.surfaceDisplacement??0;
 for(const region of regions){
  const box=region.clone().applyMatrix4(water.matrixWorld);box.min.y-=displacement;box.max.y+=displacement;
  for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])worldPoints.push(new THREE.Vector3(x,y,z));
 }
 const entries=[],vp=new THREE.Matrix4(),crop=new THREE.Matrix4(),frustum=new THREE.Frustum(),point=new THREE.Vector4();
 scene.updateMatrixWorld(true);
 scene.traverse(o=>{
  if(!o.isMesh||o.isWater||o.frustumCulled===false||o.isSkinnedMesh||o.geometry.morphAttributes.position?.length)return;
  if(o.isInstancedMesh||o.isBatchedMesh)o.computeBoundingBox();else o.geometry.computeBoundingBox();
  const local=(o.isInstancedMesh||o.isBatchedMesh?o.boundingBox:o.geometry.boundingBox).clone().expandByScalar(o.userData.waterMotionPadding??.55);
  entries.push({object:o,local,world:new THREE.Box3()});
 });
 const stats={reflection:{},refraction:{}};
 function capture(mode,camera,target){
  vp.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
  let minX=1,minY=1,maxX=-1,maxY=-1,conservative=false;
  for(const p of worldPoints){
   point.set(p.x,p.y,p.z,1).applyMatrix4(vp);
   // The pond crosses the eye plane: retaining the full target is safe.
   if(point.w<=.001){conservative=true;break;}
   const x=point.x/point.w,y=point.y/point.w;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
  }
  if(conservative){minX=minY=-1;maxX=maxY=1;}
  const margin=.06; // .03 UV reserve covers the .018 reflection distortion plus filtering.
  minX=Math.max(-1,minX-margin);maxX=Math.min(1,maxX+margin);minY=Math.max(-1,minY-margin);maxY=Math.min(1,maxY+margin);
  if(maxX<=minX||maxY<=minY)return ()=>{};
  const x=Math.floor((minX+1)*.5*target.width),y=Math.floor((minY+1)*.5*target.height);
  const right=Math.ceil((maxX+1)*.5*target.width),top=Math.ceil((maxY+1)*.5*target.height);
  const previous=target.scissor.clone(),test=target.scissorTest;
  target.scissor.set(x,y,right-x,top-y);target.scissorTest=true;
  // A cropped culling frustum, never a modified rendering projection.
  crop.set(2/(maxX-minX),0,0,-(maxX+minX)/(maxX-minX),0,2/(maxY-minY),0,-(maxY+minY)/(maxY-minY),0,0,1,0,0,0,0,1);
  frustum.setFromProjectionMatrix(crop.multiply(vp),camera.coordinateSystem);
  const hidden=[];
  for(const e of entries){
   if(mode==='refraction')break; // Original bounds do not describe the bent projection.
   if(!e.object.visible)continue;
   e.world.copy(e.local).applyMatrix4(e.object.matrixWorld);
   if(!frustum.intersectsBox(e.world)){e.object.visible=false;hidden.push(e.object);}
  }
  stats[mode]={pixelFraction:Math.round((right-x)*(top-y)/(target.width*target.height)*1000)/1000,culledMeshes:hidden.length,fullCapture:conservative};
  return ()=>{for(const o of hidden)o.visible=true;target.scissor.copy(previous);target.scissorTest=test;};
 }
 return {capture,stats};
}
