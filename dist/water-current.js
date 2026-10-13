// Metres and seconds. Broad travelling ripples remain visible from the garden
// camera; shorter ripples carry the same current instead of boiling in place.
export const POND_CURRENT={x:.10,z:-.035};
// Reference: 6.0–6.3 s of the supplied recording. Water highlights change
// appreciably within 0.1 s, while the foreground rock remains stationary.
// This is an apparent-motion calibration, not a recovered physical velocity.
export const CREEK_CURRENT_SPEED=6.3;
export const CREEK_CURRENT_SCALE=CREEK_CURRENT_SPEED/.45;
export function waterCurrentGLSL(){return `
 vec2 travellingWaterSlope(vec2 p,float t,bool creek){
  if(creek)return vec2(0.); // Creek normals come from its advected relief, not a global sine train.
  vec2 direction=creek?vec2(0.,1.):vec2(.944,-.330);
  vec2 crossDirection=vec2(-direction.y,direction.x);
  float along=dot(p,direction),across=dot(p,crossDirection);
  float speed=creek?${CREEK_CURRENT_SPEED.toFixed(3)}:.19;
  float a=(along-speed*t)*(creek?2.8:4.3)+.25*sin(across*2.1);
  float b=(along-speed*.83*t)*(creek?8.2:9.7)+across*1.8;
  float c=creek?dot(p-direction*speed*t,vec2(.71,.71))*2.4:dot(p,vec2(.71,.71))*2.4-t*.63;
  float force=creek?1.85:1.;
  return force*(direction*(.065*cos(a)+.032*cos(b))
   +crossDirection*(.008*cos(a)*cos(across*2.1)+.006*cos(b))
   +vec2(.71,.71)*.024*cos(c));
 }
 float creekCrestSample(vec2 q){
  float broad=sin(q.y*5.2+sin(q.x*3.2)*.7)+.24*sin(q.y*11.7+q.x*7.2);
  float breaks=.5+.5*sin(q.y*3.7-q.x*5.1);
  return smoothstep(.60,.99,broad)*smoothstep(.12,.76,breaks);
 }
 float creekMovingCrests(vec2 p,vec2 velocity,float t){
  float a=fract(t/1.25),b=fract(t/1.25+.5),blend=abs(a*2.-1.);
  return mix(creekCrestSample(p-velocity*a*1.25),creekCrestSample(p-velocity*b*1.25),blend);
 }`;}

export function currentWaterFragment(base){
 return base.replace('#include <common>','#include <common>\n'+waterCurrentGLSL())
 .replace('vec4 reflectColor = texture2D( tReflectionMap, vec2( 1.0 - uv.x, uv.y ) );',`
  vec2 reflectionUV=coord.xy+coord.z*normal.xz*.018;
  vec4 reflectColor=texture2D(tReflectionMap,vec2(1.-reflectionUV.x,reflectionUV.y));`)
 .replace('// calculate the fresnel term',`
  vec3 currentPoint=cameraPosition-vToEye;
  vec2 currentSlope=travellingWaterSlope(currentPoint.xz,pondTime,currentPoint.x>11.7);
  normal=normalize(normal+vec3(currentSlope.x,0.,currentSlope.y));
  // calculate the fresnel term`);
}
