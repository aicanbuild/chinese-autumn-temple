// Blender-authored polychrome coffers and seated gilt relief.
export function installCaissonVines(asset,sanctuary,scene){
 let gold;sanctuary.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.name==='Sanctuary | hand burnished gold')gold=m;});
 const meshes=[];asset.traverse(o=>{if(o.isMesh)meshes.push(o);});
 const expected=new Set(['Sanctuary | hand burnished gold','Caisson | mineral polychrome coffers','Caisson | painted square borders']);
 if(!gold||meshes.length!==3||meshes.some(o=>!expected.delete(o.userData.sourceMaterial))||expected.size)throw new Error('Caisson ornament asset is incomplete');
 for(const o of meshes){
  if(o.userData.sourceMaterial===gold.name)o.material=gold;
  else {o.material.roughness=.68;o.material.metalness=0;o.material.envMapIntensity=.4;}
  for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;
  o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.userData.waterSide='above';
 }
 asset.name='Blender polychrome caisson and gilt relief';scene.add(asset);return {panels:32,cartouches:64,batches:meshes.length};
}
