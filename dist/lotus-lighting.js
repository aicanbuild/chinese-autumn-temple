// Thin diffuse transmission for the authored flower shells. This is a local
// two-sided BSDF approximation, not a volumetric diffusion solver.
const varyings=`
varying float vLotusTransmission;
#ifdef USE_SHADOWMAP
 #if NUM_DIR_LIGHT_SHADOWS > 0
 varying vec4 vLotusDirectionalShadow[ NUM_DIR_LIGHT_SHADOWS ];
 #endif
 #if NUM_SPOT_LIGHT_SHADOWS > 0
 varying vec4 vLotusSpotShadow[ NUM_SPOT_LIGHT_SHADOWS ];
 #endif
 #if NUM_POINT_LIGHT_SHADOWS > 0
 varying vec4 vLotusPointShadow[ NUM_POINT_LIGHT_SHADOWS ];
 #endif
#endif
`;
const backShadow=`
#ifdef USE_SHADOWMAP
 #if NUM_DIR_LIGHT_SHADOWS > 0 || NUM_SPOT_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0
 vec4 lotusExitPosition = worldPosition - vec4( shadowWorldNormal * ( _lotus_thickness + 0.00025 ), 0.0 );
 #endif
 #if NUM_DIR_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
  vLotusDirectionalShadow[ i ] = directionalShadowMatrix[ i ] * lotusExitPosition;
 }
 #pragma unroll_loop_end
 #endif
 #if NUM_SPOT_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
  vLotusSpotShadow[ i ] = spotLightMatrix[ i ] * lotusExitPosition;
 }
 #pragma unroll_loop_end
 #endif
 #if NUM_POINT_LIGHT_SHADOWS > 0
 #pragma unroll_loop_start
 for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
  vLotusPointShadow[ i ] = pointShadowMatrix[ i ] * lotusExitPosition;
 }
 #pragma unroll_loop_end
 #endif
#endif
`;
const response=`
void RE_Direct_Lotus( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
 vec3 previousDiffuse = reflectedLight.directDiffuse;
 RE_Direct_Physical( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
 float fraction = clamp( vLotusTransmission, 0.0, 0.35 );
 float backCosine = max( -dot( geometryNormal, directLight.direction ), 0.0 );
 vec3 reflected = reflectedLight.directDiffuse - previousDiffuse;
 reflectedLight.directDiffuse = previousDiffuse + reflected * ( 1.0 - fraction )
  + fraction * backCosine * directLight.color * BRDF_Lambert( material.diffuseColor );
}
#undef RE_Direct
#define RE_Direct RE_Direct_Lotus
`;

export function lotusLightingChunk(chunk){
 // Choose the existing front receiver for reflection and the exit surface
 // receiver for backlighting. Each light still performs one shadow lookup.
 const condition='( vLotusTransmission > 0.0001 && dot( geometryNormal, directLight.direction ) < 0.0 )';
 for(const [original,back] of [['vDirectionalShadowCoord','vLotusDirectionalShadow'],['vSpotLightCoord','vLotusSpotShadow'],['vPointShadowCoord','vLotusPointShadow']]){
  const pattern=new RegExp(`(get(?:Point)?Shadow\\([^;]*?)${original}\\[ i \\]`,'g');
  chunk=chunk.replace(pattern,`$1(${condition} ? ${back}[ i ] : ${original}[ i ])`);
 }
 return chunk;
}

export function finishLotusLighting(source,lightingChunk){
 if(source.userData.lotusLighting)return source;
 const material=source.clone();material.userData.lotusLighting=true;
 material.onBeforeCompile=shader=>{
  shader.vertexShader='attribute float _lotus_transmittance;\nattribute float _lotus_thickness;\n'+varyings+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvLotusTransmission = _lotus_transmittance;').replace('#include <shadowmap_vertex>','#include <shadowmap_vertex>\n'+backShadow);
  shader.fragmentShader=varyings+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <lights_physical_pars_fragment>','#include <lights_physical_pars_fragment>\n'+response).replace('#include <lights_fragment_begin>',lotusLightingChunk(lightingChunk));
 };
 material.customProgramCacheKey=()=> 'temple-lotus-thin-diffuse-v1';
 return material;
}
