import * as THREE from 'three';

// Keep the original four material batches, textures and world transforms.
export function installLotusSurfaces(root,asset){
 root.updateMatrixWorld(true);asset.updateMatrixWorld(true);const sources=new Map();
 asset.traverse(o=>{if(o.isMesh)sources.set(o.userData.sourceMaterial,o);});let replaced=0;
 root.traverse(o=>{
  if(!o.isMesh)return;const source=sources.get(o.material.name);if(!source)return;
  const transform=new THREE.Matrix4().copy(o.matrixWorld).invert().multiply(source.matrixWorld);
  const geometry=source.geometry.clone().applyMatrix4(transform);geometry.computeBoundingBox();geometry.computeBoundingSphere();
  o.geometry.dispose();o.geometry=geometry;replaced++;
 });
 if(replaced!==4)throw new Error('Missing lotus flower replacement');
 return replaced;
}
