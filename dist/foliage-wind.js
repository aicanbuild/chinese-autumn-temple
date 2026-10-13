import * as THREE from 'three';

// Shared vertex deformation for lit, depth and point-light distance programs.
export function applyCanopyWind(shader,time){
 shader.uniforms.uWind=time;
 shader.vertexShader=`uniform float uWind;
 float leafGust(vec3 root){return sin(uWind*.48+root.x*.39+root.z*.3)+.35*sin(uWind*1.4+root.y*2.);}
 `+shader.vertexShader;
 shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
 #ifdef USE_INSTANCING
 transformed.z+=leafGust(instanceMatrix[3].xyz)*.10*pow(position.y+.5,2.);
 #endif`);
 shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>',`#include <beginnormal_vertex>
 #ifdef USE_INSTANCING
 objectNormal.y-=objectNormal.z*leafGust(instanceMatrix[3].xyz)*.20*(position.y+.5);
 objectNormal=normalize(objectNormal);
 #endif`);
}
export function applyWoodlandWind(shader,time){
 shader.uniforms.uWoodlandTime=time;
 shader.vertexShader='uniform float uWoodlandTime;\n'+shader.vertexShader;
 shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
 #if defined(USE_INSTANCING) || defined(USE_BATCHING)
 #ifdef USE_BATCHING
 vec3 root=batchingMatrix[3].xyz;
 #else
 vec3 root=instanceMatrix[3].xyz;
 #endif
 float gust=sin(uWoodlandTime*.48+root.x*.21+root.z*.19);
 transformed.x+=gust*.035*max(0.,position.y-2.);
 transformed.z+=sin(uWoodlandTime*.73+position.x*1.7+root.z)*.045;
 #endif`);
 shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>',`#include <beginnormal_vertex>
 #if defined(USE_INSTANCING) || defined(USE_BATCHING)
 #ifdef USE_BATCHING
 vec3 windRoot=batchingMatrix[3].xyz;
 #else
 vec3 windRoot=instanceMatrix[3].xyz;
 #endif
 float dxdy=position.y > 2.0 ? .035*sin(uWoodlandTime*.48+windRoot.x*.21+windRoot.z*.19):0.;
 float dzdx=.0765*cos(uWoodlandTime*.73+position.x*1.7+windRoot.z);
 objectNormal.x-=dzdx*objectNormal.z;
 objectNormal.y-=dxdy*objectNormal.x;
 objectNormal=normalize(objectNormal);
 #endif`);
}
export function createWindShadows(source,time,deform,key){
 const params={map:source.map,alphaMap:source.alphaMap,alphaTest:source.alphaTest,side:source.side};
 const depth=new THREE.MeshDepthMaterial({...params,depthPacking:THREE.RGBADepthPacking});
 const distance=new THREE.MeshDistanceMaterial(params);
 for(const material of [depth,distance]){material.onBeforeCompile=shader=>deform(shader,time);material.customProgramCacheKey=()=>`foliage-shadow-${key}-1`;}
 return {depth,distance};
}
