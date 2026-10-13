import {extractRegion} from './rituals.js';

export function inGuardianVolume(p,x){return Math.abs(p.x-x)<.70&&p.z>-3.01&&p.z<-1.44&&p.y>.80&&p.y<2.51;}
export function isOldGuardianFace(vertices){
 return [-3.6,3.6].some(x=>vertices.every(p=>inGuardianVolume(p,x))&&vertices.some(p=>p.y>.926));
}
export function installGuardians(model,asset,scene){
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 if(meshes.length!==2||meshes.some(o=>o.geometry.attributes.position.count<1000))throw new Error('Stone guardian asset is incomplete');
 const removed=extractRegion(model,n=>n==='Carved pale limestone'||n==='Deep dark wood',p=>[-3.6,3.6].some(x=>inGuardianVolume(p,x)),isOldGuardianFace);
 let removedTriangles=0;removed.traverse(o=>{if(o.geometry){removedTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 for(const o of meshes){o.castShadow=true;o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';o.material.envMapIntensity=.45;for(const k of ['map','roughnessMap'])if(o.material[k])o.material[k].anisotropy=8;}
 asset.name='Scanned carved stone guardians';scene.add(asset);return {lions:meshes.length,removedTriangles};
}
