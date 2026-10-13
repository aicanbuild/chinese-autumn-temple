import * as THREE from 'three';
import {extractRegion} from './rituals.js';
import {applyFoliageLighting} from './foliage-lighting.js';

export function installCamelliaBlossoms(model,asset,layout,scene){
 if(layout.blooms!==60||layout.matrices?.length!==60||!layout.matrices.every(m=>m.length===16&&m.every(Number.isFinite)))throw new Error('Invalid camellia blossom placements');
 const prototypes=[];asset.updateMatrixWorld(true);asset.traverse(o=>{if(o.isMesh)prototypes.push(o);});
 if(prototypes.length!==3)throw new Error('Expected petals, stamens and calyx');
 const original=extractRegion(model,n=>n==='Ivory camellia petals',()=>true);let removed=0;
 original.traverse(o=>{if(o.isMesh){removed+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;o.geometry.dispose();}});
 if(removed!==layout.legacyTriangles)throw new Error('Original camellia blossom geometry mismatch');
 const matrix=new THREE.Matrix4(),batches=[];let triangles=0;
 for(const prototype of prototypes){
  const geometry=prototype.geometry.clone().applyMatrix4(prototype.matrixWorld),material=prototype.material.clone();
  material.side=THREE.DoubleSide;material.forceSinglePass=true;material.envMapIntensity=.3;
  if(material.name.includes('ivory petals'))applyFoliageLighting(material,.10);
  const mesh=new THREE.InstancedMesh(geometry,material,layout.blooms);mesh.name=prototype.name+' | garden blooms';
  layout.matrices.forEach((values,i)=>mesh.setMatrixAt(i,matrix.fromArray(values)));
  mesh.castShadow=mesh.receiveShadow=true;mesh.userData.waterClipStatic=true;mesh.userData.waterSide='above';mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);batches.push(mesh);
  triangles+=(geometry.index?.count??geometry.attributes.position.count)/3*layout.blooms;
 }
 return {batches,stats:{blooms:layout.blooms,draws:batches.length,triangles,removedTriangles:removed}};
}
