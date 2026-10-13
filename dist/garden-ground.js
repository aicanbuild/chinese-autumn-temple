import * as THREE from 'three';

// Replace baked leaf litter only within the maintained courtyard. The existing
// terrain geometry, collisions and independently sweepable leaves stay aligned.
export async function installGardenGround(terrain,manager){
 const loader=new THREE.TextureLoader(manager);
 const maps=await Promise.all(['garden-moss-runtime.jpg','garden-moss-normal.jpg','garden-moss-rough-runtime.jpg'].map(n=>loader.loadAsync('./assets/'+n)));
 maps.forEach(t=>{t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;t.flipY=false;});maps[0].colorSpace=THREE.SRGBColorSpace;
 let materials=0;
 terrain.traverse(o=>{if(!o.isMesh)return;const m=o.material;
  m.onBeforeCompile=shader=>{
   Object.assign(shader.uniforms,{gardenMoss:{value:maps[0]},gardenMossNormal:{value:maps[1]},gardenMossRough:{value:maps[2]}});
   shader.vertexShader='varying vec2 gardenWorldXZ;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
    gardenWorldXZ=(modelMatrix*vec4(transformed,1.0)).xz;
   `);
   shader.fragmentShader='varying vec2 gardenWorldXZ;\nuniform sampler2D gardenMoss;\nuniform sampler2D gardenMossNormal;\nuniform sampler2D gardenMossRough;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    vec2 gardenXY=vec2(gardenWorldXZ.x,-gardenWorldXZ.y);
    float gardenRadius=length(gardenXY-vec2(0.0,-2.0));
    float gardenEdge=0.7*sin(gardenXY.x*.37)*cos(gardenXY.y*.31);
    float gardenCover=1.0-smoothstep(18.0,28.0,gardenRadius+gardenEdge);
    vec2 gardenUv=vec2(gardenXY.x/1.2,1.0-gardenXY.y/1.2);
    float gardenTone=.78+.12*sin(gardenXY.x*.8+sin(gardenXY.y*.54))+.08*cos(gardenXY.y*1.3);
    diffuseColor.rgb=mix(diffuseColor.rgb,texture2D(gardenMoss,gardenUv).rgb*gardenTone,gardenCover);
   `);
   const normal=`
    vec3 gardenSurfaceNormal=normal;
    ${THREE.ShaderChunk.normal_fragment_maps}
    mat3 gardenTBN=getTangentFrame(-vViewPosition,gardenSurfaceNormal,gardenUv);
    vec3 gardenN=texture2D(gardenMossNormal,gardenUv).xyz*2.0-1.0;
    gardenN.xy*=normalScale;
    normal=normalize(mix(normal,normalize(gardenTBN*gardenN),gardenCover));
   `;
   shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',normal).replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
    roughnessFactor=mix(roughnessFactor,texture2D(gardenMossRough,gardenUv).r,gardenCover);
   `);
  };
  m.customProgramCacheKey=()=> 'maintained-garden-moss-world-v2';m.needsUpdate=true;materials++;
 });
 return {materials,tileMeters:1.2,clearRadius:18,transitionEnd:28};
}
