import * as THREE from 'three';

// Replace only the original flat sediment mesh, retaining its photographic
// material and the existing water/caustic lighting path.
export function installPondBasin(model,asset){
 model.updateMatrixWorld(true);asset.updateMatrixWorld(true);
 let bed,source;model.traverse(o=>{if(o.isMesh&&o.material.name==='Riverbed sediment')bed=o;});
 asset.traverse(o=>{if(o.isMesh)source=o;});
 if(!bed||!source)throw new Error('Missing sediment or sculpted pond basin');
 const matrix=new THREE.Matrix4().copy(bed.matrixWorld).invert().multiply(source.matrixWorld);
 const geometry=source.geometry.clone().applyMatrix4(matrix);geometry.computeBoundingBox();geometry.computeBoundingSphere();
 bed.geometry.dispose();bed.geometry=geometry;bed.name='Blender contoured pond sediment';bed.userData.waterSide='below';
 return {triangles:(geometry.index?.count??geometry.attributes.position.count)/3};
}
