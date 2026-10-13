// Not used by the production app: measured stone-detail experiment.
import * as THREE from 'three';
import {extractRegion} from '../dist/rituals.js';

export function stoneMaterial(source){
 const material=source.clone();material.name='Continuous granite with wet waterline';material.vertexColors=true;material.roughness=.88;material.envMapIntensity=.45;
 for(const key of ['map','normalMap','roughnessMap'])if(material[key])material[key].anisotropy=8;
 material.onBeforeCompile=shader=>{
  shader.vertexShader='varying vec3 vStoneWorld;varying vec3 vStoneWorldNormal;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
   vec4 stonePosition=vec4(transformed,1.);
   #ifdef USE_BATCHING
    stonePosition=batchingMatrix*stonePosition;
   #endif
   #ifdef USE_INSTANCING
    stonePosition=instanceMatrix*stonePosition;
   #endif
   vStoneWorld=(modelMatrix*stonePosition).xyz;
   vStoneWorldNormal=inverseTransformDirection(transformedNormal,viewMatrix);`);
  shader.fragmentShader='varying vec3 vStoneWorld;varying vec3 vStoneWorldNormal;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`
   vec3 stoneN=normalize(vStoneWorldNormal);
   vec3 stoneWeights=pow(abs(stoneN),vec3(4.));stoneWeights/=dot(stoneWeights,vec3(1.));
   vec3 stoneP=vStoneWorld*1.45;
   float stoneWet=1.-smoothstep(-.045,.09,vStoneWorld.y);
   #ifdef USE_MAP
    vec4 stoneColor=texture2D(map,stoneP.yz)*stoneWeights.x+texture2D(map,stoneP.xz)*stoneWeights.y+texture2D(map,stoneP.xy)*stoneWeights.z;
    diffuseColor*=stoneColor;
   #endif
   diffuseColor.rgb*=mix(1.,.52,stoneWet);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`
   float roughnessFactor=roughness;
   #ifdef USE_ROUGHNESSMAP
    float stoneRough=texture2D(roughnessMap,stoneP.yz).g*stoneWeights.x+texture2D(roughnessMap,stoneP.xz).g*stoneWeights.y+texture2D(roughnessMap,stoneP.xy).g*stoneWeights.z;
    roughnessFactor*=stoneRough;
   #endif
   roughnessFactor=mix(roughnessFactor,.26,stoneWet);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`
   #ifdef USE_NORMALMAP
    vec2 stoneNX=(texture2D(normalMap,stoneP.yz).xy*2.-1.)*.28;
    vec2 stoneNY=(texture2D(normalMap,stoneP.xz).xy*2.-1.)*.28;
    vec2 stoneNZ=(texture2D(normalMap,stoneP.xy).xy*2.-1.)*.28;
    vec3 detail=vec3(0.,stoneNX.x,stoneNX.y)*stoneWeights.x+vec3(stoneNY.x,0.,stoneNY.y)*stoneWeights.y+vec3(stoneNZ.x,stoneNZ.y,0.)*stoneWeights.z;
    vec3 worldNormal=normalize(stoneN+detail-stoneN*dot(detail,stoneN));
    normal=normalize((viewMatrix*vec4(worldNormal,0.)).xyz);
   #endif`);
 };
 material.customProgramCacheKey=()=> 'pond-stone-triplanar-v2';return material;
}

