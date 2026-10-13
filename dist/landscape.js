import {applyFoliageLighting} from './foliage-lighting.js';
import {applyWoodlandWind,createWindShadows} from './foliage-wind.js';
import * as THREE from 'three';

// Spatial batches retain independent culling; each prototype owns one GPU geometry
// and material shared across its groves, instead of uploading identical copies.
export function createLandscape(terrain,woodland,layout,scene,{perTreeCulling=false}={}){
 const wind={value:0},transform=new THREE.Object3D(),batches=[];
 terrain.name='Blender sculpted forest terrain';
 // This dry-land asset has a pond cutout and raised banks. Remote valleys below
 // the pond's elevation are not submerged; refracting them can fold triangles
 // behind the eye into the foreground capture and cover the actual pond bed.
 terrain.traverse(o=>{if(o.isMesh){o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';o.material.roughness=.94;o.material.envMapIntensity=.35;for(const key of ['map','normalMap'])if(o.material[key])o.material[key].anisotropy=8;}});
 scene.add(terrain);woodland.updateMatrixWorld(true);
 for(let species=0;species<3;species++)for(let lod=0;lod<2;lod++){
  const root=woodland.getObjectByName(`Woodland_${species}_${lod}`);
  if(!root)throw new Error(`Missing woodland prototype ${species}/${lod}`);
  const trees=layout.trees.filter(p=>p[5]===species&&p[6]===lod);
  const groves=new Map();for(const p of trees){const key=`${Math.floor(p[0]/40)},${Math.floor(p[1]/40)}`;if(!groves.has(key))groves.set(key,[]);groves.get(key).push(p);}
  root.traverse(part=>{
   if(!part.isMesh||!trees.length)return;
   const geometry=part.geometry.clone().applyMatrix4(part.matrixWorld),material=part.material.clone();
   const leaves=part.name.startsWith('Leaves_');
   material.envMapIntensity=.35;material.roughness=.91;
   for(const key of ['map','normalMap'])if(material[key])material[key].anisotropy=8;
   if(leaves){
    material.transparent=false;material.depthWrite=true;material.alphaTest=.42;material.side=THREE.DoubleSide;material.forceSinglePass=true;
    material.onBeforeCompile=shader=>applyWoodlandWind(shader,wind);
    material.customProgramCacheKey=()=> 'woodland-wind-3';
    applyFoliageLighting(material,species===0?.20:.25);
   }
   const shadows=leaves?createWindShadows(material,wind,applyWoodlandWind,'woodland'):null;
   geometry.computeBoundingBox();
   const windPadding=leaves?Math.hypot(.035*Math.max(0,geometry.boundingBox.max.y-2),.045):0;
   // BatchedMesh culls each instance using prototype bounds. Include the entire
   // shader wind excursion before copying these bounds into its geometry slot.
   if(perTreeCulling){geometry.computeBoundingSphere();geometry.boundingBox.expandByScalar(windPadding);geometry.boundingSphere.radius+=windPadding;}
   let sharedBatchGeometry;
   for(const positions of groves.values()){
   const mesh=perTreeCulling?new THREE.BatchedMesh(positions.length,geometry.attributes.position.count,geometry.index?.count??0,material):new THREE.InstancedMesh(geometry,material,positions.length);
   const geometryId=perTreeCulling?mesh.addGeometry(geometry):null;if(perTreeCulling){mesh.sortObjects=false;mesh.userData.noAO=true;}
   // Every grove has the identical immutable geometry slot (ID 0, offset 0).
   // Share its public BufferGeometry just as the InstancedMesh path does;
   // each grove retains its own instance textures, visibility and draw lists.
   // These static groves share one scene lifetime: do not edit geometry slots
   // or dispose an individual grove while siblings still use this buffer.
   if(perTreeCulling){if(sharedBatchGeometry){const duplicate=mesh.geometry;mesh.geometry=sharedBatchGeometry;duplicate.dispose();}else sharedBatchGeometry=mesh.geometry;}
   mesh.name=`Woodland ${species}/${lod} ${leaves?'leaves':'branches'}`;mesh.userData.treeInstances=positions.length;
   mesh.userData.waterReflection=false;
   positions.forEach(([x,y,z,scale,rotation],i)=>{transform.position.set(x,z,-y);transform.rotation.set(0,rotation,0);transform.scale.setScalar(scale);transform.updateMatrix();mesh.setMatrixAt(perTreeCulling?mesh.addInstance(geometryId):i,transform.matrix);});
   mesh.castShadow=positions.some(p=>Math.hypot(p[0],p[1])<38);mesh.receiveShadow=true;if(!leaves)mesh.userData.waterMotionPadding=.005;mesh.computeBoundingBox();mesh.computeBoundingSphere();
   if(shadows){mesh.customDepthMaterial=shadows.depth;mesh.customDistanceMaterial=shadows.distance;const padding=windPadding*Math.max(...positions.map(p=>p[3]));if(!perTreeCulling)mesh.boundingSphere.radius+=padding;mesh.userData.waterMotionPadding=padding;}
   scene.add(mesh);batches.push(mesh);
   }
   if(perTreeCulling)geometry.dispose();
  });
 }
 return {trees:layout.trees.length,batches,perTreeCulling,update(time){wind.value=time;}};
}
