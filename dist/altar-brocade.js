// The Blender-authored cloth retains its woven-metal mask and dielectric silk.
export function installAltarBrocade(asset,scene){
 asset.name='Paired crimson silk altar runners';let meshes=0;
 asset.traverse(o=>{if(!o.isMesh)return;meshes++;o.castShadow=true;o.receiveShadow=true;o.userData.waterSide='above';
  o.material.envMapIntensity=.38;
  if(o.material.isMeshPhysicalMaterial){o.material.sheen=.16;o.material.sheenColor.setRGB(.35,.065,.10);o.material.sheenRoughness=.5;}
  for(const key of ['map','normalMap','roughnessMap','metalnessMap'])if(o.material[key])o.material[key].anisotropy=8;
 });
 scene.add(asset);return {meshes};
}
