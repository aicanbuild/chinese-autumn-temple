import * as THREE from 'three';

// Use the pinned renderer's depth comparisons and filtering, so water and
// opaque receivers agree at the same shadow edge. No second shadow pass.
const chunk=THREE.ShaderChunk.shadowmap_pars_fragment;
const start=chunk.indexOf('float texture2DCompare('),end=chunk.indexOf('vec2 cubeToUV(');
if(start<0||end<=start)throw new Error('Water sunlight needs the renderer shadow helpers');
const helpers=chunk.slice(start,end).replace(/\b(texture2DCompare|texture2DDistribution|VSMShadow|getShadow)\b/g,name=>'waterSun_'+name);

export function installWaterSunlight(water,sun){
 const material=water.material,term='waterSunColor*glint';
 if(!material.fragmentShader.includes(term))throw new Error('Water sunlight requires the direct sun lobe');
 const u={
  waterSunShadowMap:{value:null},waterSunShadowMatrix:{value:sun.shadow.matrix},
  waterSunShadowSize:{value:new THREE.Vector2(1,1)},
  waterSunShadowParams:{value:new THREE.Vector4()},waterSunShadowEnabled:{value:0}
 };
 Object.assign(material.uniforms,u);
 material.fragmentShader=material.fragmentShader.replace('#include <common>',`#include <common>
  #include <packing>
  uniform sampler2D waterSunShadowMap;
  uniform mat4 waterSunShadowMatrix;
  uniform vec2 waterSunShadowSize;
  uniform vec4 waterSunShadowParams;
  uniform float waterSunShadowEnabled;
  ${helpers}
  float waterSunVisibility(vec3 worldPoint){
   if(waterSunShadowEnabled<.5)return 1.;
   vec4 coordinate=waterSunShadowMatrix*vec4(worldPoint+vec3(0.,waterSunShadowParams.y,0.),1.);
   if(coordinate.w<=0.||coordinate.z<0.||coordinate.z>coordinate.w)return 1.;
   return waterSun_getShadow(waterSunShadowMap,waterSunShadowSize,waterSunShadowParams.w,waterSunShadowParams.x,waterSunShadowParams.z,coordinate);
  }`).replace(term,term+'*waterSunVisibility(cameraPosition-vToEye)');
 material.needsUpdate=true;
 const previous=water.onBeforeRender;
 water.onBeforeRender=function(renderer,...args){
  previous.call(this,renderer,...args);
  // Water captures can recursively render the scene. Bind after they return,
  // including the first draw, when the renderer has created the shadow target.
  const s=sun.shadow,map=s.map;
  u.waterSunShadowEnabled.value=renderer.shadowMap.enabled&&sun.castShadow&&map?1:0;
  u.waterSunShadowMap.value=map?.texture??null;
  u.waterSunShadowMatrix.value=s.matrix;
  if(map)u.waterSunShadowSize.value.set(map.width,map.height);
  u.waterSunShadowParams.value.set(s.bias,s.normalBias,s.radius,s.intensity);
 };
 return {uniforms:u};
}
