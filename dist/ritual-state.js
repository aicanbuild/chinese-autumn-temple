// Durations use active viewing seconds. Fresh incense waits to be lit again.
export const BURN_SECONDS=180, REPLACE_SECONDS=3;
export class IncenseCycle {
 constructor(){this.phase='ready';this.time=0;this.completed=0;}
 light(){if(this.phase!=='ready')return false;this.phase='burning';this.time=0;return true;}
 update(dt){
  if(this.phase==='ready')return;
  this.time+=Math.max(0,dt);
  if(this.phase==='burning'&&this.time>=BURN_SECONDS){this.time-=BURN_SECONDS;this.phase='replacing';this.completed++;}
  if(this.phase==='replacing'&&this.time>=REPLACE_SECONDS){this.phase='ready';this.time=0;}
 }
 get remaining(){return this.phase==='burning'?Math.max(0,1-this.time/BURN_SECONDS):this.phase==='ready'?1:0;}
}
