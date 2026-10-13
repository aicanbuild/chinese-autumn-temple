import fs from 'node:fs';
import * as T from '../dist/vendor/three/three.module.js';
import {sampleKoiMotion} from '../dist/koi-motion.js';
const bytes=fs.readFileSync(new URL('../dist/assets/koi/koi.glb',import.meta.url));
const d=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12))),parts=[];
function visit(i,parent=new T.Matrix4()){
 const n=d.nodes[i],m=new T.Matrix4();
 if(n.matrix)m.fromArray(n.matrix);else m.compose(new T.Vector3().fromArray(n.translation??[0,0,0]),new T.Quaternion().fromArray(n.rotation??[0,0,0,1]),new T.Vector3().fromArray(n.scale??[1,1,1]));m.premultiply(parent);
 if(n.mesh!==undefined)for(const p of d.meshes[n.mesh].primitives){const a=d.accessors[p.attributes.POSITION];parts.push(new T.Box3(new T.Vector3().fromArray(a.min),new T.Vector3().fromArray(a.max)).applyMatrix4(m));}
 for(const child of n.children??[])visit(child,m);
}
for(const i of d.scenes[0].nodes)visit(i);
const rest=[...new Map(parts.map(b=>[JSON.stringify(b),b])).values()];
const pose=new T.Object3D();
export const reference=JSON.parse(fs.readFileSync(new URL('./koi-flock-reference.json',import.meta.url))).map((f,i)=>({...f,schoolIndex:i,tailOffset:i*1.73,group:{scale:{x:f.scale}}}));
function envelopes(f,t){
 const m=sampleKoiMotion(f,t);pose.position.set(m.x,m.y,m.z);pose.rotation.set(m.pitch,m.yaw,m.roll,'YXZ');pose.scale.setScalar(f.group.scale.x);pose.updateMatrix();
 return rest.map(r=>{
 const b=r.clone(),bend=(m.tailAmplitude+Math.abs(m.turnBend))*T.MathUtils.clamp((.40-r.min.z)/1.4,0,1)**2;
 const flap=(Math.max(0,Math.max(Math.abs(r.min.x),Math.abs(r.max.x))-.115)/.25)**2*.035;
 b.min.x-=bend;b.max.x+=bend;b.min.y-=flap;b.max.y+=flap;
 const center=b.getCenter(new T.Vector3()).applyMatrix4(pose.matrix),half=b.getSize(new T.Vector3()).multiplyScalar(f.group.scale.x*.5);
 const axes=[new T.Vector3(1,0,0),new T.Vector3(0,1,0),new T.Vector3(0,0,1)].map(v=>v.applyEuler(pose.rotation));
 b.applyMatrix4(pose.matrix);b.obb={center,half:half.toArray(),axes};return b;
 });
}
// Separate per-part world AABBs are conservative even under animated deformation.
// A positive value on any axis proves the entire pair of boxes is separated.
function separation(a,b){return Math.max(b.min.x-a.max.x,a.min.x-b.max.x,b.min.y-a.max.y,a.min.y-b.max.y,b.min.z-a.max.z,a.min.z-b.max.z);}
function orientedSeparation(a,b){
 let gap=separation(a,b);if(gap>0)return gap;
 const A=a.obb,B=b.obb,delta=B.center.clone().sub(A.center),axes=[...A.axes,...B.axes];
 for(const x of A.axes)for(const y of B.axes){const v=new T.Vector3().crossVectors(x,y);if(v.lengthSq()>1e-12)axes.push(v.normalize());}
 for(const axis of axes){let r=0;for(let k=0;k<3;k++)r+=A.half[k]*Math.abs(axis.dot(A.axes[k]))+B.half[k]*Math.abs(axis.dot(B.axes[k]));gap=Math.max(gap,Math.abs(delta.dot(axis))-r);}
 return gap;
}
export function auditSchool(fish=reference,{duration=1800,step=.2}={}){
 let pair=Infinity,pier=Infinity,bed=Infinity,closest=null,samples=0;
 for(let t=0;t<duration;t+=step){
  const all=fish.map(f=>envelopes(f,t)),unions=all.map(parts=>parts.reduce((a,b)=>a.union(b),new T.Box3()));samples++;
  for(let i=0;i<fish.length;i++){
   for(let j=i+1;j<fish.length;j++){
    const broad=separation(unions[i],unions[j]);if(broad>pair)continue;
    let gap=Infinity;for(const a of all[i])for(const b of all[j])gap=Math.min(gap,orientedSeparation(a,b));
    if(gap<pair){pair=gap;closest={t,i,j};}
   }
   for(const b of all[i]){
    for(const x of [-1.04,1.04])for(let k=0;k<5;k++){
     const z=1.4+k*2.6,dx=Math.max(b.min.x-x-.105,x-.105-b.max.x,0),dz=Math.max(b.min.z-z-.105,z-.105-b.max.z,0);pier=Math.min(pier,Math.hypot(dx,dz));
    }
    let radius=0;for(const x of [b.min.x,b.max.x])for(const z of [b.min.z,b.max.z])radius=Math.max(radius,Math.hypot(x/11.5,(z-5.8)/6.9)/.985);
    const u=T.MathUtils.clamp((radius-.28)/.72,0,1),top=-.98-.58*(1-u*u*(3-2*u))+.024;bed=Math.min(bed,b.min.y-top);
   }
  }
 }
 return {samples,partBounds:rest.length,pair,pier,bed,closest};
}
if(process.argv[1]?.endsWith('koi-school-audit.mjs'))console.log(JSON.stringify(auditSchool(),null,2));
