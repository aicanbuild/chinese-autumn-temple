import * as THREE from 'three';

export function createSculptureLOD(detailed,distant,camera,viewportHeight){
 const lod=new THREE.LOD();lod.name='Blender altar sculpture with distance detail';
 lod.position.set(0,2.85,-8.6);
 for(const root of [detailed,distant]){
  root.position.sub(lod.position);
  root.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.material.envMapIntensity=.85;o.userData.waterSide='above';}});
 }
 lod.addLevel(detailed,0);lod.addLevel(distant,1,.12);
 lod.resize=height=>{lod.levels[1].distance=1.915*height/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*120);};
 lod.resize(viewportHeight);return lod;
}
