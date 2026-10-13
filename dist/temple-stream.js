import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {CREEK_CURRENT_SCALE,CREEK_CURRENT_SPEED} from './water-current.js';

export const STREAM_START=-72,STREAM_END=20,STREAM_LEVEL=-.025;
export function streamCenter(z){return 15+.7*Math.cos((z+9)*.22);}
export function streamWidth(z){return (1.07+.17*Math.sin(z*.51)+.11*Math.sin(z*1.12))*Math.exp(Math.min(0,(z+14)/28))*Math.min(1,.14+(z-STREAM_START)/3,.14+(STREAM_END-z)/2);}
export function streamContains(x,z,margin=0){return z>=STREAM_START&&z<=STREAM_END&&Math.abs(x-streamCenter(z))<streamWidth(z)*.94+margin;}

export function installTempleStream(root,scene,{normal,roughness,stoneColor,moss,sandNormal,waterNormal}){
 for(const t of [normal,roughness,stoneColor,moss,sandNormal]){t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;t.flipY=false;}
 root.name='East garden clear stream';root.updateMatrixWorld(true);let surface,headwater;const headwaterTime={value:0};
 root.traverse(o=>{if(!o.isMesh)return;
  if(o.userData.streamAssembly==='water surface'){surface=o;return;}
  if(o.userData.streamAssembly==='headwater surface'){
   headwater=o;o.castShadow=false;o.receiveShadow=true;o.userData.waterSide='above';
   const ripples=waterNormal;
   if(!ripples)throw new Error('Missing headwater normal map');
   o.material=new THREE.MeshPhysicalMaterial({color:'#adc6b5',transparent:true,opacity:.28,roughness:.10,metalness:0,ior:1.333,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:.75,normalMap:ripples,normalScale:new THREE.Vector2(.26,.26),depthWrite:false,side:THREE.DoubleSide});
   o.material.onBeforeCompile=shader=>{shader.uniforms.headwaterTime=headwaterTime;shader.fragmentShader='uniform float headwaterTime;\n'+shader.fragmentShader;shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',THREE.ShaderChunk.normal_fragment_maps.replace('vNormalMapUv',`(vNormalMapUv+vec2(0.,-headwaterTime*${(CREEK_CURRENT_SPEED*.7).toFixed(3)}))`));};
   o.material.customProgramCacheKey=()=> 'sloping-headwater-flow-v2';return;
  }
  o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;
  const m=o.material;m.envMapIntensity=.38;
  if(m.name.includes('stones')){m.map=stoneColor;m.normalMap=normal;m.normalScale.set(.32,.32);m.roughnessMap=roughness;m.roughness=.84;}
  if(m.name.includes('gravel')){m.normalMap=sandNormal;m.normalScale.set(.28,.28);const prior=m.onBeforeCompile;m.onBeforeCompile=shader=>{prior.call(m,shader);shader.uniforms.creekMoss={value:moss};shader.vertexShader='varying vec3 creekGround;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\ncreekGround=(modelMatrix*vec4(transformed,1.)).xyz;');shader.fragmentShader='varying vec3 creekGround;uniform sampler2D creekMoss;\n'+shader.fragmentShader;shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
float cx=15.+.7*cos((creekGround.z+9.)*.22);
float width=(1.07+.17*sin(creekGround.z*.51)+.11*sin(creekGround.z*1.12))*exp(min(0.,(creekGround.z+14.)/28.))*min(1.,min(.14+(creekGround.z+72.)/3.,.14+(20.-creekGround.z)/2.));
float bank=abs(creekGround.x-cx)/max(.1,width);
float cover=smoothstep(1.02,1.65,bank+.12*sin(creekGround.z*6.)+.08*sin(creekGround.x*11.));
vec2 uv=vec2(creekGround.x/1.2,1.+creekGround.z/1.2);
vec3 moss=texture2D(creekMoss,uv).rgb*(.78+.12*sin(creekGround.x*.8+sin(-creekGround.z*.54))+.08*cos(creekGround.z*1.3));
diffuseColor.rgb=mix(diffuseColor.rgb*vec3(.81,.78,.64),moss,cover);`);};m.customProgramCacheKey=()=> 'creek-moss-transition-v2';}
  if(m.map){m.map.anisotropy=8;m.map.wrapS=m.map.wrapT=THREE.RepeatWrapping;}
 });
 if(!surface)throw new Error('Missing authored creek surface');
 const waterGeometry=surface.geometry.clone().applyMatrix4(surface.matrixWorld);surface.removeFromParent();scene.add(root);
 return {root,waterGeometry,headwater,update(time){headwaterTime.value=time;}};
}

export function combineWaterGeometry(pond,stream){
 const local=new THREE.Matrix4().compose(new THREE.Vector3(0,STREAM_LEVEL,5.8),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),-Math.PI/2),new THREE.Vector3(1,1,1)).invert();
 const creek=stream.clone().applyMatrix4(local);
 const inputs=[pond,creek].map(g=>{g=g.clone();if(!g.index)g.setIndex(Array.from({length:g.attributes.position.count},(_,i)=>i));for(const key of Object.keys(g.attributes))if(!['position','normal','uv'].includes(key))g.deleteAttribute(key);if(!g.attributes.uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count*2),2));return g;});
 const merged=mergeGeometries(inputs);if(!merged)throw new Error('Cannot combine creek and pond surfaces');merged.userData.surfaceRegions=inputs.map(g=>{g.computeBoundingBox();return g.boundingBox.clone();});inputs.forEach(g=>g.dispose());creek.dispose();return merged;
}

// Advect normal maps through a rock-aware vector field. Offset phases crossfade
// before either resets, so the water has no visible repeating backward jump.
export function streamWaterFragment(base){
 return base.replace('#include <common>',`#include <common>
 uniform sampler2D streamFlow,streamNormal0,streamNormal1;
 vec3 creekRipples(vec2 p,vec2 velocity,float clock){
  float a=fract(clock/1.25),b=fract(clock/1.25+.5);
  float blend=abs(a*2.-1.);
  // Larger travelling features survive the overview camera and low FPS;
  // fine ripples ride the same current rather than flickering in place.
  vec2 uv=p*1.05;
  vec3 n0=texture2D(streamNormal0,uv-velocity*a*1.3125).rgb;
  vec3 n1=texture2D(streamNormal0,uv-velocity*b*1.3125).rgb;
  vec3 n=mix(n0,n1,blend);
  vec3 fine=mix(texture2D(streamNormal1,p*3.4-velocity*a*4.25).rgb,texture2D(streamNormal1,p*3.4-velocity*b*4.25).rgb,blend);
  return mix(n,fine,.24);
 }`)
 .replace('// calculate the fresnel term',`
  vec3 creekPoint=cameraPosition-vToEye;
  bool creek=creekPoint.x>11.7;
  vec3 creekFlow=vec3(0.);
  vec3 creekNormal=vec3(.5,.5,1.);
  if(creek){
   creekFlow=texture2D(streamFlow,vec2((creekPoint.x-12.)/6.,(creekPoint.z+72.)/92.)).rgb;
   vec2 velocity=(creekFlow.rg*2.-1.)*1.2*${CREEK_CURRENT_SCALE.toFixed(2)};
   creekNormal=creekRipples(creekPoint.xz,velocity,pondTime);
   float strength=.84+.10*min(length(velocity),2.6)+.36*creekFlow.b;
   normal=normalize(vec3((creekNormal.r*2.-1.)*strength,max(creekNormal.b*2.-1.,.4),(creekNormal.g*2.-1.)*strength));
  }
  // calculate the fresnel term`)
 .replace('vec3 transmission=pondBeamTransmittance(waterPath);','vec3 transmission=creek?exp(-vec3(.16,.055,.025)*waterPath):pondBeamTransmittance(waterPath);')
 .replace('gl_FragColor=vec4(mix(submerged,reflectColor.rgb,reflectance)+waterSunColor*glint,1.);',`
  vec3 waterRadiance=mix(submerged,reflectColor.rgb,reflectance)+waterSunColor*glint;
  vec2 foamVelocity=(creekFlow.rg*2.-1.)*1.2*${CREEK_CURRENT_SCALE.toFixed(2)};
  float movingCrest=creek?creekMovingCrests(creekPoint.xz,foamVelocity,pondTime):0.;
  float foam=creek?(creekFlow.b*.72+.075)*movingCrest:0.;
  gl_FragColor=vec4(mix(waterRadiance,vec3(.76,.82,.78),foam),1.);`);
}

export function installStreamUniforms(material,flow,normals){
 flow.flipY=false;flow.colorSpace=THREE.NoColorSpace;flow.wrapS=flow.wrapT=THREE.ClampToEdgeWrapping;
 for(const n of normals){n.wrapS=n.wrapT=THREE.RepeatWrapping;n.colorSpace=THREE.NoColorSpace;n.anisotropy=8;}
 Object.assign(material.uniforms,{streamFlow:{value:flow},streamNormal0:{value:normals[0]},streamNormal1:{value:normals[1]}});
}
