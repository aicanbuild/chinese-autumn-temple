import * as THREE from 'three';
import {createHallCamera} from './hall-camera.js';

export function createCameraSafety(camera,controls,surfaceAt){
 const ray=new THREE.Raycaster(),down=new THREE.Vector3(0,-1,0),last=new THREE.Vector2(Infinity,Infinity);
 let terrain=null,terrainY=0;const hall=createHallCamera(camera,controls,surfaceAt);
 return {
  setHall:hall.setLayout,hallStats:hall.stats,
  setTerrain(root){terrain=root;root.updateMatrixWorld(true);last.set(Infinity,Infinity);},
  constrain(inside=false){
   if(inside)return hall.constrain();
   hall.reset();
   const before=controls.target.clone();
   controls.target.x=THREE.MathUtils.clamp(controls.target.x,-14,18);
   controls.target.z=THREE.MathUtils.clamp(controls.target.z,-12,17);
   controls.target.y=THREE.MathUtils.clamp(controls.target.y,.9,5);
   camera.position.add(controls.target.clone().sub(before));
   const {x,z}=camera.position;
   if(terrain&&Math.hypot(x-last.x,z-last.y)>.025){
    ray.set(new THREE.Vector3(x,150,z),down);ray.far=200;
    terrainY=ray.intersectObject(terrain,true)[0]?.point.y??0;last.set(x,z);
   }
   const floor=Math.max(terrainY,Math.abs(x)<16&&z>-13&&z<18?surfaceAt(x,z):0);
   if(camera.position.y<floor+.85){camera.position.y=floor+.85;camera.lookAt(controls.target);return true;}
   camera.lookAt(controls.target);return false;
  }
 };
}
