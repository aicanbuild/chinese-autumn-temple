import * as THREE from 'three';

export function pondShadowSlope(direction,index=1.333,out=new THREE.Vector2()){
 const d=direction.clone().normalize(),airY=Math.max(d.y,.05),waterY=Math.sqrt(Math.max(.001,1-(d.x*d.x+d.z*d.z)/(index*index)));
 return out.set(-d.x/airY+d.x/(index*waterY),-d.z/airY+d.z/(index*waterY));
}
export function refractedShadowPoint(point,direction,height=-.025,out=new THREE.Vector3()){
 out.copy(point);const depth=Math.max(0,height-point.y),delta=pondShadowSlope(direction);out.x+=depth*delta.x;out.z+=depth*delta.y;return out;
}
const functions=`
uniform vec2 pondShadowShift;
uniform vec2 pondShadowWaterSlope;
uniform float pondShadowLevel;
uniform float pondShadowEnabled;
uniform mat4 pondSunShadowMatrix;
vec3 pondShadowPoint(vec3 point){
 float depth=max(0.,pondShadowLevel-point.y);
 vec2 entry=point.xz-depth*pondShadowWaterSlope;
 float inPond=step(length(vec2(entry.x/11.48,(entry.y-5.8)/6.88)),1.);
 point.xz+=pondShadowShift*depth*pondShadowEnabled*inPond;return point;
}
bool isPondSunMatrix(mat4 candidate){
 return distance(candidate[0],pondSunShadowMatrix[0])+distance(candidate[1],pondSunShadowMatrix[1])+distance(candidate[2],pondSunShadowMatrix[2])+distance(candidate[3],pondSunShadowMatrix[3])<.00001;
}`;

export function installPondShadows(scene,sun,{height=-.025}={}){
 const uniforms={pondShadowShift:{value:new THREE.Vector2()},pondShadowWaterSlope:{value:new THREE.Vector2()},pondShadowLevel:{value:height},pondShadowEnabled:{value:1},pondSunShadowMatrix:{value:sun.shadow.matrix}};
 const origin=new THREE.Vector3(),target=origin.clone(),direction=origin.clone(),box=new THREE.Box3(),materials=new Set(),casters=[],bounds=[];
 function update(){sun.getWorldPosition(origin);sun.target.getWorldPosition(target);direction.subVectors(origin,target).normalize();pondShadowSlope(direction,1.333,uniforms.pondShadowShift.value);const y=Math.sqrt(Math.max(.001,1-(direction.x**2+direction.z**2)/1.333**2));uniforms.pondShadowWaterSlope.value.set(-direction.x/(1.333*y),-direction.z/(1.333*y));
  for(const b of bounds){const padding=b.depth*uniforms.pondShadowShift.value.length();b.object.userData.refractedShadowPadding=padding;b.sphere.radius=b.radius+(padding+b.motion)/b.scale;}
 }
 update();scene.updateMatrixWorld(true);
 scene.traverse(o=>{
  if(!o.isMesh||o.isWater||o.userData.waterSide==='above'||o.userData.waterClipBounds?.[4]==='above')return;
  if(o.isInstancedMesh||o.isBatchedMesh){o.computeBoundingBox();box.copy(o.boundingBox);}else{o.geometry.computeBoundingBox();box.copy(o.geometry.boundingBox);}box.applyMatrix4(o.matrixWorld);
  if(box.min.y>=height||box.max.x< -11.48||box.min.x>11.48||box.max.z< -1.08||box.min.z>12.68)return;
  for(const material of Array.isArray(o.material)?o.material:[o.material]){
   if(!material||materials.has(material)||!material.isMeshStandardMaterial)continue;materials.add(material);
   const previous=material.onBeforeCompile,key=material.customProgramCacheKey();material.onBeforeCompile=function(shader,renderer){previous.call(this,shader,renderer);Object.assign(shader.uniforms,uniforms);shader.vertexShader=functions+'\n'+shader.vertexShader;
    const chunk=THREE.ShaderChunk.shadowmap_vertex.replace('vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;',`if(isPondSunMatrix(directionalShadowMatrix[i]))shadowWorldPosition.xyz=pondShadowPoint(shadowWorldPosition.xyz);
     vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;`);
    shader.vertexShader=shader.vertexShader.replace('#include <shadowmap_vertex>',chunk);
   };material.customProgramCacheKey=()=>key+'|pond-refracted-shadows-v1';material.needsUpdate=true;
  }
  if(!o.castShadow)return;
  const originalDepth=o.customDepthMaterial,before=o.onBeforeShadow,after=o.onAfterShadow;
  const depth=originalDepth?.clone()??new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking}),previous=originalDepth?.onBeforeCompile??depth.onBeforeCompile,key=originalDepth?.customProgramCacheKey()??depth.customProgramCacheKey(),pass={value:0};
  depth.onBeforeCompile=function(shader,renderer){previous.call(this,shader,renderer);Object.assign(shader.uniforms,uniforms,{pondShadowPass:pass});shader.vertexShader=functions+'\nuniform float pondShadowPass;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
    if(pondShadowPass>.5){
     vec4 pondCaster=vec4(transformed,1.);
     #ifdef USE_BATCHING
      pondCaster=batchingMatrix*pondCaster;
     #endif
     #ifdef USE_INSTANCING
      pondCaster=instanceMatrix*pondCaster;
     #endif
     pondCaster=modelMatrix*pondCaster;
     mvPosition=viewMatrix*vec4(pondShadowPoint(pondCaster.xyz),1.);
     gl_Position=projectionMatrix*mvPosition;
    }`);
  };depth.customProgramCacheKey=()=>key+'|pond-refracted-shadow-depth-v1';depth.needsUpdate=true;o.customDepthMaterial=depth;
  const stack=[];o.onBeforeShadow=function(renderer,object,camera,shadowCamera,...args){before.call(this,renderer,object,camera,shadowCamera,...args);stack.push(pass.value);pass.value=shadowCamera===sun.shadow.camera?1:0;};
  o.onAfterShadow=function(...args){pass.value=stack.pop()??0;after.apply(this,args);};
  // Only our stationary depth transform is safe for the static sunlight cache.
  if(!originalDepth&&before===THREE.Object3D.prototype.onBeforeShadow&&after===THREE.Object3D.prototype.onAfterShadow)o.userData.pondStaticShadow={depth,before:o.onBeforeShadow,after:o.onAfterShadow,state:()=>[height,...uniforms.pondShadowShift.value.toArray(),uniforms.pondShadowEnabled.value]};
  // Shifted shadow geometry needs conservative bounds before shadow culling.
  const padding=Math.max(0,height-box.min.y)*uniforms.pondShadowShift.value.length();o.userData.refractedShadowPadding=padding;
  const scale=Math.max(.0001,o.matrixWorld.getMaxScaleOnAxis()),motion=(o.userData.waterMotionPadding??0)*scale;
  if(o.isInstancedMesh||o.isBatchedMesh)o.computeBoundingSphere();else o.geometry.computeBoundingSphere();
  const sphere=o.isInstancedMesh||o.isBatchedMesh?o.boundingSphere:o.geometry.boundingSphere;bounds.push({object:o,sphere,radius:sphere.radius,scale,motion,depth:Math.max(0,height-box.min.y)});sphere.radius+=(padding+motion)/scale;
  casters.push(o);
 });
 return {uniforms,casters,materials:materials.size,update,set enabled(value){uniforms.pondShadowEnabled.value=value?1:0;},get enabled(){return uniforms.pondShadowEnabled.value===1;}};
}
