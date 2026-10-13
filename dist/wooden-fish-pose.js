import * as THREE from 'three';
// Landmarks of the Blender-authored resting beater, in glTF Y-up coordinates.
export const malletHead = new THREE.Vector3(.253,.040,-.055);
export const malletGrip = malletHead.clone().add(new THREE.Vector3(.07,-.025,.32).normalize().multiplyScalar(Math.hypot(.07,.32,.005)));
export function heldMalletPose(){
 const reach=malletHead.clone().sub(malletGrip);
 const rotation=new THREE.Quaternion().setFromUnitVectors(reach.clone().normalize(),new THREE.Vector3(-1,0,0));
 const contact=new THREE.Vector3(0,.349,-.02);
 return {rotation,position:malletGrip.clone().negate().applyQuaternion(rotation),pivot:contact.sub(reach.applyQuaternion(rotation))};
}
