import * as THREE from 'three';

// Geometry-only distance detail. Full materials and editable source stay intact.
export function createSanctuaryDetail(root,distant,{errorBudget=.006,pixelLimit=.55,expectedMeshes=3}={}){
 root.updateMatrixWorld(true);distant.updateMatrixWorld(true);
 const sources=new Map();distant.traverse(o=>{if(o.isMesh)sources.set(o.userData.sourceMaterial,o);});
 const entries=[],inverse=new THREE.Matrix4();
 root.traverse(mesh=>{
  if(!mesh.isMesh)return;const source=sources.get(mesh.material.name);if(!source)return;
  const full=mesh.geometry,far=source.geometry.clone().applyMatrix4(inverse.copy(mesh.matrixWorld).invert().multiply(source.matrixWorld));
  full.computeBoundingBox();far.computeBoundingBox();far.computeBoundingSphere();
  const bounds=full.boundingBox.clone().union(far.boundingBox);
  entries.push({mesh,full,far,bounds,distant:false});
 });
 if(entries.length!==expectedMeshes)throw new Error('Missing sanctuary distance geometry');
 const view=new THREE.Matrix4(),box=new THREE.Box3();
 const stats={fullMeshes:expectedMeshes,distantMeshes:0,savedTriangles:0};
 const triangles=g=>(g.index?.count??g.attributes.position.count)/3;
 function update(camera,height,inside=false){
  camera.updateMatrixWorld();stats.fullMeshes=stats.distantMeshes=stats.savedTriangles=0;
  const focal=Math.abs(camera.projectionMatrix.elements[5])*height/2;
  for(const entry of entries){
   const {mesh,full,far,bounds}=entry;mesh.updateWorldMatrix(true,false);
   view.multiplyMatrices(camera.matrixWorldInverse,mesh.matrixWorld);box.copy(bounds).applyMatrix4(view);
   const depth=-box.max.z,offAxis=Math.max(Math.abs(box.min.x),Math.abs(box.max.x),Math.abs(box.min.y),Math.abs(box.max.y));
   // Perspective error includes both transverse displacement and depth change.
   const worldError=errorBudget*mesh.matrixWorld.getMaxScaleOnAxis();
   const projected=depth>worldError?focal*worldError/(depth-worldError)*(1+offAxis/depth):Infinity;
   if(inside||projected>pixelLimit)entry.distant=false;
   else if(projected<pixelLimit*.8)entry.distant=true;
   mesh.geometry=entry.distant?far:full;
   if(entry.distant){stats.distantMeshes++;stats.savedTriangles+=triangles(full)-triangles(far);}else stats.fullMeshes++;
  }
  return stats;
 }
 return {update,stats,entries};
}
