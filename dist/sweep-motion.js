import * as THREE from 'three';

const rotationMatrix=new THREE.Matrix4();
// Resolve the complete footprint against the same stepped ground used for walking.
// A curled edge or tilted bristle can touch a higher board before its origin does.
export function supportHeight(positions,rotation,size,x,z,surfaceAt,clearance=.002){
 rotationMatrix.makeRotationFromEuler(rotation);const e=rotationMatrix.elements;let height=-Infinity;
 for(let i=0;i<positions.count;i++){
  const px=positions.getX(i)*size,py=positions.getY(i)*size,pz=positions.getZ(i)*size;
  const dx=e[0]*px+e[4]*py+e[8]*pz,dy=e[1]*px+e[5]*py+e[9]*pz,dz=e[2]*px+e[6]*py+e[10]*pz;
  const ground=surfaceAt(x+dx,z+dz);
  height=Math.max(height,ground+clearance-dy);
 }
 return height;
}

export function collectSupportVertices(root){
 root.updateMatrixWorld(true);const inverse=new THREE.Matrix4().copy(root.matrixWorld).invert(),matrix=new THREE.Matrix4(),point=new THREE.Vector3(),vertices=[];
 root.traverse(mesh=>{
  if(!mesh.isMesh)return;
  matrix.multiplyMatrices(inverse,mesh.matrixWorld);const p=mesh.geometry.attributes.position;
  for(let i=0;i<p.count;i++){point.fromBufferAttribute(p,i).applyMatrix4(matrix);vertices.push(point.x,point.y,point.z);}
 });
 return new THREE.Float32BufferAttribute(vertices,3);
}

export function advanceSweptLeaf(leaf,dt){
 const drag=Math.exp(-1.2*dt),travel=-Math.expm1(-1.2*dt)/1.2;
 leaf.x+=leaf.vx*travel;leaf.z+=leaf.vz*travel;
 leaf.y+=leaf.vy*dt-.75*dt*dt;leaf.vy-=1.5*dt;
 leaf.vx*=drag;leaf.vz*=drag;leaf.life+=dt;
}
