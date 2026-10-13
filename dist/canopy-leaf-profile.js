// Unit leaf surface in the albedo's XY plane; Y=-.5 anchors the petiole.
export function canopyLeafSurface(x,y){
 const t=y+.5,rib=Math.exp(-28*x*x),s=Math.sin(Math.PI*t),c=Math.cos(Math.PI*t);
 return {height:.192*x*x*t+.028*t*t+.026*rib*s+.020*x*t,
  dx:.384*x*t-1.456*x*rib*s+.020*t,
  dy:.192*x*x+.056*t+.026*rib*Math.PI*c+.020*x};
}
export function canopyLeafProfile(){
 const position=[],normal=[],uv=[],index=[];
 for(let j=0;j<3;j++)for(let i=0;i<3;i++){
  const x=i*.5-.5,y=j*.5-.5,p=canopyLeafSurface(x,y),length=Math.hypot(p.dx,p.dy,1);
  position.push(x,y,p.height);normal.push(-p.dx/length,-p.dy/length,1/length);uv.push(x+.5,y+.5);
 }
 // Diagonals run towards the midrib, allowing both wings to curl independently.
 for(let j=0;j<2;j++)for(let i=0;i<2;i++){
  const a=j*3+i,b=a+1,c=a+3,d=c+1;
  if(i===0)index.push(a,b,d,a,d,c);else index.push(a,b,c,b,d,c);
 }
 return {position,normal,uv,index};
}
