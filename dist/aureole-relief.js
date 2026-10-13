import {extractRegion} from './rituals.js';
// Native closed relief geometry shares the temple's existing metal finishes.
export function installAureoleRelief(asset,sanctuary,scene){
 const materials=new Map();sanctuary.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.set(m.name,m);});
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 if(meshes.length!==2||meshes.some(o=>!materials.has(o.userData.sourceMaterial)))throw new Error('Aureole relief materials are incomplete');
 // Only the obsolete bronze rods occupy this measured native mandorla slab.
 // Bronze has no sanctuary distance-geometry replacement.
 const inside=p=>Math.abs(p.x)<1.04&&p.y>1.72&&p.y<4.14&&p.z>-9.200&&p.z<-9.180;
 const oldRays=extractRegion(sanctuary,n=>n==='Sanctuary | antique gilt bronze',inside,pts=>pts.every(inside));
 let removedTriangles=0;oldRays.traverse(o=>{if(o.isMesh){removedTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 for(const o of meshes){o.material=materials.get(o.userData.sourceMaterial);o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';}
 asset.name='Blender lotus and flame mandorla relief';scene.add(asset);return {batches:meshes.length,petals:80,removedTriangles};
}
