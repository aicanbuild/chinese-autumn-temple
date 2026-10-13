import * as THREE from 'three';
import {POND_CURRENT} from './water-current.js';

export const RIPPLE_CAPACITY=12;
export const CLICK_RIPPLE_CAPACITY=8;
export const RIPPLE_LIFETIME=6.8;
const smooth=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);};

// The same height profile used by the GPU also carries floating leaves.
export function sampleImpactHeight(r,age,strength){
 if(age<=0||age>=RIPPLE_LIFETIME||strength<=0)return 0;
 const large=strength>.015,radius=.08+age*(large?1.4:.32),width=large?.28+.13*age:.065+.022*age;
 const band=r-radius;if(Math.abs(band)>width*4&&r>.55)return 0;
 const k=large?11.5:52,fade=(1-smooth(4.8,RIPPLE_LIFETIME,age))*Math.exp(-age*(large?.23:1.2));
 const amplitude=strength*fade*smooth(.035,.18,age)/Math.sqrt(1+radius*.85);
 const ring=amplitude*Math.exp(-band*band/(2*width*width))*Math.cos(k*band);
 const centre=large?strength*(-1.65*Math.exp(-r*r/.035-age*13)+.70*Math.exp(-r*r/.022-((age-.23)/.11)**2))*(1-Math.exp(-age*65)):0;
 return ring+centre;
}
export function createPondGeometry(){
 // A square-to-disc grid avoids the original long triangle fan: crests now
 // have actual height, while the perimeter still matches the authored ellipse.
 const g=new THREE.PlaneGeometry(2,2,192,112),p=g.attributes.position,uv=g.attributes.uv;
 for(let i=0;i<p.count;i++){const u=p.getX(i),v=p.getY(i),x=11.48*u*Math.sqrt(1-v*v*.5),y=6.88*v*Math.sqrt(1-u*u*.5);p.setXYZ(i,x,y,0);uv.setXY(i,x,y);}
 g.computeBoundingBox();g.computeBoundingSphere();return g;
}
export function createPondMotion(material,sun){
 const events=Array.from({length:RIPPLE_CAPACITY},()=>new THREE.Vector4(0,0,-100,0));let next=0,nextLeaf=CLICK_RIPPLE_CAPACITY,total=0;
 const target=new THREE.Vector3();
 const time={value:0},direction={value:new THREE.Vector3()},light={value:new THREE.Color()};
 material.uniforms.pondImpacts={value:events};material.uniforms.pondTime=time;material.uniforms.waterSunDirection=direction;material.uniforms.waterSunColor=light;
 function update(t){time.value=t;sun.getWorldPosition(direction.value);sun.target.getWorldPosition(target);direction.value.sub(target).normalize();let visible=true;for(let p=sun;p;p=p.parent)visible=visible&&p.visible;light.value.copy(sun.color).multiplyScalar(visible?Math.max(0,sun.intensity):0);}
 update(0);
 return {events,update,
  disturb(x,z,t){events[next].set(x,z,t,.075);next=(next+1)%CLICK_RIPPLE_CAPACITY;total++;},
  impact(x,z,t,size){events[nextLeaf].set(x,z,t,Math.min(.0045,.0025*(size/.15)**2));nextLeaf=CLICK_RIPPLE_CAPACITY+(nextLeaf-CLICK_RIPPLE_CAPACITY+1)%(RIPPLE_CAPACITY-CLICK_RIPPLE_CAPACITY);total++;},
  heightAt(x,z,t){const q=(x/11.48)**2+((z-5.8)/6.88)**2,mask=1-smooth(.90,1,q);if(!mask)return 0;let h=0;for(const e of events)if(t>e.z&&t<e.z+RIPPLE_LIFETIME)h+=sampleImpactHeight(Math.hypot(x-e.x,z-e.y),t-e.z,e.w);h*=mask;return h/Math.sqrt(1+(h/.14)**2);},get stats(){return {impacts:total,active:events.filter(e=>time.value>=e.z&&time.value<e.z+RIPPLE_LIFETIME).length};}};
}

