import {extractRegion} from './rituals.js';

// Cosine-weighted visibility baked from the actual assembled bridge. Direct
// sunlight remains governed by the shadow map; only local environment light dims.
export function installBridgeContact(material,geometry){
 if(!geometry.getAttribute('_bridge_occlusion')||material.userData.bridgeContactStrength)return;
 const strength={value:1},previous=material.onBeforeCompile,cache=material.customProgramCacheKey();material.userData.bridgeContactStrength=strength;
 material.onBeforeCompile=function(shader,renderer){
  previous.call(this,shader,renderer);shader.uniforms.bridgeContactStrength=strength;
  shader.vertexShader='attribute float _bridge_occlusion; varying float bridgeOcclusion;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nbridgeOcclusion=_bridge_occlusion;');
  shader.fragmentShader='varying float bridgeOcclusion; uniform float bridgeContactStrength;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <aomap_fragment>',`#include <aomap_fragment>
   float bridgeAO=mix(1.0,clamp(bridgeOcclusion,0.0,1.0),bridgeContactStrength);
   reflectedLight.indirectDiffuse*=bridgeAO;
   #if defined(USE_ENVMAP) && defined(STANDARD)
    reflectedLight.indirectSpecular*=computeSpecularOcclusion(saturate(dot(geometryNormal,geometryViewDir)),bridgeAO,material.roughness);
   #endif
  `);
 };
 material.customProgramCacheKey=()=>cache+'-bridge-local-visibility-v1';material.needsUpdate=true;
}

export function replaceBridge(model,bridge,scene){
 const old=extractRegion(model,name=>/^(Polished ebony cedar|Satin gilded bronze)$/.test(name),p=>Math.abs(p.x)<1.43&&p.z> -1.02&&p.z<12.53&&p.y> -1&&p.y<2.4);
 let removedTriangles=0;
 old.traverse(o=>{if(o.isMesh){removedTriangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;o.geometry.dispose();}});
 bridge.name='Blender finished timber bridge';
 bridge.traverse(o=>{if(o.isMesh){installBridgeContact(o.material,o.geometry);o.castShadow=true;o.receiveShadow=true;o.userData.waterClipStatic=true;o.material.envMapIntensity=o.material.metalness>.6?.9:.55;for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;}});
 scene.add(bridge);return {removedTriangles};
}
