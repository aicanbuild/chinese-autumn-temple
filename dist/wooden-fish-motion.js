// One accepted click is one complete stroke. Holding never schedules repeats.
export const MUYU_IMPACT=.065, MUYU_DURATION=.23;
export class WoodenFishStrike {
 constructor(impact=()=>{}){this.impact=impact;this.held=false;this.pending=0;this.age=MUYU_DURATION;this.strikes=0;this.requests=0;}
 take(){if(this.held)return false;this.held=true;return true;}
 putBack(){this.held=false;this.pending=0;this.age=MUYU_DURATION;}
 click(){if(!this.held)return false;this.pending++;this.requests++;return true;}
 update(dt){
  if(!this.held)return 0;
  let remaining=Math.max(0,dt);
  while(remaining>0){
   if(this.age>=MUYU_DURATION){if(!this.pending)break;this.pending--;this.age=0;}
   const before=this.age,step=Math.min(remaining,MUYU_DURATION-this.age);this.age+=step;remaining-=step;
   if(before<MUYU_IMPACT&&this.age>=MUYU_IMPACT){this.strikes++;this.impact();}
  }
  if(this.age>=MUYU_DURATION)return 0;
  return this.age<MUYU_IMPACT?Math.pow(this.age/MUYU_IMPACT,2):Math.pow(1-(this.age-MUYU_IMPACT)/(MUYU_DURATION-MUYU_IMPACT),3);
 }
}
