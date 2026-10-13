// Fixed-anchor twin-rope pendulum. Sound fires once, when the timber reaches the boss.
export const BELL_IMPACT=.8;
export const BELL_CONTACT=Math.asin((.515-.725)/1.25);
const smooth=t=>t*t*(3-2*t);
export function bellAngle(age){
 if(age<0||age>=5)return 0;
 if(age<.35)return .25*smooth(age/.35);
 if(age<BELL_IMPACT)return .25+(BELL_CONTACT-.25)*smooth((age-.35)/.45);
 const t=age-BELL_IMPACT;return BELL_CONTACT*Math.exp(-2*t)*Math.cos(5.6*t)*(1-smooth(Math.min(1,t/4.2)));
}
export class BellStrike{
 constructor(sound){this.sound=sound;this.age=99;this.rings=0;this.sounded=true;}
 ring(){if(this.age<2.5)return false;this.age=0;this.sounded=false;this.rings++;return true;}
 update(dt){this.age+=Math.max(0,dt);if(!this.sounded&&this.age>=BELL_IMPACT){this.sounded=true;this.sound();}return bellAngle(this.age);}
}
