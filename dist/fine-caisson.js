import {extractRegion} from './rituals.js';
// The original ceiling is wholly above 4.14m, furnishings end below 3.6m.
export function installFineCaisson(asset,sanctuary,distant,scene){
 let removed=0;
 for(const root of [sanctuary,distant]){
  const old=extractRegion(root,()=>true,p=>p.y>4.14,points=>points.every(p=>p.y>4.14));
  old.traverse(o=>{if(o.isMesh){removed+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;o.geometry.dispose();}});
 }
 const materials=new Map();sanctuary.traverse(o=>{if(o.isMesh)materials.set(o.material.name,o.material);});
 asset.traverse(o=>{if(!o.isMesh)return;const shared=materials.get(o.userData.sourceMaterial);if(shared)o.material=shared;o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;});scene.add(asset);return {removedTriangles:removed};
}
