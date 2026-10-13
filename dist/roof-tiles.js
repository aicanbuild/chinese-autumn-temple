export function installRoofTiles(model,asset,scene){
 const replacements=[];asset.traverse(o=>{if(o.isMesh)replacements.push(o);});
 if(replacements.length!==1||replacements[0].geometry.attributes.position.count<1000)throw new Error('Refined roof asset is incomplete');
 const old=[];model.traverse(o=>{if(o.isMesh&&o.material?.name.startsWith('Charcoal glazed ceramic'))old.push(o);});
 let removedTriangles=0;
 for(const o of old){removedTriangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;o.removeFromParent();o.geometry.dispose();}
 for(const o of replacements){o.castShadow=true;o.receiveShadow=true;o.userData.waterSide='above';o.userData.waterClipStatic=true;o.material.envMapIntensity=.55;for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;}
 asset.name='Blender closed glazed ceramic roof tiles';scene.add(asset);return {removedTriangles,batches:replacements.length};
}
