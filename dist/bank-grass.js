import * as THREE from 'three';
import {extractRegion} from './rituals.js';

// Legacy blades were four-point faces rooted at y=.18, mixed into rock moss.
// Check the complete triangle so nearby low moss caps and tall foliage survive.
export function isLegacyGrassTriangle(points){
 const y=points.map(p=>p.y),x=points.map(p=>p.x),z=points.map(p=>p.z);
 return Math.abs(Math.min(...y)-.18)<.002 && Math.max(...y)>.30 && Math.max(...y)<.72 && Math.max(...x)-Math.min(...x)<.40 && Math.max(...z)-Math.min(...z)<.40;
}
export function installBankGrass(model,asset,scene){
 let removed=0;
 const legacy=extractRegion(model,n=>n==='Soft forest moss',()=>true,isLegacyGrassTriangle);
 legacy.traverse(o=>{if(o.isMesh){removed+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 asset.name='Curved bank sedge';let triangles=0,batches=0;
 asset.traverse(o=>{if(!o.isMesh)return;batches++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;
  o.material.side=THREE.DoubleSide;o.material.envMapIntensity=.4;o.castShadow=true;o.receiveShadow=true;o.userData.waterClipStatic=true;
 });scene.add(asset);return {removedLegacyTriangles:removed,triangles,batches};
}
