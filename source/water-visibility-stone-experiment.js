// Not used by the production app: measured stone-detail experiment.
import * as THREE from 'three';

// Classification is conservative: objects crossing the surface stay in both captures.
// Dynamic schools/leaves declare their side; static geometry uses world-space bounds.
export function createWaterVisibility(scene,height){
 const above=[],below=[],partial=[],instances=[],batched=[],box=new THREE.Box3(),users=new Map();
 scene.updateMatrixWorld(true);
 scene.traverse(o=>{if(o.isMesh)users.set(o.geometry,(users.get(o.geometry)||0)+1);});
 scene.traverse(object=>{
  if(!object.isMesh||object.isWater)return;
  if(object.isBatchedMesh&&Array.isArray(object.userData.waterReflectionIds))batched.push(object);
  if(object.isInstancedMesh&&Number.isInteger(object.userData.waterReflectionCount)&&object.userData.waterReflectionCount>=0&&object.userData.waterReflectionCount<object.count)instances.push(object);
  let side=object.userData.waterSide;
  if(!side&&object.frustumCulled!==false){
   if(object.isInstancedMesh||object.isBatchedMesh){object.computeBoundingBox();box.copy(object.boundingBox);}
   else {object.geometry.computeBoundingBox();box.copy(object.geometry.boundingBox);}
   box.applyMatrix4(object.matrixWorld);
   // Static masonry has no wind. Keep a wider bound for shader-deformed plants.
   const padding=object.userData.waterMotionPadding??(object.isInstancedMesh?.25:.01);
   if(box.min.y>height+padding)side='above';
   else if(box.max.y<height-padding)side='below';
   object.userData.waterClipBounds=[box.min.y,box.max.y,height,padding,side??'crossing'];
  }
  if(side==='above')above.push(object);else if(side==='below')below.push(object);
  else if(object.userData.waterClipStatic&&!object.isInstancedMesh&&!object.isBatchedMesh&&!object.isSkinnedMesh&&users.get(object.geometry)===1){
   const geometry=object.geometry,position=geometry.attributes.position,index=geometry.index;
   if(geometry.groups.length||geometry.drawRange.start||Number.isFinite(geometry.drawRange.count)||geometry.morphAttributes.position?.length)return;
   const top=[],bottom=[],m=object.matrixWorld.elements;
   for(let i=0;i<(index?.count??position.count);i+=3){
    const ids=[0,1,2].map(k=>index?index.getX(i+k):i+k);
    const heights=ids.map(id=>m[1]*position.getX(id)+m[5]*position.getY(id)+m[9]*position.getZ(id)+m[13]);
    if(Math.max(...heights)>=height-.01)top.push(...ids);
    if(Math.min(...heights)<=height+.01)bottom.push(...ids);
   }
   const IndexArray=position.count>65535?Uint32Array:Uint16Array;
   partial.push({object,geometry,reflection:new THREE.BufferAttribute(new IndexArray(top),1),refraction:new THREE.BufferAttribute(new IndexArray(bottom),1)});
  }
 });
 function capture(mode){
  const hidden=[],indices=[],counts=[],instanceVisibility=[];
  for(const object of mode==='refraction'?above:below){if(object.visible){hidden.push(object);object.visible=false;}}
  // Crossing faces are retained in both passes; only wholly clipped faces leave the draw list.
  for(const item of partial){if(!item.object.visible)continue;indices.push([item.geometry,item.geometry.index]);item.geometry.setIndex(item[mode]);}
  if(mode==='reflection')for(const object of instances){if(!object.visible)continue;counts.push([object,object.count]);object.count=Math.min(object.count,object.userData.waterReflectionCount);}
  if(mode==='reflection')for(const object of batched){if(!object.visible)continue;for(const id of object.userData.waterReflectionIds){if(object.getVisibleAt(id)){instanceVisibility.push([object,id]);object.setVisibleAt(id,false);}}}
  return ()=>{for(const [object,id]of instanceVisibility)object.setVisibleAt(id,true);for(const [object,count]of counts)object.count=count;for(const [geometry,index]of indices)geometry.setIndex(index);for(const object of hidden)object.visible=true;};
 }
 return {capture,above:above.length,below:below.length,splitMeshes:partial.length};
}
