import * as THREE from 'three';

// A wide, flat pond has a very loose bounding sphere. Its sphere intersects a
// camera inside the hall even when every water triangle is behind that camera.
// A conservative world-space box avoids both expensive captures in that case.
export function createWaterSurfaceVisibility(water){
 water.geometry.computeBoundingBox();
 const regions=water.geometry.userData.surfaceRegions??[water.geometry.boundingBox.clone()],world=new THREE.Box3(),view=new THREE.Matrix4(),frustum=new THREE.Frustum();
 return {
  update(camera){
   camera.updateWorldMatrix(true,false);water.updateWorldMatrix(true,false);
   
   view.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
   frustum.setFromProjectionMatrix(view,camera.coordinateSystem);
   water.visible=regions.some(local=>{world.copy(local).applyMatrix4(water.matrixWorld).expandByScalar(.01+(water.userData.surfaceDisplacement??0));return frustum.intersectsBox(world);});
   return water.visible;
  }
 };
}
