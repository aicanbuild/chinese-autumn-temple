import * as THREE from 'three';
import {applyWaterRefraction} from '../dist/water-refraction.js';

// Shared with regression checks: reconstruct using the oblique capture matrix.
export function capturedWaterPath(uv,depth,inverseViewProjection,eye,waterY=-.025){
 const p=new THREE.Vector4(uv.x*2-1,uv.y*2-1,depth*2-1,1).applyMatrix4(inverseViewProjection);p.multiplyScalar(1/p.w);
 const ray=new THREE.Vector3(p.x-eye.x,p.y-eye.y,p.z-eye.z).normalize();
 return Math.min(8,Math.max(0,waterY-p.y)/Math.max(Math.abs(ray.y),.08));
}

export function depthWaterFragment(base,{refraction=true}={}){
 const fragment=base.replace('#include <common>',`#include <common>
  uniform sampler2D tRefractionDepth;
  uniform mat4 refractionInverseViewProjection;`)
 .replace('vec3 normal = normalize( vec3( normalColor.r * 2.0 - 1.0, normalColor.b,  normalColor.g * 2.0 - 1.0 ) );',
  'vec3 normal = normalize(vec3((normalColor.r * 2.0 - 1.0)*.42, max(normalColor.b*2.-1.,.001), (normalColor.g * 2.0 - 1.0)*.42));')
 .replace('normal.xz * 0.05','normal.xz * 0.010')
 .replace('gl_FragColor = vec4( color, 1.0 ) * mix( refractColor, reflectColor, reflectance );',`
  vec2 depthUV=clamp(uv,vec2(.001),vec2(.999));
  float capturedDepth=texture2D(tRefractionDepth,depthUV).x;
  vec4 capturedPoint=refractionInverseViewProjection*vec4(depthUV*2.-1.,capturedDepth*2.-1.,1.);
  vec3 submergedPoint=capturedPoint.xyz/capturedPoint.w;
  vec3 captureRay=normalize(submergedPoint-cameraPosition);
  float waterPath=clamp((-.025-submergedPoint.y)/max(abs(captureRay.y),.08),0.,8.);
  if(capturedDepth>.99999)waterPath=2.;
  vec3 transmission=exp(-vec3(.55,.18,.095)*waterPath);
  vec3 submerged=refractColor.rgb*transmission+vec3(.006,.025,.029)*(1.-transmission);
  vec3 halfDirection=normalize(toEye+waterSunDirection);
  float glint=pow(max(dot(normal,halfDirection),0.),420.)*(.24/3.7);
  // Reflected sky and temple radiance never pass through the absorption term.
  gl_FragColor=vec4(mix(submerged,reflectColor.rgb,reflectance)+waterSunColor*glint,1.);`);
 return refraction?applyWaterRefraction(fragment):fragment;
}
