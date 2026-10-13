import {applyFoliageLighting} from './foliage-lighting.js';
import * as THREE from 'three';

// Small spatial groves keep the opaque leaf geometry out of unrelated views.
export function installUnderstory(asset,layout,scene){
 asset.updateMatrixWorld(true);
 const batches=[],transform=new THREE.Object3D();
 for(let variant=0;variant<layout.variants;variant++){
  const root=asset.getObjectByName(`Understory_${variant}`);
  if(!root)throw new Error(`Missing understory prototype ${variant}`);
  const groves=new Map();
  for(const p of layout.shrubs.filter(p=>p[5]===variant)){
   const key=`${Math.floor(p[0]/40)},${Math.floor(p[1]/40)}`;
   if(!groves.has(key))groves.set(key,[]);groves.get(key).push(p);
  }
  for(const positions of groves.values())root.traverse(part=>{
   if(!part.isMesh)return;
   const geometry=part.geometry.clone().applyMatrix4(part.matrixWorld),material=part.material.clone();
   material.envMapIntensity=.42;material.side=THREE.DoubleSide;material.transparent=false;material.alphaTest=0;material.forceSinglePass=true;
   for(const key of ['map','normalMap'])if(material[key])material[key].anisotropy=8;
   if(part.name.includes('leaves'))applyFoliageLighting(material,.16);
   const mesh=new THREE.InstancedMesh(geometry,material,positions.length);
   mesh.name=`Understory ${variant} ${part.name.includes('leaves')?'leaves':'twigs'}`;
   positions.forEach(([x,y,z,scale,rotation],i)=>{transform.position.set(x,z,-y);transform.rotation.set(0,rotation,0);transform.scale.setScalar(scale);transform.updateMatrix();mesh.setMatrixAt(i,transform.matrix);});
   mesh.castShadow=positions.some(p=>Math.hypot(p[0],p[1])<32);mesh.receiveShadow=true;mesh.userData.waterReflection=false;mesh.userData.waterClipStatic=true;mesh.userData.waterMotionPadding=.005;
   mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);batches.push(mesh);
  });
 }
 return {shrubs:layout.shrubs.length,batches};
}
