import * as THREE from 'three';

export const SMOKE_HEIGHT=1.4,SMOKE_RISE=.28,SMOKE_LIFETIME=SMOKE_HEIGHT/SMOKE_RISE+.3;

// Emission travels upward: lighting does not fill the entire column instantly,
// and smoke already in the air survives the end of burning and stick replacement.
export function createIncenseSmoke(parent,phase=0){
 const uniforms={uTime:{value:0},uStart:{value:1e6},uStop:{value:1e6},uPhase:{value:phase}};
 const geometry=new THREE.BoxGeometry(.32,SMOKE_HEIGHT,.28).translate(0,SMOKE_HEIGHT/2,0);
 const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.BackSide,uniforms,
  vertexShader:`varying vec3 localPoint;varying vec3 localEye;
   void main(){localPoint=position;localEye=(inverse(modelMatrix)*vec4(cameraPosition,1.)).xyz;
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform float uTime,uStart,uStop,uPhase;varying vec3 localPoint,localEye;
   float densityAt(vec3 p){
    float h=p.y/1.4;
    if(h<=0.||h>=1.)return 0.;
    float born=uTime-p.y/.28;
    float emission=smoothstep(uStart,uStart+.3,born)*(1.-smoothstep(uStop,uStop+.2,born));
    float bend=smoothstep(.10,.85,h);
    vec2 center=vec2(.032*sin(h*11.-uTime*.95+uPhase)+.012*sin(h*23.-uTime*1.7+uPhase),.026*sin(h*14.-uTime*.7+uPhase*1.3))*bend;
    float radius=.005+.024*pow(h,.95);
    vec2 q=(p.xz-center)/radius;
    float wisps=.72+.18*sin(p.y*31.-uTime*8.68+uPhase)+.10*sin(p.y*57.-uTime*15.96+uPhase*2.);
    float crossSection=exp(-2.*dot(q,q));
    return emission*crossSection*wisps*(.005/radius)*smoothstep(0.,.008,p.y)*(1.-smoothstep(.58,1.,h));
   }
   void main(){
    vec3 ray=normalize(localPoint-localEye);
    vec3 safeRay=mix(vec3(-1.),vec3(1.),step(vec3(0.),ray))*max(abs(ray),vec3(.00001));
    vec3 a=(vec3(-.16,0.,-.14)-localEye)/safeRay,b=(vec3(.16,1.4,.14)-localEye)/safeRay;
    vec3 lo=min(a,b),hi=max(a,b);
    float start=max(0.,max(lo.x,max(lo.y,lo.z))),end=min(hi.x,min(hi.y,hi.z));if(end<=start)discard;
    float ds=(end-start)/48.,opticalDepth=0.;
    for(int k=0;k<48;k++)opticalDepth+=densityAt(localEye+ray*(start+(float(k)+.5)*ds))*22.*ds;
    float alpha=1.-exp(-opticalDepth);if(alpha<.0005)discard;
    // Quiet, diffuse room illumination; this is an artistic participating medium,
    // not a fluid simulation or an additional emissive light source.
    gl_FragColor=vec4(.54,.56,.53,alpha);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`
 });
 const mesh=new THREE.Mesh(geometry,material);mesh.name='Three-dimensional incense plume';mesh.visible=false;mesh.userData.noAO=true;mesh.userData.waterSide='above';parent.add(mesh);
 // Keep the last extinguished plume separate if the replacement is lit quickly.
 // It must neither jump to the new tip nor disappear when emission restarts.
 const tail=mesh.clone();tail.material=material.clone();tail.name='Detached incense after-smoke';parent.add(tail);
 let wasBurning=false,stop=-Infinity,tailStop=-Infinity;
 return {mesh,tail,update(time,burning,tip){
  uniforms.uTime.value=time;
  if(burning&&!wasBurning){
   if(Number.isFinite(stop)&&time-stop<SMOKE_LIFETIME){
    tail.position.copy(mesh.position);tail.material.uniforms.uStart.value=uniforms.uStart.value;tail.material.uniforms.uStop.value=stop;tailStop=stop;
   }
   uniforms.uStart.value=time;uniforms.uStop.value=1e6;stop=Infinity;
  }
  if(!burning&&wasBurning){stop=time;uniforms.uStop.value=time;}
  if(burning)mesh.position.copy(tip);
  mesh.visible=burning||time-stop<SMOKE_LIFETIME;
  tail.material.uniforms.uTime.value=time;tail.visible=time-tailStop<SMOKE_LIFETIME;
  wasBurning=burning;
 },dispose(){geometry.dispose();material.dispose();tail.material.dispose();mesh.removeFromParent();tail.removeFromParent();}};
}
