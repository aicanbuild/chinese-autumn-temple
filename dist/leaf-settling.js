import * as THREE from 'three';

const supportMatrix=new THREE.Matrix4();
export function lowestLeafPoint(geometry,rotation,size){
 supportMatrix.makeRotationFromEuler(rotation);const e=supportMatrix.elements,p=geometry.attributes.position;let lowest=Infinity;
 for(let i=0;i<p.count;i++)lowest=Math.min(lowest,e[1]*p.getX(i)+e[5]*p.getY(i)+e[9]*p.getZ(i));
 return lowest*size;
}

export function setLeafRotation(leaf,time,out){
 if(leaf.state==='swept'){
  const age=leaf.life,fade=Math.exp(-2.5*age),turn=(1-Math.exp(-3*age))/3;
  return out.set(leaf.sweepPose[0]+Math.sin(age*7)*.32*fade,leaf.sweepPose[1]+Math.sin(age*6)*.2*fade,leaf.sweepPose[2]+leaf.sweepSpin*turn);
 }
 if(leaf.state!=='rest')return out.set(-Math.PI/2+Math.sin(leaf.tilt)*.7,Math.cos(leaf.tilt)*.4,leaf.rot);
 const age=Math.max(0,time-(leaf.landedAt??-Infinity)),t=Math.min(.8,age);
 const fade=age>=.8?0:Math.exp(-9*t)*Math.cos(t*16)*(1-(t/.8)**4);
 const tilt=leaf.contactTilt??0;
 // Start at the exact incoming pose, then let a light sheet wobble to rest.
 const turn=Number.isFinite(leaf.landedAt)?.47*(1-Math.exp(-12*t))/12:0;
 return out.set(-Math.PI/2+Math.sin(tilt)*.7*fade,Math.cos(tilt)*.4*fade,leaf.rot+turn);
}

export function leafInstanceColor(id,out=new THREE.Color()){
 const noise=n=>{const v=Math.sin((id+1)*n)*43758.5453;return v-Math.floor(v);};
 const shade=.74+.26*noise(12.9898);
 return out.setRGB(shade,shade*(.86+.14*noise(7.233)),shade*(.78+.22*noise(3.417)));
}
