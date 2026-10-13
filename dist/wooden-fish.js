import * as THREE from 'three';
import {WoodenFishStrike} from './wooden-fish-motion.js';
import {heldMalletPose} from './wooden-fish-pose.js';
export function createWoodenFish(asset,scene,camera,sound){
 const groups=Object.fromEntries(['body','mallet','stand'].map(k=>[k,new THREE.Group()]));
 asset.updateMatrixWorld(true);
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 for(const o of meshes){const key=o.userData.assembly||Object.keys(groups).find(k=>o.name.startsWith('Muyu_'+k));if(!key)throw new Error('Unknown wooden fish assembly');groups[key].attach(o);o.castShadow=o.receiveShadow=true;o.userData.waterSide='above';o.material.envMapIntensity=.65;if(o.material.name.includes('satin rosewood'))o.material.color.setRGB(.30,.105,.028);if(o.material.map)o.material.map.anisotropy=8;}
 const parked=new THREE.Group();parked.name='Wooden fish on silk cushion';parked.position.set(-.95,1.62,-6.45);scene.add(parked);
 parked.add(groups.stand,groups.body,groups.mallet);
 const overlay=new THREE.Scene(),view=new THREE.PerspectiveCamera(45,1,.01,10),hand=new THREE.Group(),pivot=new THREE.Group();
 overlay.environment=scene.environment;overlay.environmentIntensity=.5;overlay.add(new THREE.HemisphereLight('#fff0d7','#382616',2));const light=new THREE.DirectionalLight('#ffe0ac',2.4);light.position.set(-1,3,2);overlay.add(light,hand);hand.rotation.set(.16,-.28,-.05);hand.add(pivot);
 const heldPose=heldMalletPose();pivot.position.copy(heldPose.pivot);
 const state=new WoodenFishStrike(sound),button=document.querySelector('#return-muyu');let pickup=0;
 function take(){if(!state.take())return;pickup=0;hand.add(groups.body);pivot.add(groups.mallet);groups.mallet.position.copy(heldPose.position);groups.mallet.quaternion.copy(heldPose.rotation);pivot.rotation.z=-.18;button.classList.remove('hidden');}
 function putBack(){state.putBack();parked.add(groups.body,groups.mallet);groups.body.position.set(0,0,0);groups.body.rotation.set(0,0,0);groups.mallet.position.set(0,0,0);groups.mallet.quaternion.identity();pivot.rotation.set(0,0,0);button.classList.add('hidden');}
 button.addEventListener('click',putBack);
 function update(dt){const stroke=state.update(dt);pickup=Math.min(1,pickup+dt/.42);pivot.rotation.z=-.18*(1-stroke);groups.body.rotation.z=state.held?.012*stroke:0;}
 function render(renderer){if(!state.held)return;const aspect=camera.aspect;view.aspect=aspect;view.updateProjectionMatrix();hand.position.set(Math.min(.38,.19*aspect),-.39-.35*(1-pickup)**3,-1.42);const clear=renderer.autoClear,shadows=renderer.shadowMap.enabled;renderer.autoClear=false;renderer.shadowMap.enabled=false;renderer.clearDepth();try{renderer.render(overlay,view);}finally{renderer.autoClear=clear;renderer.shadowMap.enabled=shadows;}}
 return {take,putBack,update,render,strike:()=>state.click(),get held(){return state.held;},get stats(){return {held:state.held,strikes:state.strikes,requests:state.requests,pending:state.pending};}};
}
