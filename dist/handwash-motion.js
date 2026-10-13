// Small, bounded state machine shared by mouse, touch and keyboard input.
export class HandwashMotion {
 constructor(){this.held=false;this.phase='rest';this.time=0;this.water=0;this.scoops=0;this.pours=0;}
 take(){if(this.held)return false;this.held=true;this.phase='stir';this.time=0;this.water=0;return true;}
 click(){if(!this.held)return false;if(this.phase==='stir'){this.phase='scoop';this.time=0;return true;}if(this.phase==='full'){this.phase='pour';this.time=0;return true;}return false;}
 putBack(){this.held=false;this.phase='rest';this.time=0;this.water=0;}
 update(dt){if(!this.held||!(dt>0))return;this.time+=Math.min(dt,.12);
  if(this.phase==='scoop'){this.water=Math.min(1,this.time/.32);if(this.time>=.85){this.phase='full';this.time=0;this.water=1;this.scoops++;}}
  else if(this.phase==='pour'){this.water=Math.max(0,1-Math.max(0,this.time-.16)/.70);if(this.time>=1.15){this.phase='stir';this.time=0;this.water=0;this.pours++;}}
 }
 get pose(){if(this.phase==='full')return {lift:.27,tilt:0};if(this.phase==='scoop'){const t=Math.max(0,Math.min(1,(this.time-.3)/.55));return {lift:-.065*Math.sin(Math.min(1,this.time/.30)*Math.PI)+.27*t*t*(3-2*t),tilt:0};}if(this.phase==='pour'){const t=this.time;return {lift:.27*(1-Math.max(0,(t-.90)/.25)),tilt:Math.sin(Math.min(1,t/1.1)*Math.PI)*1.5};}return {lift:0,tilt:0};}
}

// The +Z handle stays raised above both bamboo rails. Pour across the cup's
// +X side instead of bringing the handle through the front of the basin.
export function ladleTilt(){return -.35;}
export function ladleAngles(pourAmount){return {x:ladleTilt(),y:0,z:-.86*Math.max(0,Math.min(1.5,pourAmount))};}
export function constrainLadleTarget(x,z){
 z=Math.max(-.34,Math.min(-.16,z));const maxX=Math.sqrt(Math.max(0,.36*.36-z*z));
 return {x:Math.max(-maxX,Math.min(maxX,x)),z};
}
const ease=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);};
export function ladleTravel(from,to,t){
 const top=Math.max(from.y,to.y)+.33;
 if(t<.22)return {x:from.x,y:from.y+(top-from.y)*ease(t/.22),z:from.z};
 if(t<.76){const a=ease((t-.22)/.54);return {x:from.x+(to.x-from.x)*a,y:top,z:from.z+(to.z-from.z)*a};}
 return {x:to.x,y:top+(to.y-top)*ease((t-.76)/.24),z:to.z};
}
