import * as THREE from 'three';

// Atlas baked from the fixed native stone/pier placement. A separate UV set
// preserves the photographic sediment's original texture pitch and normals.
export function installPondContact(root,map,{intensity=.85}={}){
 let bed;root.traverse(o=>{if(o.isMesh&&o.material?.name==='Riverbed sediment')bed=o;});
 if(!bed)throw new Error('Missing sediment for baked pond contact');
 if(bed.material.aoMap)throw new Error('Sediment already has an occlusion map');
 bed.updateWorldMatrix(true,false);
 const positions=bed.geometry.attributes.position,uv=new Float32Array(positions.count*2),p=new THREE.Vector3();
 for(let i=0;i<positions.count;i++){
  p.fromBufferAttribute(positions,i).applyMatrix4(bed.matrixWorld);
  uv[i*2]=(p.x+11.5)/23;uv[i*2+1]=(12.7-p.z)/13.8;
 }
 bed.geometry.setAttribute('uv1',new THREE.BufferAttribute(uv,2));
 map.channel=1;map.colorSpace=THREE.NoColorSpace;map.flipY=true;
 map.wrapS=map.wrapT=THREE.ClampToEdgeWrapping;map.anisotropy=8;map.needsUpdate=true;
 bed.material=bed.material.clone();bed.material.aoMap=map;bed.material.aoMapIntensity=intensity;bed.material.needsUpdate=true;
 return {bed,stats:{width:map.image.width,height:map.image.height,distance:.45,intensity,uvChannel:1}};
}
