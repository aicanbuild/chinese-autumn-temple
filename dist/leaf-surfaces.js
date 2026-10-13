import {applyCanopyWind} from './foliage-wind.js';
import * as THREE from 'three';
import {canopyLeafProfile} from './canopy-leaf-profile.js';

export function createFallenLeafGeometry(kind=0,variant=0){
 // Boundaries follow the botanical albedo silhouette; empty card corners cannot
 // become invisible support points when a leaf rocks against the ground.
 let outline;
 if(kind===0)outline=[[507,957],[476,737],[78,635],[281,582],[103,333],[337,465],[282,89],[430,354],[514,33],[603,370],[768,129],[713,478],[958,367],[794,595],[935,689],[550,743],[524,957]];
 else{
  outline=[[505,951],[497,758]];
  for(let i=0;i<=24;i++){const t=i/24,a=(204+132*t)*Math.PI/180,r=660-94*Math.exp(-(((t-.50)/.046)**2));outline.push([512+r*Math.cos(a)*.74,777+r*Math.sin(a)]);}
  outline.push([530,754],[523,952]);
 }
 const points=outline.map(([x,y])=>new THREE.Vector2(x/1024-.5,.5-y/1024));
 const faces=THREE.ShapeUtils.triangulateShape(points,[]),midpoints=new Map();
 function midpoint(a,b){const key=[Math.min(a,b),Math.max(a,b)].join(':');if(!midpoints.has(key)){midpoints.set(key,points.length);points.push(points[a].clone().add(points[b]).multiplyScalar(.5));}return midpoints.get(key);}
 const indices=[];for(const [a,b,c] of faces){const ab=midpoint(a,b),bc=midpoint(b,c),ca=midpoint(c,a);indices.push(a,ab,ca,ab,b,bc,ca,bc,c,ab,bc,ca);}
 function height(x,y){
  const rib=.016*Math.exp(-x*x*65)*(y+.6);
  const z=variant===0?.055*Math.abs(x*2)**1.6+.016*(y+.5)**2+rib:variant===1?.16*(x+.10)**2+.085*(y+.5)**3+.045*x*Math.sin(y*6)+rib:.11*(x*2)**2+.10*Math.max(0,y-.03)**2+.045*Math.sin(y*5+x*5)+rib;
  return z;
 }
 // Refine only edges whose linear chord misses the authored curl by >0.4 mm
 // at a 20 cm leaf size. Shared edge splits keep adjacent faces connected.
 const splits=new Map(),edgeKey=(a,b)=>[Math.min(a,b),Math.max(a,b)].join(':');
 for(let i=0;i<indices.length;i+=3)for(let k=0;k<3;k++){
  const a=indices[i+k],b=indices[i+(k+1)%3],key=edgeKey(a,b);if(splits.has(key))continue;
  const A=points[a],B=points[b],P=A.clone().add(B).multiplyScalar(.5);
  if(Math.abs(height(P.x,P.y)-(height(A.x,A.y)+height(B.x,B.y))*.5)>.002)splits.set(key,midpoint(a,b));
 }
 const refined=[];
 for(let i=0;i<indices.length;i+=3){
  const v=indices.slice(i,i+3),m=v.map((a,k)=>splits.get(edgeKey(a,v[(k+1)%3]))),count=m.filter(x=>x!==undefined).length;
  if(!count)refined.push(...v);
  else if(count===3){const [a,b,c]=v,[ab,bc,ca]=m;refined.push(a,ab,ca,ab,b,bc,ca,bc,c,ab,bc,ca);}
  else if(count===1){const k=m.findIndex(x=>x!==undefined),a=v[k],b=v[(k+1)%3],c=v[(k+2)%3];refined.push(a,m[k],c,m[k],b,c);}
  else{const k=v.findIndex((_,j)=>m[(j+2)%3]!==undefined&&m[j]!==undefined),a=v[(k+2)%3],b=v[k],c=v[(k+1)%3],ab=m[(k+2)%3],bc=m[k];refined.push(ab,b,bc,a,ab,c,ab,bc,c);}
 }
 const positions=[],uv=[],normals=[];let minimum=Infinity;
 for(const p of points){const x=p.x,y=p.y,z=height(x,y),eps=.0001;
  const normal=new THREE.Vector3(-(height(x+eps,y)-height(x-eps,y))/(2*eps),-(height(x,y+eps)-height(x,y-eps))/(2*eps),1).normalize();
  minimum=Math.min(minimum,z);positions.push(x,y,z);uv.push(x+.5,y+.5);normals.push(normal.x,normal.y,normal.z);
 }
 for(let i=2;i<positions.length;i+=3)positions[i]-=minimum;
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(refined);g.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));g.computeBoundingBox();g.computeBoundingSphere();g.userData.species=kind;g.userData.curlVariant=variant;return g;
}

export function createLeafGeometry(detailed=false){
 let geometry;
 if(detailed){
  return createFallenLeafGeometry();
 }else{
  const profile=canopyLeafProfile();
  geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(profile.position,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(profile.uv,2));
  geometry.setAttribute('normal',new THREE.Float32BufferAttribute(profile.normal,3));
  geometry.setIndex(profile.index);
 }
 geometry.computeBoundingBox();geometry.computeBoundingSphere();return geometry;
}

export function applyLeafSurface(material,{normal,surface,wind=null}){
 material.normalMap=normal;material.normalScale=new THREE.Vector2(.38,.38);
 material.roughnessMap=surface;material.roughness=1;material.forceSinglePass=true;
 material.onBeforeCompile=shader=>{
  shader.uniforms.uLeafSurface={value:surface};
  shader.vertexShader='varying vec2 vLeafUv;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <uv_vertex>','#include <uv_vertex>\nvLeafUv=uv;');
  shader.fragmentShader='varying vec2 vLeafUv;\nuniform sampler2D uLeafSurface;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <lights_physical_pars_fragment>',`#include <lights_physical_pars_fragment>
   void RE_Direct_Leaf(const in IncidentLight light,const in vec3 position,const in vec3 normal,const in vec3 viewDir,const in vec3 coatNormal,const in PhysicalMaterial material,inout ReflectedLight reflectedLight){
    RE_Direct_Physical(light,position,normal,viewDir,coatNormal,material,reflectedLight);
    float thinness=texture2D(uLeafSurface,vLeafUv).r;
    float backLight=pow(max(0.,dot(-normal,light.direction)),.7);
    // Incoming light already includes its shadow term. Dense veins transmit less.
    reflectedLight.directDiffuse+=light.color*material.diffuseColor*thinness*backLight*.24;
   }
   #undef RE_Direct
   #define RE_Direct RE_Direct_Leaf`);
  if(wind)applyCanopyWind(shader,wind);
 };
 material.customProgramCacheKey=()=>`botanical-leaf-1-${wind?'wind':'still'}`;
 material.needsUpdate=true;return material;
}
