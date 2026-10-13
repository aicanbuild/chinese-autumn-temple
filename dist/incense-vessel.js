import {extractRegion} from './rituals.js';

// The old bowl and handles were baked into one architecture material batch.
// Remove only complete triangles in their measured footprint; preserve the altar.
export function installIncenseVessel(model,vessel,scene){
 const inside=p=>Math.abs(p.x)<.57&&Math.abs(p.z+6.6)<.43&&p.y>1.0&&p.y<1.70;
 const removed=extractRegion(model,n=>/gilded|gold/i.test(n),inside,points=>points.every(inside));
 let removedTriangles=0;removed.traverse(o=>{if(o.isMesh){removedTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 vessel.name='Blender chased bronze incense vessel';
 vessel.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.userData.waterSide='above';o.material.envMapIntensity=.8;for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;}});
 scene.add(vessel);return {removedTriangles};
}
