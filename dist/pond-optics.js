import * as THREE from 'three';
import {pondTransmittanceGLSL} from './water-medium.js';

// Air-to-water Snell refraction at the mean horizontal surface. Direction points
// towards the sun; the result follows travelling photons down into the pond.
export function refractedPondRay(sunDirection,out=new THREE.Vector3()){
 const length=sunDirection.length()||1,eta=1/1.333;
 out.set(-sunDirection.x/length*eta,0,-sunDirection.z/length*eta);
 out.y=-Math.sqrt(Math.max(0,1-out.x*out.x-out.z*out.z));return out;
}

const pondFunctions=`
${pondTransmittanceGLSL()}
varying vec3 vPondPoint;
uniform float pondCausticContrast;
uniform sampler2D pondLight0;uniform sampler2D pondLight1;uniform float pondTime;
uniform vec3 pondSunDirection;uniform vec3 pondRefractedUp;uniform vec2 pondRaySlope;
float pondReceiverMask(){
 float depth=-.025-vPondPoint.y;
 float edge=1.-length(vec2(vPondPoint.x/11.48,(vPondPoint.z-5.8)/6.88));
 return smoothstep(0.,.09,depth)*smoothstep(0.,.05,edge)*step(.001,pondSunDirection.y);
}
float pondDensity(sampler2D lightMap,vec2 drift,float depth){
 float deep=step(.875,depth);
 float low=mix(.25,.875,deep),high=mix(.875,1.6,deep);
 // Project each receiver along the refracted sun ray to both baked depth planes.
 vec2 lo=(vPondPoint.xz+pondRaySlope*(low-depth))*.25+drift;
 vec2 hi=(vPondPoint.xz+pondRaySlope*(high-depth))*.25+drift;
 vec3 a=texture2D(lightMap,lo).rgb,b=texture2D(lightMap,hi).rgb;
 return mix(mix(a.r,a.g,deep),mix(b.g,b.b,deep),clamp((depth-low)/(high-low),0.,1.))*6.;
}
vec3 pondSunTransmission(){
 float depth=max(0.,-.025-vPondPoint.y);
 vec2 uv=vPondPoint.xz*.25;
 vec2 warp=vec2(sin(uv.y*4.1+pondTime*.14),cos(uv.x*3.7-pondTime*.11))*.012;
 float a=pondDensity(pondLight0,warp-pondTime*vec2(.025,-.00875),depth);
 float b=pondDensity(pondLight1,-warp-pondTime*vec2(.019,-.00665),depth);
 float density=mix(a,b,.5+.18*sin(pondTime*.19));
 // Mean-one density redistributes sunlight instead of making every patch brighter.
 float focus=mix(1.,density,pondCausticContrast*exp(-depth*.14));
 float path=depth/max(pondRefractedUp.y,.1);
 vec3 incoming=pondBeamTransmittance(path)*focus;
 return mix(vec3(1.),incoming,pondReceiverMask());
}`;

export function pondDirectionalLighting(chunk){
 const start=chunk.indexOf('#if ( NUM_DIR_LIGHTS'),end=chunk.indexOf('#if ( NUM_RECT_AREA_LIGHTS',start);
 if(start<0||end<0)throw new Error('Unsupported Three directional-light chunk');
 const call='RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );';
 const directional=chunk.slice(start,end);
 if(!directional.includes(call))throw new Error('Missing directional light evaluation');
 return chunk.slice(0,start)+directional.replace(call,`
  // Keep renderer shadow visibility; only the selected sun crosses this surface.
  if(dot(inverseTransformDirection(directLight.direction,viewMatrix),pondSunDirection)>.9999){
   directLight.color*=pondSunTransmission();
   directLight.direction=normalize(mix(directLight.direction,transformDirection(pondRefractedUp,viewMatrix),pondReceiverMask()));
  }
  ${call}`)+chunk.slice(end);
}

export function installPondOptics(scene,maps,time,sun,{causticContrast=.48,creek=false}={}){
 const contrast={value:Math.max(0,Math.min(1,causticContrast))},lightMaps=maps.map(value=>({value}));
 for(const map of maps){map.wrapS=map.wrapT=THREE.RepeatWrapping;map.colorSpace=THREE.NoColorSpace;map.flipY=false;map.anisotropy=8;}
 const sunDirection={value:new THREE.Vector3(0,1,0)},refractedUp={value:new THREE.Vector3(0,1,0)},raySlope={value:new THREE.Vector2()};
 const origin=new THREE.Vector3(),target=new THREE.Vector3(),ray=new THREE.Vector3();
 function update(){
  if(sun){sun.getWorldPosition(origin);sun.target.getWorldPosition(target);sunDirection.value.subVectors(origin,target).normalize();}
  refractedPondRay(sunDirection.value,ray);raySlope.value.set(ray.x/-ray.y,ray.z/-ray.y);refractedUp.value.copy(ray).negate();
 }
 update();const materials=new Set();
 scene.traverse(o=>{
  if(!o.isMesh||o.isWater)return;
  if(!creek&&o.userData.waterSide!=='below'&&!/Riverbed sediment|Continuous granite with wet waterline/.test(o.material?.name??''))return;
  const material=o.material;if(!material?.isMeshStandardMaterial||materials.has(material))return;
  materials.add(material);const previous=material.onBeforeCompile,cache=material.customProgramCacheKey();
  material.onBeforeCompile=shader=>{
   previous.call(material,shader);
   Object.assign(shader.uniforms,{pondCausticContrast:contrast,pondLight0:lightMaps[0],pondLight1:lightMaps[1],pondTime:time,pondSunDirection:sunDirection,pondRefractedUp:refractedUp,pondRaySlope:raySlope});
   shader.vertexShader='varying vec3 vPondPoint;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
    vec4 pondPoint=vec4(transformed,1.);
    #ifdef USE_INSTANCING
     pondPoint=instanceMatrix*pondPoint;
    #endif
    vPondPoint=(modelMatrix*pondPoint).xyz;`);
   const functions=creek?pondFunctions.replace('float edge=1.-length(vec2(vPondPoint.x/11.48,(vPondPoint.z-5.8)/6.88));','float edge=1.;').replace('vec3(.55,0.18,0.095)','vec3(.16,.055,.025)').replace('vec3(0.55,0.18,0.095)','vec3(.16,.055,.025)').replace('pondTime*vec2(.025,-.00875)','pondTime*vec2(0.,.52)').replace('pondTime*vec2(.019,-.00665)','pondTime*vec2(.012,.43)'):pondFunctions;
   shader.fragmentShader=functions+'\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_begin>',pondDirectionalLighting(THREE.ShaderChunk.lights_fragment_begin));
  };
  material.customProgramCacheKey=()=>cache+'|pond-depth-caustics-v4'+(creek?'|clear-creek':'');material.needsUpdate=true;
 });
 return {materials:materials.size,update,contrast,lightMaps};
}
