import * as THREE from 'three';

// Fixed furniture/wall visibility above the authored stone floor. Separate UVs
// preserve each slab's independently rotated stone color/normal/roughness maps.
export function installHallContact(root,map,{intensity=.8}={}){
 const meshes=[];root.traverse(o=>{if(o.isMesh&&o.material?.name.startsWith('Sanctuary floor | '))meshes.push(o);});
 if(meshes.length!==3)throw new Error('Missing three sanctuary floor materials for baked contact');
 if(meshes.some(o=>o.material.aoMap||o.geometry.attributes.uv1))throw new Error('Sanctuary floor already has an occlusion map or secondary UVs');
 root.updateWorldMatrix(true,true);
 const point=new THREE.Vector3();
 for(const mesh of meshes){
  const position=mesh.geometry.attributes.position,uv=new Float32Array(position.count*2);
  for(let i=0;i<position.count;i++){
   point.fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);
   uv[i*2]=(point.x+6.1275)/12.245;uv[i*2+1]=(-point.z-3.475)/7.25;
  }
  mesh.geometry.setAttribute('uv1',new THREE.BufferAttribute(uv,2));
  mesh.material=mesh.material.clone();mesh.material.aoMap=map;mesh.material.aoMapIntensity=intensity;mesh.material.needsUpdate=true;
 }
 map.channel=1;map.colorSpace=THREE.NoColorSpace;map.flipY=true;map.wrapS=map.wrapT=THREE.ClampToEdgeWrapping;map.anisotropy=8;map.needsUpdate=true;
 return {meshes,stats:{width:map.image.width,height:map.image.height,distance:1,intensity,materials:meshes.length,uvChannel:1}};
}
