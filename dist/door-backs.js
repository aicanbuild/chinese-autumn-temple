// Geometry-only export reuses the existing sanctuary wood and gilding textures.
export function installDoorBacks(asset,sanctuary,scene){
 const materials=new Map();sanctuary.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.set(m.name,m);});
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 if(meshes.length!==4||meshes.some(o=>!materials.has(o.userData.sourceMaterial)))throw new Error('Door back materials are incomplete');
 for(const o of meshes){o.material=materials.get(o.userData.sourceMaterial);o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';}
 asset.name='Blender carved interior door linings';scene.add(asset);return {batches:meshes.length,leaves:4};
}
