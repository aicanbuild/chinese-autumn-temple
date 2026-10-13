import * as THREE from 'three';
import {Pass,FullScreenQuad} from 'three/addons/postprocessing/Pass.js';

// Integrate sunlight through the actual directional shadow map, stopping at scene
// depth. Tree leaves, eaves and the bridge therefore carve the same light volume
// as their surface shadows. Quarter-resolution integration keeps the cost bounded.
export class SunlightPass extends Pass {
 constructor(camera,sun){
  super();this.camera=camera;this.sun=sun;
  this.volume=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,depthBuffer:false});
  const vertexShader='varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}';
  this.integrate=new THREE.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{depth:{value:null},shadow:{value:null},inverseProjection:{value:new THREE.Matrix4()},cameraWorld:{value:new THREE.Matrix4()},shadowMatrix:{value:new THREE.Matrix4()},eye:{value:new THREE.Vector3()},sunDirection:{value:new THREE.Vector3()},strength:{value:1},extinction:{value:.010}},vertexShader,fragmentShader:`
   #include <packing>
   varying vec2 vUv;uniform sampler2D depth,shadow;uniform mat4 inverseProjection,cameraWorld,shadowMatrix;uniform vec3 eye,sunDirection;uniform float strength,extinction;
   void main(){
    float d=texture2D(depth,vUv).x;
    vec4 p=inverseProjection*vec4(vUv*2.-1.,d*2.-1.,1.);p/=p.w;p=cameraWorld*p;
    vec3 delta=p.xyz-eye;float distanceToSurface=length(delta);vec3 direction=normalize(delta);
    float lengthAlongRay=min(distanceToSurface,55.);float stepLength=lengthAlongRay/32.;float integral=0.;float transmission=1.;
    float jitter=fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453);
    for(int i=0;i<32;i++){
     vec3 point=eye+direction*(float(i)+jitter)*stepLength;
     vec4 sc=shadowMatrix*vec4(point,1.);vec3 q=sc.xyz/sc.w;
     float inMap=step(0.,q.x)*step(q.x,1.)*step(0.,q.y)*step(q.y,1.)*step(0.,q.z)*step(q.z,1.);
     float visible=step(q.z-.00025,unpackRGBAToDepth(texture2D(shadow,q.xy)))*inMap;
     float density=exp(-max(point.y,0.)*.19)*smoothstep(-.25,.7,point.y);
     float garden=1.-smoothstep(17.,28.,length(point.xz-vec2(0.,3.)));
     float attenuation=exp(-extinction*density*garden*stepLength*strength);
     integral+=transmission*(1.-attenuation)*visible;
     transmission*=attenuation;
    }
    float phase=.30+.75*pow(max(dot(direction,sunDirection),0.),4.);
    // R carries shadowed scattering; G preserves extinction for compositing.
    gl_FragColor=vec4(integral*phase,transmission,0.,min(distanceToSurface,100.)/100.);
   }`});
  this.composite=new THREE.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{tDiffuse:{value:null},volume:{value:this.volume.texture},texel:{value:new THREE.Vector2()},sunColor:{value:new THREE.Color()},skyColor:{value:new THREE.Color(.018,.026,.029)}},vertexShader,fragmentShader:`
   varying vec2 vUv;uniform sampler2D tDiffuse,volume;uniform vec2 texel;uniform vec3 sunColor,skyColor;
   void main(){vec4 center=texture2D(volume,vUv);vec2 sum=vec2(0.);float weight=0.;
    for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++){vec4 s=texture2D(volume,vUv+vec2(float(x),float(y))*texel);float w=exp(-abs(s.a-center.a)*150.)/(1.+float(x*x+y*y));sum+=s.rg*w;weight+=w;}
    vec4 c=texture2D(tDiffuse,vUv);vec2 fog=sum/max(weight,.001);gl_FragColor=vec4(c.rgb*fog.y+sunColor*fog.x+skyColor*(1.-fog.y),c.a);
   }`});
  this.quad=new FullScreenQuad(this.integrate);
 }
 setSize(w,h){this.volume.setSize(Math.max(1,Math.ceil(w/4)),Math.max(1,Math.ceil(h/4)));this.composite.uniforms.texel.value.set(1/this.volume.width,1/this.volume.height);}
 render(renderer,writeBuffer,readBuffer){
  const u=this.integrate.uniforms;u.depth.value=readBuffer.depthTexture;u.shadow.value=this.sun.shadow.map.texture;u.shadowMatrix.value.copy(this.sun.shadow.matrix);u.inverseProjection.value.copy(this.camera.projectionMatrixInverse);u.cameraWorld.value.copy(this.camera.matrixWorld);u.eye.value.copy(this.camera.position);u.sunDirection.value.copy(this.sun.position).sub(this.sun.target.position).normalize();
  this.composite.uniforms.sunColor.value.copy(this.sun.color).multiplyScalar(this.sun.intensity*.32);
  this.quad.material=this.integrate;renderer.setRenderTarget(this.volume);this.quad.render(renderer);
  this.composite.uniforms.tDiffuse.value=readBuffer.texture;this.quad.material=this.composite;renderer.setRenderTarget(this.renderToScreen?null:writeBuffer);this.quad.render(renderer);
 }
 dispose(){this.volume.dispose();this.integrate.dispose();this.composite.dispose();this.quad.dispose();}
}
