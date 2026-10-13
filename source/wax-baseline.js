// Frozen former wax finish for the local visual comparison; not shipped.
import * as THREE from "three";
export function finishCandleWax(source,layout){
 const material=source.clone();material.roughness=.43;
 const tips=layout.flames.map(([x,y,z])=>new THREE.Vector3(x,y-.015,z));
 material.onBeforeCompile=shader=>{
  shader.uniforms.waxTips={value:tips};
  shader.vertexShader='varying vec3 waxWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\nwaxWorld=(modelMatrix*vec4(transformed,1.)).xyz;');
  shader.fragmentShader='varying vec3 waxWorld;uniform vec3 waxTips[4];\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
   float waxGlow=0.,waxPool=0.;
   for(int i=0;i<4;i++){
    vec3 d=waxWorld-waxTips[i];float radial=length(d.xz);
    waxGlow=max(waxGlow,exp(-radial*24.-abs(d.y)*55.));
    waxPool=max(waxPool,(1.-smoothstep(.018,.040,radial))*(1.-smoothstep(.010,.043,abs(d.y))));
   }
   float waxGrain=sin(waxWorld.x*1100.)*sin(waxWorld.y*975.)*sin(waxWorld.z*1050.);
   roughnessFactor=mix(clamp(roughnessFactor+waxGrain*.035,.30,.60),.19,waxPool);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\ntotalEmissiveRadiance+=vec3(.28,.026,.003)*waxGlow;');
 };
 material.customProgramCacheKey=()=> 'warm-pigmented-candle-wax-v1';return material;
}
