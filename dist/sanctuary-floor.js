import {extractRegion} from './rituals.js';

export function oldSanctuaryFloorContains(p){return p.x>-6.14&&p.x<6.14&&p.z>-10.74&&p.z<-3.46&&p.y>.90&&p.y<1.081;}
export function isOriginalFloorVertex(p){return oldSanctuaryFloorContains(p)&&Math.min(Math.abs(p.z+3.475),Math.abs(p.z+10.725))<.012;}
export function installSanctuaryFloor(model,asset,scene){
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 if(meshes.length!==3||meshes.some(o=>!o.geometry.attributes.position?.count))throw new Error('Sanctuary stone floor is incomplete');
 const discarded=extractRegion(model,n=>n==='Polished ebony cedar',oldSanctuaryFloorContains,ps=>ps.every(isOriginalFloorVertex));
 let removedTriangles=0;discarded.traverse(o=>{if(o.geometry){removedTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 for(const o of meshes){o.castShadow=true;o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';o.material.envMapIntensity=.30;for(const k of ['map','normalMap','roughnessMap'])if(o.material[k])o.material[k].anisotropy=8;}
 asset.name='Blender honed stone sanctuary floor';scene.add(asset);return {removedTriangles,batches:meshes.length};
}