export function installPondStones(model,prototypes,layout,scene,{perStoneCulling=false,distant=null,errorBudget=.008,pixelLimit=.5}={}){
 let original;model.traverse(o=>{if(o.isMesh&&o.material.name==='Natural mossy bank stones')original=o.material;});
 if(!original)throw new Error('Missing original photographic stone material');
 const removed=extractRegion(model,n=>n==='Natural mossy bank stones'||n==='Soft forest moss',p=>(p.x/11.5)**2+((p.z-5.8)/6.9)**2<1.28&&p.y<1.15);
 removed.traverse(o=>o.geometry?.dispose());
 const material=stoneMaterial(original),dummy=new THREE.Object3D(),meshes=[],entries=[];prototypes.updateMatrixWorld(true);distant?.updateMatrixWorld(true);
 let mainCamera=null;const stats={distantStones:0,savedMainTriangles:0,perStoneCulling};
 for(let kind=0;kind<8;kind++){
  const source=prototypes.getObjectByName(`PondStone_${kind}`);if(!source?.isMesh)throw new Error(`Missing pond stone prototype ${kind}`);
  const placements=layout.placements.filter(p=>p[0]===kind),geometry=source.geometry.clone().applyMatrix4(source.matrixWorld);
  const lowSource=perStoneCulling?distant?.getObjectByName(`PondStoneDistant_${kind}`):null;
  const low=lowSource?.geometry.clone().applyMatrix4(lowSource.matrixWorld);
  const mesh=perStoneCulling?new THREE.BatchedMesh(placements.length,geometry.attributes.position.count+(low?.attributes.position.count??0),(geometry.index?.count??0)+(low?.index?.count??0),material):new THREE.InstancedMesh(geometry,material,placements.length);mesh.name=`Weathered pond stones ${kind}`;
  const fullId=perStoneCulling?mesh.addGeometry(geometry):null,lowId=low?mesh.addGeometry(low):fullId;
  // Keep submerged instances at the tail so reflections can shorten the same draw
  // without extra batches, reduced geometry, or uploading matrices every frame.
  geometry.computeBoundingBox();const reflected=[],submerged=[],bounds=new THREE.Box3();
  placements.forEach(([id,x,y,z,sx,sy,sz,rotation])=>{
   dummy.position.set(x,z,-y);dummy.rotation.set(0,rotation,0);dummy.scale.set(sx,sz,sy);dummy.updateMatrix();
   bounds.copy(geometry.boundingBox).applyMatrix4(dummy.matrix);
   (bounds.max.y<-.025-.005?submerged:reflected).push(dummy.matrix.clone());
  });
  const matrices=[...reflected,...submerged],instances=[];
  matrices.forEach((matrix,i)=>{const id=perStoneCulling?mesh.addInstance(fullId):i;mesh.setMatrixAt(id,matrix);instances.push({id,matrix,distant:false});});
  if(perStoneCulling){
   mesh.userData.waterReflectionIds=instances.slice(reflected.length).map(i=>i.id);mesh.userData.noAO=true;
   // Other cameras retain full geometry. BatchedMesh's shadow callback also
   // enters this hook, so shadow and refracted silhouettes remain unchanged.
   const before=mesh.onBeforeRender;
   mesh.onBeforeRender=function(renderer,currentScene,camera,...args){
    for(const instance of instances){const id=camera===mainCamera&&instance.distant?lowId:fullId;if(mesh.getGeometryIdAt(instance.id)!==id)mesh.setGeometryIdAt(instance.id,id);}
    before.call(this,renderer,currentScene,camera,...args);
   };
   const bounds=geometry.boundingBox.clone();if(low){low.computeBoundingBox();bounds.union(low.boundingBox);}
   entries.push({mesh,instances,bounds,fullTriangles:(geometry.index?.count??geometry.attributes.position.count)/3,lowTriangles:low?(low.index?.count??low.attributes.position.count)/3:0,hasLow:!!low});
   geometry.dispose();low?.dispose();
  }else mesh.userData.waterReflectionCount=reflected.length;
  // Submerged stones still block sunlight: omitting their shadows makes the
  // correctly seated gravel appear suspended above the sediment.
  mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.waterMotionPadding=.005;if(!reflected.length)mesh.userData.waterSide='below';mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);meshes.push(mesh);
  if(lowSource){const padding=errorBudget*Math.max(...matrices.map(m=>m.getMaxScaleOnAxis()));mesh.boundingBox.expandByScalar(padding);mesh.boundingSphere.radius+=padding;}
 }
 const world=new THREE.Matrix4(),view=new THREE.Matrix4(),box=new THREE.Box3();
 function update(camera,height){
  mainCamera=camera;camera.updateMatrixWorld();const focal=Math.abs(camera.projectionMatrix.elements[5])*height/2;stats.distantStones=stats.savedMainTriangles=0;
  for(const entry of entries){entry.mesh.updateWorldMatrix(true,false);for(const instance of entry.instances){
   if(!entry.hasLow)continue;world.multiplyMatrices(entry.mesh.matrixWorld,instance.matrix);view.multiplyMatrices(camera.matrixWorldInverse,world);box.copy(entry.bounds).applyMatrix4(view);
   const depth=-box.max.z,offAxis=Math.max(Math.abs(box.min.x),Math.abs(box.max.x),Math.abs(box.min.y),Math.abs(box.max.y)),error=errorBudget*world.getMaxScaleOnAxis();
   const projected=depth>error?focal*error/(depth-error)*(1+offAxis/depth):Infinity;
   if(projected>pixelLimit)instance.distant=false;else if(projected<pixelLimit*.8)instance.distant=true;
   if(instance.distant){stats.distantStones++;stats.savedMainTriangles+=entry.fullTriangles-entry.lowTriangles;}
  }}
  return stats;
 }
 return {count:layout.placements.length,meshes,entries,stats,update,perStoneCulling};
}
