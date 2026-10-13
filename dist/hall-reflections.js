import * as THREE from 'three';

const fragment=`
varying vec3 hallProbeWorld;
uniform vec3 hallProbePosition;
uniform vec3 hallProbeMin;
uniform vec3 hallProbeMax;
vec3 hallProbeDirection(vec3 direction){
 if(any(lessThan(hallProbeWorld,hallProbeMin))||any(greaterThan(hallProbeWorld,hallProbeMax)))return direction;
 vec3 safeDirection=mix(vec3(-1.),vec3(1.),step(vec3(0.),direction))*max(abs(direction),vec3(.00001));
 vec3 face=mix(hallProbeMin,hallProbeMax,step(vec3(0.),direction));
 vec3 distances=(face-hallProbeWorld)/safeDirection;
 float travel=min(distances.x,min(distances.y,distances.z));
 return travel>0.?hallProbeWorld+direction*travel-hallProbePosition:direction;
}
`;

// A box projection corrects reflected directions for a finite room. Diffuse IBL
// remains the room-average probe; this is not spatial GI or ray-traced reflection.
export function applyHallReflection(material,texture,{position=new THREE.Vector3(0,2.8,-6.8),min=new THREE.Vector3(-5.1,1.07,-10.14),max=new THREE.Vector3(5.1,4.3,-3.6),intensity=1,specularMap=null}={}){
 if(specularMap&&(texture.image.width!==specularMap.image.width||texture.image.height!==specularMap.image.height))throw new Error('Hall reflection atlases must share CubeUV dimensions');
 const before=material.onBeforeCompile,cache=material.customProgramCacheKey();
 material.envMap=texture;material.envMapIntensity=intensity;material.envMapRotation.set(0,0,0);
 material.onBeforeCompile=function(shader,...args){
  before.call(this,shader,...args);
  shader.uniforms.hallProbePosition={value:position};shader.uniforms.hallProbeMin={value:min};shader.uniforms.hallProbeMax={value:max};
  if(specularMap)shader.uniforms.hallSpecularMap={value:specularMap};
  shader.vertexShader='varying vec3 hallProbeWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>',`#include <worldpos_vertex>
   vec4 hallPoint=vec4(transformed,1.);
   #ifdef USE_INSTANCING
    hallPoint=instanceMatrix*hallPoint;
   #endif
   hallProbeWorld=(modelMatrix*hallPoint).xyz;`);
  shader.fragmentShader=fragment+shader.fragmentShader;
  let chunk=THREE.ShaderChunk.envmap_physical_pars_fragment.replace('envMapRotation * reflectVec','envMapRotation * hallProbeDirection( reflectVec )');
  // Keep diffuse irradiance from the original room probe. Only the specular
  // lookup sees the separately captured furniture; roughness filtering stays
  // in Three's existing PMREM path and uses an identically sized atlas.
  if(specularMap){shader.fragmentShader='uniform sampler2D hallSpecularMap;\n'+shader.fragmentShader;chunk=chunk.replace('textureCubeUV( envMap, envMapRotation * hallProbeDirection','textureCubeUV( hallSpecularMap, envMapRotation * hallProbeDirection');}
  shader.fragmentShader=shader.fragmentShader.replace('#include <envmap_physical_pars_fragment>',chunk);
 };
 material.customProgramCacheKey=()=>cache+'|hall-box-probe-v1'+(specularMap?'|furnished-specular-v1':'');material.needsUpdate=true;return material;
}

export function captureHallReflections(renderer,scene,roots,{exclude=[],size=128,projections=new Map(),specularRoots=[]}={}){
 // An appended detail asset may share gold/paint with the original room. Keep
 // the first owner's projection; only its new materials take the new bounds.
 const materials=new Map();for(const root of roots)root.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.isMeshStandardMaterial&&!materials.has(m))materials.set(m,projections.get(root));});
 const specularMaterials=new Set();for(const root of specularRoots)root.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(materials.has(m))specularMaterials.add(m);});
 const hidden=[];scene.traverse(o=>{if(o.isWater||exclude.includes(o)){hidden.push([o,o.visible]);o.visible=false;}});
 const state={target:renderer.getRenderTarget(),face:renderer.getActiveCubeFace(),mip:renderer.getActiveMipmapLevel(),toneMapping:renderer.toneMapping,autoClear:renderer.autoClear,xr:renderer.xr.enabled};
 const generator=new THREE.PMREMGenerator(renderer),position=new THREE.Vector3(0,2.8,-6.8);let target,specularTarget;
 try{
  scene.updateMatrixWorld(true);target=generator.fromScene(scene,0,.09,600,{size,position});
  if(specularMaterials.size){
   for(const [o,visible]of hidden)if(!o.isWater)o.visible=visible;
   renderer.shadowMap.needsUpdate=true;scene.traverse(o=>{if(o.isLight&&o.castShadow)o.shadow.needsUpdate=true;});
   specularTarget=generator.fromScene(scene,0,.09,600,{size,position});
  }
 }catch(error){target?.dispose();specularTarget?.dispose();throw error;}
 finally{for(const [o,visible]of hidden)o.visible=visible;generator.dispose();renderer.setRenderTarget(state.target,state.face,state.mip);renderer.toneMapping=state.toneMapping;renderer.autoClear=state.autoClear;renderer.xr.enabled=state.xr;renderer.shadowMap.needsUpdate=true;scene.traverse(o=>{if(o.isLight&&o.castShadow)o.shadow.needsUpdate=true;});}
 for(const [material,projection] of materials)applyHallReflection(material,target.texture,{position,...projection,specularMap:specularMaterials.has(material)?specularTarget.texture:null});
 return {target,specularTarget,setIntensity(value){for(const material of materials.keys())material.envMapIntensity=Math.max(0,value);},stats:{materials:materials.size,captures:specularTarget?2:1,specularMaterials:specularMaterials.size,faceSize:size,position:position.toArray()},dispose(){target.dispose();specularTarget?.dispose();}};
}
