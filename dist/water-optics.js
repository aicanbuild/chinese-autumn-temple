import * as THREE from 'three';
import {applyWaterRefraction} from './water-refraction.js';
import {pondTransmittanceGLSL} from './water-medium.js';

// Shared with regression checks: reconstruct using the oblique capture matrix.
export function capturedWaterPath(uv,depth,inverseViewProjection,eye,waterY=-.025){
 const p=new THREE.Vector4(uv.x*2-1,uv.y*2-1,depth*2-1,1).applyMatrix4(inverseViewProjection);p.multiplyScalar(1/p.w);
 const ray=new THREE.Vector3(p.x-eye.x,p.y-eye.y,p.z-eye.z).normalize();
 return Math.min(8,Math.max(0,waterY-p.y)/Math.max(Math.abs(ray.y),.08));
}

// GGX with correlated Smith masking, evaluated in linear radiance. The base
// perceptual roughness matches the authored Blender water (.075). Sun radius
// and pixel footprint enter as a small slope-variance approximation.
export function waterSunSpecularGLSL(){return `
 float pondSunSpecular(vec3 n,vec3 v,vec3 l,float pixelVariance,float f0){
  float nv=dot(n,v),nl=dot(n,l);
  if(nv<=0.||nl<=0.)return 0.;
  vec3 h=normalize(v+l);float nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);
  float a2=.000031640625+.000005405625+clamp(pixelVariance,0.,.01);
  vec3 nxh=cross(n,h);float denominator=dot(nxh,nxh)+nh*nh*a2;
  float distribution=a2/(3.141592653589793*denominator*denominator);
  float masking=.5/max(nl*sqrt(nv*nv*(1.-a2)+a2)+nv*sqrt(nl*nl*(1.-a2)+a2),1.e-7);
  float fresnel=F_Schlick(f0,1.,vh);
  return distribution*masking*fresnel*nl;
 }`;}

export function depthWaterFragment(base,{refraction=true}={}){
 const fragment=base.replace('#include <common>',`#include <common>
  uniform sampler2D tRefractionDepth;
  uniform mat4 refractionInverseViewProjection;
  ${pondTransmittanceGLSL()}
  ${waterSunSpecularGLSL()}`)
 .replace('vec3 normal = normalize( vec3( normalColor.r * 2.0 - 1.0, normalColor.b,  normalColor.g * 2.0 - 1.0 ) );',
  'vec3 normal = normalize(vec3((normalColor.r * 2.0 - 1.0)*.42, max(normalColor.b*2.-1.,.001), (normalColor.g * 2.0 - 1.0)*.42));')
 .replace('normal.xz * 0.05','normal.xz * 0.010')
 // The garden is viewed mostly at grazing angles. Keep captured silhouettes
 // subordinate to the clear bed instead of allowing a full dark mirror there.
 // This is an art-directed cap on planar scenery, not on the direct sun lobe.
 .replace('float reflectance = reflectivity + ( 1.0 - reflectivity ) * pow( ( 1.0 - theta ), 5.0 );',
  'float reflectance = min(.16, reflectivity + (1.0-reflectivity)*pow(1.0-theta,5.0));')
 .replace('gl_FragColor = vec4( color, 1.0 ) * mix( refractColor, reflectColor, reflectance );',`
  vec2 depthUV=clamp(uv,vec2(.001),vec2(.999));
  float capturedDepth=texture2D(tRefractionDepth,depthUV).x;
  vec4 capturedPoint=refractionInverseViewProjection*vec4(depthUV*2.-1.,capturedDepth*2.-1.,1.);
  vec3 submergedPoint=capturedPoint.xyz/capturedPoint.w;
  vec3 captureRay=normalize(submergedPoint-cameraPosition);
  float waterPath=clamp((-.025-submergedPoint.y)/max(abs(captureRay.y),.08),0.,8.);
  if(capturedDepth>.99999)waterPath=2.;
  vec3 transmission=pondBeamTransmittance(waterPath);
  vec3 submerged=refractColor.rgb*transmission+vec3(.006,.025,.029)*(1.-transmission);
  vec3 halfDirection=normalize(toEye+waterSunDirection);
  vec3 specularSlope=normal-halfDirection;
  vec3 slopeDX=dFdx(specularSlope),slopeDY=dFdy(specularSlope);
  float pixelVariance=.25*(dot(slopeDX,slopeDX)+dot(slopeDY,slopeDY));
  float glint=pondSunSpecular(normal,toEye,waterSunDirection,pixelVariance,reflectivity);
  // Reflected sky and temple radiance never pass through the absorption term.
  gl_FragColor=vec4(mix(submerged,reflectColor.rgb,reflectance)+waterSunColor*glint,1.);`);
 return refraction?applyWaterRefraction(fragment):fragment;
}
