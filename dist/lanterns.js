import * as THREE from 'three';
import {extractRegion} from './rituals.js';

export function containsOldLantern(p,[x,y,z,s]){
 return Math.abs(p.x-x)<.376*s&&Math.abs(p.z+y)<.376*s&&p.y>z-.006&&p.y<z+2.236*s;
}

// Baked cosine-weighted local visibility affects environment light only.
export function installLanternContact(material,geometry){
 if(!geometry.getAttribute('_lantern_occlusion')||material.userData.lanternContactStrength)return;
 const strength={value:1};material.userData.lanternContactStrength=strength;
 material.onBeforeCompile=shader=>{
  shader.uniforms.lanternContactStrength=strength;
  shader.vertexShader='attribute float _lantern_occlusion; varying float lanternOcclusion;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nlanternOcclusion=_lantern_occlusion;');
  shader.fragmentShader='varying float lanternOcclusion; uniform float lanternContactStrength;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <aomap_fragment>',`#include <aomap_fragment>
   float lanternAO=mix(1.0,clamp(lanternOcclusion,0.0,1.0),lanternContactStrength);
   reflectedLight.indirectDiffuse*=lanternAO;
   #if defined(USE_ENVMAP) && defined(STANDARD)
    reflectedLight.indirectSpecular*=computeSpecularOcclusion(saturate(dot(geometryNormal,geometryViewDir)),lanternAO,material.roughness);
   #endif
  `);
 };
 material.customProgramCacheKey=()=> 'lantern-local-visibility-v1';material.needsUpdate=true;
}

export function installLanterns(model,prototype,layout,scene,{perLampCulling=false}={}){
 // Whole-face containment preserves large paving faces beneath each fixture.
 const removed=extractRegion(model,n=>n==='Honed silver granite'||n==='Warm paper lantern',
  p=>layout.placements.some(a=>containsOldLantern(p,a)),
  vertices=>layout.placements.some(a=>vertices.every(p=>containsOldLantern(p,a))));
 removed.traverse(o=>o.geometry?.dispose());
 const meshes=[],dummy=new THREE.Object3D();prototype.updateMatrixWorld(true);
 prototype.traverse(source=>{
  if(!source.isMesh)return;
  const geometry=source.geometry.clone().applyMatrix4(source.matrixWorld),material=source.material;
  installLanternContact(material,geometry);
  material.envMapIntensity=material.metalness>.5?.7:.45;
  for(const key of ['map','normalMap','roughnessMap'])if(material[key])material[key].anisotropy=8;
  // Multi-draw keeps one material batch while the renderer independently culls
  // each complete lamp for the main, reflection, and shadow cameras.
  const mesh=perLampCulling?new THREE.BatchedMesh(layout.placements.length,geometry.attributes.position.count,geometry.index?.count??0,material):new THREE.InstancedMesh(geometry,material,layout.placements.length);
  const geometryId=perLampCulling?mesh.addGeometry(geometry):null;
  if(perLampCulling){mesh.sortObjects=false;geometry.dispose();}
  mesh.name=material.name;
  layout.placements.forEach(([x,y,z,s],i)=>{dummy.position.set(x,z,-y);dummy.scale.setScalar(s);dummy.updateMatrix();mesh.setMatrixAt(perLampCulling?mesh.addInstance(geometryId):i,dummy.matrix);});
  mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.waterMotionPadding=.005;mesh.userData.waterSide='above';mesh.userData.noAO=true;mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);meshes.push(mesh);
 });
 return {count:layout.placements.length,meshes,perLampCulling};
}
