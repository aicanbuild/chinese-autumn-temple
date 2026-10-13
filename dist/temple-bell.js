import * as THREE from 'three';
import {BellStrike,BELL_IMPACT} from './bell-motion.js';
export function createTempleBell(asset,root,ringSound){
 const body=asset.getObjectByName('Bell_Body'),hammer=asset.getObjectByName('Bell_Hammer'),ropes=[0,1].map(i=>asset.getObjectByName('Bell_Rope_'+i));
 if(!body||!hammer||ropes.some(r=>!r))throw new Error('Temple bell is missing a moving assembly');
 const rest=hammer.position.clone(),bodyRest=body.position.clone(),strike=new BellStrike(ringSound);let parts=0;
 asset.traverse(o=>{if(!o.isMesh)return;parts++;o.castShadow=o.receiveShadow=true;o.userData.waterSide='above';o.userData.waterMotionPadding=.5;o.material.envMapIntensity=.55;for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;});root.add(asset);
 return {ring:()=>strike.ring(),get rings(){return strike.rings;},parts,update(dt){const angle=strike.update(dt);for(const rope of ropes)rope.rotation.z=angle;hammer.position.set(rest.x+1.25*Math.sin(angle),rest.y+1.25*(1-Math.cos(angle)),rest.z);const t=strike.age-BELL_IMPACT;body.position.copy(bodyRest);if(t>=0&&t<3)body.position.x+=.0007*Math.sin(t*65)*Math.exp(-t*2.5);}};
}
