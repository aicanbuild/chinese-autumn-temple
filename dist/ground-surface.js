import * as THREE from 'three';

// Exact triangle interpolation, accelerated by a small spatial grid. This is
// built once from static ground meshes; runtime samples allocate no vectors.
export function createGroundSurface(sources,{min=-17,max=17,cellSize=1}={}){
 const width=Math.ceil((max-min)/cellSize),cells=Array.from({length:width*width},()=>[]),triangles=[];
 const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
 for(const {root,include=()=>true,maxHeight=Infinity} of sources){
  root.updateMatrixWorld(true);
  root.traverse(mesh=>{
   if(!mesh.isMesh||!include(mesh))return;
   const p=mesh.geometry.attributes.position,index=mesh.geometry.index;
   for(let i=0;i<(index?.count??p.count);i+=3){
    a.fromBufferAttribute(p,index?index.getX(i):i).applyMatrix4(mesh.matrixWorld);b.fromBufferAttribute(p,index?index.getX(i+1):i+1).applyMatrix4(mesh.matrixWorld);c.fromBufferAttribute(p,index?index.getX(i+2):i+2).applyMatrix4(mesh.matrixWorld);
    const x0=Math.min(a.x,b.x,c.x),x1=Math.max(a.x,b.x,c.x),z0=Math.min(a.z,b.z,c.z),z1=Math.max(a.z,b.z,c.z);
    if(x1<min||x0>=max||z1<min||z0>=max||Math.max(a.y,b.y,c.y)>maxHeight)continue;
    const bx=b.x-a.x,bz=b.z-a.z,by=b.y-a.y,cx=c.x-a.x,cz=c.z-a.z,cy=c.y-a.y,det=bx*cz-bz*cx;
    const nx=by*cz-bz*cy,ny=bz*cx-bx*cz,nz=bx*cy-by*cx;
    if(ny<=.35*Math.hypot(nx,ny,nz)||Math.abs(det)<1e-10)continue;
    const id=triangles.length;triangles.push([a.x,a.z,a.y,bx,bz,by,cx,cz,cy,1/det]);
    for(let x=Math.max(0,Math.floor((x0-min)/cellSize));x<=Math.min(width-1,Math.floor((x1-min)/cellSize));x++)for(let z=Math.max(0,Math.floor((z0-min)/cellSize));z<=Math.min(width-1,Math.floor((z1-min)/cellSize));z++)cells[z*width+x].push(id);
   }
  });
 }
 function heightAt(x,z){
  if(x<min||x>=max||z<min||z>=max)return null;
  const ids=cells[Math.floor((z-min)/cellSize)*width+Math.floor((x-min)/cellSize)];let height=-Infinity;
  for(const id of ids){const t=triangles[id],dx=x-t[0],dz=z-t[1],u=(dx*t[7]-dz*t[6])*t[9],v=(t[3]*dz-t[4]*dx)*t[9];if(u>=-1e-8&&v>=-1e-8&&u+v<=1+1e-8)height=Math.max(height,t[2]+u*t[5]+v*t[8]);}
  return Number.isFinite(height)?height:null;
 }
 return {heightAt,stats:{triangles:triangles.length,cells:cells.length,maxCellTriangles:Math.max(...cells.map(c=>c.length))}};
}
