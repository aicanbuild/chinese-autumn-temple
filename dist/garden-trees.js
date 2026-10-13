import * as THREE from 'three';
import {applyBarkJunctions} from './bark-junctions.js';

export function installGardenTrees(model,trees,distant,scene){
 let source;const originals=[];
 model.traverse(o=>{if(o.isMesh&&o.material?.name==='Ridged maple bark'){source=o.material;originals.push(o);}});
 if(!source)throw new Error('Missing shared bark material for specimen trees');
 const material=source.clone();material.name='Curved specimen tree bark';material.roughness=.91;material.envMapIntensity=.35;
 if(material.normalMap)material.normalScale.setScalar(.38);
 for(const key of ['map','normalMap','roughnessMap'])if(material[key])material[key].anisotropy=8;
 const root=new THREE.Group(),levels=[];let count=0,blendedTrunks=0,blendedMaterial;trees.updateMatrixWorld(true);distant.updateMatrixWorld(true);
 trees.traverse(o=>{
  if(!o.isMesh)return;const far=distant.getObjectByName(o.name);if(!far?.isMesh)throw new Error(`Missing distant tree part ${o.name}`);
  const nearGeometry=o.geometry.clone().applyMatrix4(o.matrixWorld);nearGeometry.computeBoundingBox();
  const center=nearGeometry.boundingBox.getCenter(new THREE.Vector3());nearGeometry.translate(-center.x,-center.y,-center.z);
  const farGeometry=far.geometry.clone().applyMatrix4(far.matrixWorld).translate(-center.x,-center.y,-center.z);
  let treeMaterial=material;
  if(nearGeometry.hasAttribute('_bark_blend')){
   if(!farGeometry.hasAttribute('_bark_blend'))throw new Error(`Missing distant bark blend for ${o.name}`);
   for(const g of [nearGeometry,farGeometry])g.setAttribute('barkBlend',g.getAttribute('_bark_blend'));
   blendedMaterial??=applyBarkJunctions(material.clone());treeMaterial=blendedMaterial;blendedTrunks++;
  }
  const lod=new THREE.LOD();lod.autoUpdate=false;lod.position.copy(center);
  for(const [geometry,distance]of [[nearGeometry,0],[farGeometry,25]]){const mesh=new THREE.Mesh(geometry,treeMaterial);mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.waterReflection=false;lod.addLevel(mesh,distance,.15);}
  levels.push(lod);root.add(lod);count++;
 });
 if(count!==36)throw new Error(`Expected 36 tree meshes, received ${count}`);
 originals.forEach(o=>{o.visible=false;});root.name='Blender curved garden trees';scene.add(root);root.updateMatrixWorld(true);
 return {trees:15,pines:6,meshes:count,blendedTrunks,levels,update:camera=>{for(const lod of levels)lod.update(camera);}};
}
