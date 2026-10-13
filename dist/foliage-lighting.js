// The normal bias of a two-sided sheet must point towards the light. Otherwise
// a rear-lit leaf samples behind its own shadow and falsely blocks transmission.
const receiverFunctions=`
vec3 foliageReceiverNormal(mat4 shadowMatrix,vec4 point,vec3 normal){
 vec4 projected=shadowMatrix*point;
 vec4 delta=shadowMatrix*vec4(normal,0.);
 float depthDerivative=delta.z*projected.w-projected.z*delta.w;
 return normal*(depthDerivative>0.?-1.:1.);
}
`;
const receiverCoordinates=`
#ifdef USE_SHADOWMAP
 #if NUM_DIR_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for(int i=0;i<NUM_DIR_LIGHT_SHADOWS;i++){
 {
  vec3 receiverNormal=foliageReceiverNormal(directionalShadowMatrix[i],worldPosition,shadowWorldNormal);
  vDirectionalShadowCoord[i]=directionalShadowMatrix[i]*(worldPosition+vec4(receiverNormal*directionalLightShadows[i].shadowNormalBias,0.));
 }
 }
 #pragma unroll_loop_end
 #endif
 #if NUM_POINT_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for(int i=0;i<NUM_POINT_LIGHT_SHADOWS;i++){
 {
  vec3 toReceiver=(pointShadowMatrix[i]*worldPosition).xyz;
  vec3 receiverNormal=shadowWorldNormal*(dot(toReceiver,shadowWorldNormal)>0.?-1.:1.);
  vPointShadowCoord[i]=pointShadowMatrix[i]*(worldPosition+vec4(receiverNormal*pointLightShadows[i].shadowNormalBias,0.));
 }
 }
 #pragma unroll_loop_end
 #endif
 #if NUM_SPOT_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for(int i=0;i<NUM_SPOT_LIGHT_SHADOWS;i++){
 {
  vec3 receiverNormal=foliageReceiverNormal(spotLightMatrix[i],worldPosition,shadowWorldNormal);
  vSpotLightCoord[i]=spotLightMatrix[i]*(worldPosition+vec4(receiverNormal*spotLightShadows[i].shadowNormalBias,0.));
 }
 }
 #pragma unroll_loop_end
 #endif
#endif
`;
// Thin, pigmented diffuse transport for foliage. Existing direct-light shadow
// visibility is reused; no emission, transparent pass or screen-space refraction.
export function applyFoliageLighting(material,fraction=.22){
 if(material.userData.foliageTransmission)return material;
 const amount={value:Math.max(0,Math.min(.35,fraction))};
 const previous=material.onBeforeCompile,cache=material.customProgramCacheKey();
 material.userData.foliageTransmission=amount;
 material.onBeforeCompile=shader=>{
  previous.call(material,shader);
  shader.vertexShader=receiverFunctions+shader.vertexShader.replace('#include <shadowmap_vertex>','#include <shadowmap_vertex>\n'+receiverCoordinates);
  shader.uniforms.foliageTransmission=amount;
  shader.fragmentShader='uniform float foliageTransmission;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <lights_physical_pars_fragment>',`#include <lights_physical_pars_fragment>
void RE_Direct_Foliage(const in IncidentLight light,const in vec3 position,const in vec3 normal,const in vec3 viewDir,const in vec3 coatNormal,const in PhysicalMaterial material,inout ReflectedLight reflectedLight){
 vec3 before=reflectedLight.directDiffuse;
 RE_Direct_Physical(light,position,normal,viewDir,coatNormal,material,reflectedLight);
 // Split the diffuse budget between reflection and transmission. Pigment and
 // vein detail come from the existing base map and vertex color, not a glow tint.
 vec3 reflected=reflectedLight.directDiffuse-before;
 float backCosine=max(0.,-dot(normal,light.direction));
 reflectedLight.directDiffuse=before+reflected*(1.-foliageTransmission)
   +foliageTransmission*backCosine*light.color*BRDF_Lambert(material.diffuseColor);
}
#undef RE_Direct
#define RE_Direct RE_Direct_Foliage`);
 };
 material.customProgramCacheKey=()=>cache+'|foliage-thin-diffuse-v1';
 material.needsUpdate=true;return material;
}
