import * as THREE from 'three';
import {extractRegion} from './rituals.js';
import {applyFoliageLighting} from './foliage-lighting.js';

export function installCamellias(model,asset,layout,buffer,understory,scene){
 const {groups,leavesPerGroup,stride}=layout;
 if(groups!==12||leavesPerGroup!==950||stride!==19||buffer.byteLength!==groups*leavesPerGroup*stride*4)throw new Error('Invalid camellia instance layout');
 const data=new Float32Array(buffer);if(!data.every(Number.isFinite))throw new Error('Non-finite camellia placement');
 let prototype,source;asset.updateMatrixWorld(true);asset.traverse(o=>{if(o.isMesh)prototype=o;});understory.traverse(o=>{if(o.isMesh&&o.name.includes('leaves'))source=o.material;});
 if(!prototype||!source)throw new Error('Missing curved leaf or shared botanical maps');
 const geometry=prototype.geometry.clone().applyMatrix4(prototype.matrixWorld),material=source.clone();
 material.vertexColors=false;material.color.setRGB(1,1,1);material.roughness=layout.roughness;material.normalScale.setScalar(layout.normalStrength);material.envMapIntensity=.35;material.side=THREE.DoubleSide;material.alphaTest=0;material.transparent=false;material.forceSinglePass=true;
 for(const key of ['map','normalMap'])if(material[key])material[key].anisotropy=8;
 applyFoliageLighting(material,.16);
 const legacy=extractRegion(model,n=>n==='Clipped garden foliage',p=>p.y<1.35,points=>points.every(p=>p.y<1.35));let removed=0;
 legacy.traverse(o=>{if(o.isMesh){removed+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;o.geometry.dispose();}});
 if(removed!==layout.legacyTriangles)throw new Error(`Expected ${layout.legacyTriangles} shrub triangles, got ${removed}`);
 const batches=[],matrix=new THREE.Matrix4(),color=new THREE.Color();
 for(let group=0;group<groups;group++){
  const mesh=new THREE.InstancedMesh(geometry,material,leavesPerGroup);mesh.name=`Curved camellia leaves ${group}`;
  for(let i=0;i<leavesPerGroup;i++){const offset=(group*leavesPerGroup+i)*stride;matrix.fromArray(data,offset);mesh.setMatrixAt(i,matrix);color.fromArray(data,offset+16);mesh.setColorAt(i,color);}
  mesh.castShadow=mesh.receiveShadow=true;mesh.userData.waterReflection=false;mesh.userData.waterClipStatic=true;mesh.userData.waterSide='above';mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);batches.push(mesh);
 }
 return {batches,stats:{shrubs:groups,leaves:groups*leavesPerGroup,removedTriangles:removed,leafTriangles:(geometry.index?.count??geometry.attributes.position.count)/3,draws:groups}};
}
