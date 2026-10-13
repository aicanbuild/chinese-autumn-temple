import * as THREE from 'three';

// Paint uses UV0 and metre-scale plaster uses UV1. The independent third set
// follows the measured, inward-facing wall receivers, including both side walls.
export function installMuralContact(root,map,layout,{intensity=.85}={}){
 const meshes=[];root.traverse(o=>{if(o.isMesh&&o.material?.name.includes('mural'))meshes.push(o);});
 if(meshes.length!==2||layout.panels?.length!==4)throw new Error('Missing paired mural materials or four contact panels');
 if(meshes.some(o=>o.material.aoMap||o.geometry.attributes.uv2))throw new Error('Mural contact UV or material already occupied');
 root.updateWorldMatrix(true,true);
 const world=new THREE.Vector3(),native=new THREE.Vector3(),delta=new THREE.Vector3(),counts=[0,0,0,0];
 const panels=layout.panels.map(p=>({...p,center:new THREE.Vector3(...p.center),u:new THREE.Vector3(...p.u),v:new THREE.Vector3(...p.v),normal:new THREE.Vector3(...p.normal)}));
 const prepared=meshes.map(mesh=>{
  const position=mesh.geometry.attributes.position,uv=new Float32Array(position.count*2);
  for(let i=0;i<position.count;i++){
   world.fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);native.set(world.x,-world.z,world.y);
   let found=false;
   for(let k=0;k<panels.length;k++){
    const p=panels[k];delta.copy(native).sub(p.center);const u=delta.dot(p.u)/p.size[0]+.5,v=delta.dot(p.v)/p.size[1]+.5;
    if(Math.abs(delta.dot(p.normal))>.005||u<-.001||u>1.001||v<-.001||v>1.001)continue;
    const [x0,y0,x1,y1]=p.atlas;uv[i*2]=x0+THREE.MathUtils.clamp(u,0,1)*(x1-x0);uv[i*2+1]=y0+THREE.MathUtils.clamp(v,0,1)*(y1-y0);counts[k]++;found=true;break;
   }
   if(!found)throw new Error('Mural geometry no longer matches its baked wall plane');
  }
  return {mesh,uv};
 });
 if(counts.some(n=>n<3))throw new Error('Mural contact is missing a wall panel');
 for(const {mesh,uv} of prepared){mesh.geometry.setAttribute('uv2',new THREE.BufferAttribute(uv,2));mesh.material=mesh.material.clone();mesh.material.aoMap=map;mesh.material.aoMapIntensity=intensity;mesh.material.needsUpdate=true;}
 map.channel=2;map.colorSpace=THREE.NoColorSpace;map.flipY=true;map.wrapS=map.wrapT=THREE.ClampToEdgeWrapping;map.anisotropy=8;map.needsUpdate=true;
 return {meshes,stats:{width:map.image.width,height:map.image.height,distance:layout.distance,intensity,materials:meshes.length,panels:counts.length,verticesPerPanel:counts,uvChannel:2}};
}
