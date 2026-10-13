import * as THREE from 'three';
import {extractRegion} from './rituals.js';

export function installPineCrowns(model,near,far,scene){
 const pairs=[];near.updateMatrixWorld(true);far.updateMatrixWorld(true);
 near.traverse(o=>{if(!o.isMesh)return;const distant=far.getObjectByName(o.name);if(!distant?.isMesh)throw new Error(`Missing pine LOD ${o.name}`);pairs.push([o,distant]);});
 if(pairs.length!==12)throw new Error('Expected six pairs of pine needle and twig meshes');
 const removed=extractRegion(model,n=>n==='Deep green pine needles',p=>p.z>-2,ps=>ps.every(p=>p.z>-2));let oldTriangles=0;
 removed.traverse(o=>{if(o.isMesh){oldTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 const root=new THREE.Group();root.name='Branch-attached pine needle crowns';const levels=[];
 for(const [o,distant] of pairs){
  const nearGeometry=o.geometry.clone().applyMatrix4(o.matrixWorld);nearGeometry.computeBoundingBox();const center=nearGeometry.boundingBox.getCenter(new THREE.Vector3());nearGeometry.translate(-center.x,-center.y,-center.z);
  const farGeometry=distant.geometry.clone().applyMatrix4(distant.matrixWorld).translate(-center.x,-center.y,-center.z);
  const material=o.material.clone();material.envMapIntensity=.40;material.side=THREE.DoubleSide;
  const lod=new THREE.LOD();lod.autoUpdate=false;lod.position.copy(center);
  for(const [geometry,distance]of [[nearGeometry,0],[farGeometry,22]]){const mesh=new THREE.Mesh(geometry,material);mesh.name=o.name;mesh.userData.waterReflection=false;mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.waterMotionPadding=.003;lod.addLevel(mesh,distance,.15);}
  root.add(lod);levels.push(lod);
 }scene.add(root);root.updateMatrixWorld(true);
 return {oldTriangles,levels,update(camera){for(const lod of levels)lod.update(camera);}};
}
