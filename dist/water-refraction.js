import * as THREE from 'three';

// Snell at the mean horizontal interface. The safeguarded solve uses the maximum
// underwater lateral travel, keeping grazing views well conditioned.
export function waterSurfaceExit(point,eye,height=-.025,out=new THREE.Vector3()){
 const dx=point.x-eye.x,dz=point.z-eye.z,L=Math.hypot(dx,dz),D=height-point.y,H=eye.y-height,n=1.333;
 if(D<=0||H<=.001||L<1e-7)return out.set(point.x,height,point.z);
 const maximum=Math.min(L/D,1/Math.sqrt(n*n-1));
 let u=Math.min(maximum,L/Math.sqrt(n*n*H*H+(n*n-1)*L*L)),lo=0,hi=maximum;
 for(let i=0;i<5;i++){
  const x=L-D*u,a=Math.hypot(x,H),b=Math.hypot(u,1),f=x/a-n*u/b;
  if(f>0)lo=u;else hi=u;
  const derivative=-D*H*H/(a*a*a)-n/(b*b*b);
  u=Math.max(lo,Math.min(hi,u-f/derivative));
 }
 const residual=(L-D*u)/Math.hypot(L-D*u,H)-n*u/Math.hypot(u,1);
 // |f'| >= .38 on this bracket: only difficult grazing configurations need
 // the longer fallback, with a maximum remaining bracket below 0.14 mm at 8 m.
 if(Math.abs(residual)*D>.00002*.38){for(let i=0;i<16;i++){const q=(lo+hi)/2,x=L-D*q;if(x/Math.hypot(x,H)>n*q/Math.hypot(q,1))lo=q;else hi=q;}u=(lo+hi)/2;}
 const x=L-D*u;
 return out.set(eye.x+dx*x/L,height,eye.z+dz*x/L);
}
export const waterProjectionGLSL=`
uniform float waterRefractionPass;
uniform float waterInterfaceY;
vec3 waterSurfaceExit(vec3 p,vec3 eye){
 float D=waterInterfaceY-p.y,H=eye.y-waterInterfaceY;
 vec2 delta=p.xz-eye.xz;float L=length(delta),n=1.333;
 if(D<=0.||H<=.001||L<.000001)return vec3(p.x,waterInterfaceY,p.z);
 float maximum=min(L/D,1./sqrt(n*n-1.));
 float u=min(maximum,L/sqrt(n*n*H*H+(n*n-1.)*L*L)),low=0.,high=maximum;
 for(int i=0;i<5;i++){
  float x=L-D*u,a=sqrt(x*x+H*H),b=sqrt(u*u+1.),f=x/a-n*u/b;
  if(f>0.)low=u;else high=u;
  float derivative=-D*H*H/(a*a*a)-n/(b*b*b);
  u=clamp(u-f/derivative,low,high);
 }
 float x=L-D*u,residual=x/sqrt(x*x+H*H)-n*u/sqrt(u*u+1.);
 if(abs(residual)*D>.00002*.38){
  for(int i=0;i<16;i++){float q=(low+high)*.5,air=L-D*q;if(air/sqrt(air*air+H*H)>n*q/sqrt(q*q+1.))low=q;else high=q;}
  u=(low+high)*.5;
 }
 x=L-D*u;
 return vec3(eye.x+delta.x*x/L,waterInterfaceY,eye.z+delta.y*x/L);
}`;
export function installWaterRefraction(scene,height=-.025){
 const pass={value:0},level={value:height},materials=new Set(),objects=[];
 scene.traverse(o=>{
  if(!o.isMesh||o.isWater)return;objects.push(o);
  for(const m of Array.isArray(o.material)?o.material:[o.material]){
   if(!m||materials.has(m)||!m.isMeshStandardMaterial&&!m.isMeshBasicMaterial)continue;
   materials.add(m);const previous=m.onBeforeCompile,cache=m.customProgramCacheKey();
   m.onBeforeCompile=shader=>{
    previous.call(m,shader);shader.uniforms.waterRefractionPass=pass;shader.uniforms.waterInterfaceY=level;
    shader.vertexShader=waterProjectionGLSL+'\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
     if(waterRefractionPass>.5){
      vec4 refractionPoint=vec4(transformed,1.);
      #ifdef USE_BATCHING
       refractionPoint=batchingMatrix*refractionPoint;
      #endif
      #ifdef USE_INSTANCING
       refractionPoint=instanceMatrix*refractionPoint;
      #endif
      refractionPoint=modelMatrix*refractionPoint;
      if(refractionPoint.y<waterInterfaceY){
       vec3 surfaceExit=waterSurfaceExit(refractionPoint.xyz,cameraPosition);
       vec4 refractedClip=projectionMatrix*viewMatrix*vec4(surfaceExit,1.);
       gl_Position.xy=refractedClip.xy/max(refractedClip.w,.00001)*gl_Position.w;
      }
     }`);
   };
   m.customProgramCacheKey=()=>cache+'|water-geometry-refraction-v2';m.needsUpdate=true;
  }
 });
 return {materials:materials.size,capture(mode){
  if(mode!=='refraction')return ()=>{};
  const old=pass.value,culled=objects.map(o=>o.frustumCulled);pass.value=1;
  // Original world-space bounds cannot cull a nonlinearly refracted projection.
  objects.forEach(o=>{o.frustumCulled=false;});
  return ()=>{pass.value=old;objects.forEach((o,i)=>{o.frustumCulled=culled[i];});};
 }};
}
// Depth retains original clip Z/W while XY is refracted. Recover travel on the
// Snell ray with the exact oblique projection used for the capture.
export function applyWaterRefraction(fragment){
 return fragment.replace('uniform mat4 refractionInverseViewProjection;','uniform mat4 refractionInverseViewProjection;\n  uniform mat4 refractionViewProjection;')
 .replace('vec3 submergedPoint=capturedPoint.xyz/capturedPoint.w;',`
  vec3 apparentPoint=capturedPoint.xyz/capturedPoint.w;
  vec3 airRay=normalize(apparentPoint-cameraPosition);
  vec3 surfaceExit=cameraPosition+airRay*((-.025-cameraPosition.y)/min(airRay.y,-.0001));
  vec3 underwaterRay=refract(airRay,vec3(0.,1.,0.),1./1.333);
  vec4 entryClip=refractionViewProjection*vec4(surfaceExit,1.);
  vec4 rayClip=refractionViewProjection*vec4(underwaterRay,0.);
  float ndcDepth=capturedDepth*2.-1.;
  float denominator=ndcDepth*rayClip.w-rayClip.z;
  float refractionTravel=abs(denominator)>.000001?(entryClip.z-ndcDepth*entryClip.w)/denominator:0.;
  refractionTravel=clamp(refractionTravel,0.,8.);
  vec3 submergedPoint=surfaceExit+underwaterRay*refractionTravel;`)
 .replace('float waterPath=clamp((-.025-submergedPoint.y)/max(abs(captureRay.y),.08),0.,8.);','float waterPath=refractionTravel;');
}
