const pillars=Array.from({length:5},(_,i)=>1.4+2.6*i);
export function safeKoiPoint(x,z){
 if((x/10.72)**2+((z-5.8)/6.1)**2>=1)return false;
 return !pillars.some(p=>Math.abs(z-p)<.40&&Math.abs(Math.abs(x)-1.04)<.43);
}
export function scareKoi(fish,x,z,t){
 let count=0;
 for(const f of fish){const p=f.group.position,d=Math.hypot(p.x-x,p.z-z);if(d>4.4)continue;
  const a=Math.atan2(p.z-z,p.x-x)+((f.schoolIndex??0)%3-1)*.12;
  const old=f.escape;
  const yaw=f.motion?.yaw??0,speed=f.motion?.speed??.25;
  f.escape={x:p.x,z:p.z,vx:old?.vx??Math.sin(yaw)*speed,vz:old?.vz??Math.cos(yaw)*speed,awayX:Math.cos(a),awayZ:Math.sin(a),start:t,last:t,until:t+2.6};count++;
 }return count;
}
export function applyKoiReaction(f,m,t){
 const e=f.escape;if(!e)return m;
 let dt=Math.max(0,Math.min(.25,t-e.last));e.last=t;
 const fleeing=t<e.until,speed=fleeing?1.85:1.1;
 const tx=fleeing?e.awayX:m.x-e.x,tz=fleeing?e.awayZ:m.z-e.z,len=Math.hypot(tx,tz)||1;
 const wantX=tx/len*speed,wantZ=tz/len*speed;
 while(dt>1e-7){const step=Math.min(dt,.025),blend=1-Math.exp(-step*5);dt-=step;
  e.vx+=(wantX-e.vx)*blend;e.vz+=(wantZ-e.vz)*blend;
  const x=e.x+e.vx*step,z=e.z+e.vz*step;
  if(safeKoiPoint(x,z)){e.x=x;e.z=z;}
  else if(safeKoiPoint(x,e.z)){e.x=x;e.vz*=.55;}
  else if(safeKoiPoint(e.x,z)){e.z=z;e.vx*=.55;}
  else{e.vx*=.6;e.vz*=.6;}
 }
 if(!fleeing&&Math.hypot(e.x-m.x,e.z-m.z)<.09){f.escape=null;return m;}
 m.x=e.x;m.z=e.z;
 const v=Math.hypot(e.vx,e.vz);if(v>.04)m.yaw=Math.atan2(e.vx,e.vz);
 m.speed=v;m.tailPhase+=(t-e.start)*9;m.tailAmplitude=fleeing?.14:.08;m.finPhase+=(t-e.start)*5;
 return m;
}