// A calm, continuous current. Invalid trials slide along the bank or bridge,
// instead of letting a floating leaf travel through a solid board or onto land.
export function advanceFloatingLeaf(leaf,dt,time,surfaceAt){
 if(!(dt>0))return;
 const vx=POND_CURRENT.x+.018*Math.cos(leaf.z*.22+time*.025)+.008*Math.sin(leaf.id*.73);
 const vz=POND_CURRENT.z+.010*Math.sin(leaf.x*.27-time*.021)+.006*Math.cos(leaf.id*.47);
 const x=leaf.x+vx*dt,z=leaf.z+vz*dt;
 const wet=(x,z)=>surfaceAt(x,z)<0&&(x/11.5)**2+((z-5.8)/6.9)**2<.97;
 if(wet(x,z)){leaf.x=x;leaf.z=z;}
 else if(wet(x,leaf.z))leaf.x=x;
 else if(wet(leaf.x,z))leaf.z=z;
 leaf.rot+=dt*.022*Math.sin(time*.13+leaf.id);
}

// Height and its analytic spatial derivative drive the mesh, refraction,
// reflected scenery and sunlight together. No coloured rings are composited.
export function pondImpactGLSL(){return `
 uniform vec4 pondImpacts[${RIPPLE_CAPACITY}];
 uniform float pondTime;
 vec3 pondImpactField(vec2 p){
  vec2 q=(p-vec2(0.,5.8))/vec2(11.48,6.88);
  float shore=1.-smoothstep(.90,1.,dot(q,q));
  if(shore<=0.)return vec3(0.);
  vec3 field=vec3(0.);
  for(int i=0;i<${RIPPLE_CAPACITY};i++){
   vec4 event=pondImpacts[i];float age=pondTime-event.z;
   if(age<=0.||age>=${RIPPLE_LIFETIME.toFixed(1)}||event.w<=0.)continue;
   bool large=event.w>.015;
   vec2 delta=p-event.xy;float r=length(delta),radius=.08+age*(large?1.4:.32);
   float width=large?.28+.13*age:.065+.022*age,band=r-radius;
   if(abs(band)>width*4.&&r>.55)continue;
   float k=large?11.5:52.;
   float fade=(1.-smoothstep(4.8,${RIPPLE_LIFETIME.toFixed(1)},age))*exp(-age*(large?.23:1.2));
   float amplitude=event.w*fade*smoothstep(.035,.18,age)/sqrt(1.+radius*.85);
   float envelope=amplitude*exp(-band*band/(2.*width*width));
   float h=envelope*cos(k*band);
   float derivative=envelope*(-band/(width*width)*cos(k*band)-k*sin(k*band));
   if(large){
    float rise=1.-exp(-age*65.);
    float depression=-1.65*event.w*exp(-r*r/.035-age*13.)*rise;
    float rebound=.70*event.w*exp(-r*r/.022-pow((age-.23)/.11,2.))*rise;
    h+=depression+rebound;derivative+=depression*(-2.*r/.035)+rebound*(-2.*r/.022);
   }
   field+=vec3(h,delta/max(r,.0001)*derivative);
  }
  field*=shore;float compression=sqrt(1.+pow(field.x/.14,2.));
  return vec3(field.x/compression,field.yz/(compression*compression*compression));
 }`;}
export function impactWaterVertex(base){
 return base.replace('#include <common>','#include <common>\n'+pondImpactGLSL())
  .replace('vToEye = cameraPosition - worldPosition.xyz;',`worldPosition.y+=pondImpactField(worldPosition.xz).x;
   vToEye = cameraPosition - worldPosition.xyz;`);
}
export function impactWaterFragment(base){
 return base.replace('#include <common>','#include <common>\n'+pondImpactGLSL()+'\nuniform vec3 waterSunDirection,waterSunColor;')
  .replace('// calculate the fresnel term',`vec3 impactField=pondImpactField((cameraPosition-vToEye).xz);
   normal=normalize(normal-vec3(impactField.y,0.,impactField.z));
   // calculate the fresnel term`);
}
