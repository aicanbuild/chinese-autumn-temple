// Native _BARK_BLEND stores a transported secondary UV chart and its fork weight.
// Normal maps are blended after each chart is transformed into view space.
export function applyBarkJunctions(material){
 const previous=material.onBeforeCompile,cacheKey=material.customProgramCacheKey();
 material.onBeforeCompile=function(shader,renderer){
  previous.call(this,shader,renderer);
  shader.vertexShader='attribute vec3 barkBlend;\nvarying vec3 vBarkBlend;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvBarkBlend=barkBlend;');
  shader.fragmentShader=`varying vec3 vBarkBlend;
mat3 barkTangentFrame(vec3 eye,vec3 n,vec2 uv){
 vec3 q0=dFdx(eye),q1=dFdy(eye);vec2 st0=dFdx(uv),st1=dFdy(uv);
 vec3 p1=cross(q1,n),p0=cross(n,q0),t=p1*st0.x+p0*st1.x,b=p1*st0.y+p0*st1.y;
 float d=max(dot(t,t),dot(b,b));float s=d==0.0?0.0:inversesqrt(d);
 return mat3(t*s,b*s,n);
}
`+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`
#ifdef USE_MAP
 diffuseColor *= mix(texture2D(map,vMapUv),texture2D(map,vBarkBlend.xy),clamp(vBarkBlend.z,0.0,1.0));
#endif`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`
float roughnessFactor=roughness;
#ifdef USE_ROUGHNESSMAP
 roughnessFactor *= mix(texture2D(roughnessMap,vRoughnessMapUv).g,texture2D(roughnessMap,vBarkBlend.xy).g,clamp(vBarkBlend.z,0.0,1.0));
#endif`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`
vec3 barkSurfaceNormal=normal;
#include <normal_fragment_maps>
#ifdef USE_NORMALMAP_TANGENTSPACE
 mat3 barkFrame=barkTangentFrame(-vViewPosition,barkSurfaceNormal,vBarkBlend.xy);
 #ifdef DOUBLE_SIDED
  barkFrame[0]*=faceDirection;barkFrame[1]*=faceDirection;
 #endif
 vec3 barkMapN=texture2D(normalMap,vBarkBlend.xy).xyz*2.0-1.0;barkMapN.xy*=normalScale;
 vec3 barkSecondaryNormal=normalize(barkFrame*barkMapN);
 normal=normalize(mix(normal,barkSecondaryNormal,clamp(vBarkBlend.z,0.0,1.0)));
#endif`);
 };
 material.customProgramCacheKey=()=>cacheKey+'|bark-fork-charts-v1';material.needsUpdate=true;return material;
}
