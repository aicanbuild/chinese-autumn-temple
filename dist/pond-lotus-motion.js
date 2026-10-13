import * as THREE from 'three';
export const POND_SWAY_PADDING=.031;
export function lotusSway(x,y,z,time){
 const s=Math.max(0,Math.min(1,(y+1.05)/1.75)),w=s*s*(3-2*s),dw=6*s*(1-s)/1.75;
 const a=time*.65+x*.32+z*.27,b=time*1.07-z*.45+1.8,c=time*.49+x*.19-z*.31;
 const fx=.020*Math.sin(a)+.004*Math.sin(b),fz=.014*Math.cos(c)+.003*Math.sin(b);
 return {position:[x+w*fx,y,z+w*fz],jacobian:[1+w*.0064*Math.cos(a),dw*fx,w*(.0054*Math.cos(a)-.0018*Math.cos(b)),0,1,0,-w*.00266*Math.sin(c),dw*fz,1+w*(.00434*Math.sin(c)-.00135*Math.cos(b))]};
}
const declarations=`
uniform float pondSwayTime;
attribute vec2 pondSwayWeight;
void pondSwayField(vec3 p,out vec2 wind,out vec4 gradient){
 float a=pondSwayTime*.65+p.x*.32+p.z*.27;
 float b=pondSwayTime*1.07-p.z*.45+1.8;
 float c=pondSwayTime*.49+p.x*.19-p.z*.31;
 wind=vec2(.020*sin(a)+.004*sin(b),.014*cos(c)+.003*sin(b));
 gradient=vec4(.0064*cos(a),.0054*cos(a)-.0018*cos(b),-.00266*sin(c),.00434*sin(c)-.00135*cos(b));
}
vec3 pondSwayPosition(vec3 p){
 if(pondSwayWeight.x<=0.)return p;
 vec2 wind;vec4 gradient;pondSwayField(p,wind,gradient);
 return p+vec3(wind.x,0.,wind.y)*pondSwayWeight.x;
}
vec3 pondSwayNormal(vec3 p,vec3 n){
 if(pondSwayWeight.x<=0.)return n;
 vec2 wind;vec4 g;pondSwayField(p,wind,g);
 float w=pondSwayWeight.x,a=1.+w*g.x,c=w*g.y,d=w*g.z,f=1.+w*g.w,det=a*f-c*d;
 vec2 xz=vec2(f*n.x-d*n.z,-c*n.x+a*n.z)/det;
 return normalize(vec3(xz.x,n.y-pondSwayWeight.y*dot(wind,xz),xz.y));
}`;
export function applyPondLotusSway(shader,time){
 shader.uniforms.pondSwayTime=time;shader.vertexShader=declarations+'\n'+shader.vertexShader;
 shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n transformed=pondSwayPosition(transformed);');
 shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>','#include <beginnormal_vertex>\n objectNormal=pondSwayNormal(position,objectNormal);');
}
function decorate(material,time){
 const previous=material.onBeforeCompile,key=material.customProgramCacheKey();
 material.onBeforeCompile=function(shader,renderer){previous.call(this,shader,renderer);applyPondLotusSway(shader,time);};
 material.customProgramCacheKey=()=>key+'|pond-lotus-sway-1';material.needsUpdate=true;
}
export function installPondLotusMotion(root,time,aoNormalMaterial){
 root.updateMatrixWorld(true);let meshes=0,vertices=0;const materials=new Set();
 const identity=new THREE.Matrix4();
 root.traverse(o=>{
  if(!o.isMesh)return;
  // This asset exports world-space vertices without object transforms. Reject
  // a changed layout instead of separating the leaf and its supporting stalk.
  if(!o.matrixWorld.equals(identity))throw new Error('Pond lotus motion requires world-space asset geometry');
  const p=o.geometry.attributes.position,weights=new Float32Array(p.count*2);
  for(let i=0;i<p.count;i++){const s=Math.max(0,Math.min(1,(p.getY(i)+1.05)/1.75));weights[i*2]=s*s*(3-2*s);weights[i*2+1]=6*s*(1-s)/1.75;}
  o.geometry.setAttribute('pondSwayWeight',new THREE.BufferAttribute(weights,2));
  o.geometry.computeBoundingSphere();o.geometry.boundingSphere.radius+=POND_SWAY_PADDING;
  o.userData.waterClipStatic=false;o.userData.waterMotionPadding=POND_SWAY_PADDING;o.userData.aoAnimated=true;o.userData.aoMotionSpeed=.021;
  if(!materials.has(o.material)){decorate(o.material,time);materials.add(o.material);}
  o.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,side:o.material.side});
  o.customDistanceMaterial=new THREE.MeshDistanceMaterial({side:o.material.side});
  decorate(o.customDepthMaterial,time);decorate(o.customDistanceMaterial,time);meshes++;vertices+=p.count;
 });
 // SSAO renders an override normal material. Explicit zero generic attributes
 // leave every non-lotus object exactly static in that same normal pass.
 aoNormalMaterial.defaultAttributeValues={...aoNormalMaterial.defaultAttributeValues,pondSwayWeight:[0,0]};decorate(aoNormalMaterial,time);
 return {meshes,vertices,maxDisplacement:POND_SWAY_PADDING,rootFixedBelow:-1.05};
}
