import {applyFoliageLighting} from './foliage-lighting.js';
import * as THREE from 'three';

// Reuse the existing shrub and fern assets in small, independently culled groves.
export function installForestEdge(shrubs,ferns,layout,scene,{perPlantCulling=false}={}){
 shrubs.updateMatrixWorld(true);ferns.updateMatrixWorld(true);
 const batches=[],up=new THREE.Vector3(0,1,0),normal=new THREE.Vector3(),yaw=new THREE.Quaternion(),transform=new THREE.Object3D();
 for(const kind of ['shrub','fern'])for(let variant=0;variant<(kind==='shrub'?3:4);variant++){
  const rows=layout.plants.filter(p=>p[5]===kind&&p[6]===variant);if(!rows.length)continue;
  const root=kind==='shrub'?shrubs.getObjectByName(`Understory_${variant}`):ferns.getObjectByName(layout.fernNames[variant]);
  if(!root)throw new Error(`Missing forest edge prototype ${kind}/${variant}`);
  const groves=new Map();for(const p of rows){const key=perPlantCulling?'all':`${Math.floor(p[0]/14)},${Math.floor(p[1]/14)}`;if(!groves.has(key))groves.set(key,[]);groves.get(key).push(p);}
  root.traverse(part=>{
   if(!part.isMesh)return;
   const geometry=part.geometry.clone().applyMatrix4(part.matrixWorld),material=part.material.clone();
   if(kind==='fern'){
    geometry.computeBoundingBox();const b=geometry.boundingBox,c=b.getCenter(new THREE.Vector3()),width=b.max.x-b.min.x;geometry.translate(-c.x,-b.min.y,-c.z);geometry.scale(1/width,1/width,1/width);
    material.color.set('#b3bd83');material.roughness=.9;material.alphaTest=.5;
   }
   material.envMapIntensity=kind==='fern'?.2:.42;material.side=THREE.DoubleSide;material.transparent=false;material.depthWrite=true;material.forceSinglePass=true;
   for(const key of ['map','normalMap'])if(material[key])material[key].anisotropy=8;
   if(kind==='fern'||part.name.includes('leaves'))applyFoliageLighting(material,kind==='fern'?.27:.16);
   let sharedGeometry;
   for(const positions of groves.values()){
    const mesh=perPlantCulling?new THREE.BatchedMesh(positions.length,geometry.attributes.position.count,geometry.index?.count??0,material):new THREE.InstancedMesh(geometry,material,positions.length);
    const slot=perPlantCulling?mesh.addGeometry(geometry):null;
    if(perPlantCulling){mesh.sortObjects=false;mesh.userData.noAO=true;if(sharedGeometry){const duplicate=mesh.geometry;mesh.geometry=sharedGeometry;duplicate.dispose();}else sharedGeometry=mesh.geometry;}
    positions.forEach(([x,y,z,s,rotation,type,id,nx,ny,nz],i)=>{
     transform.position.set(x,z,-y);normal.set(nx,nz,-ny).normalize();transform.quaternion.setFromUnitVectors(up,normal);yaw.setFromAxisAngle(up,rotation);transform.quaternion.multiply(yaw);transform.scale.setScalar(s);transform.updateMatrix();mesh.setMatrixAt(perPlantCulling?mesh.addInstance(slot):i,transform.matrix);
    });
    mesh.name=`Forest edge ${kind}/${variant}`;mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.waterReflection=kind!=='shrub';mesh.userData.waterClipStatic=true;mesh.userData.waterSide='above';mesh.userData.waterMotionPadding=.005;mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);batches.push(mesh);
   }
   if(perPlantCulling)geometry.dispose();
  });
 }
 return {plants:layout.plants.length,batches,perPlantCulling};
}
