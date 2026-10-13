import * as THREE from 'three';

// Spatial batches let the renderer cull groves outside the camera and shadow views.
export function createLandscape(terrain,woodland,layout,scene){
 const wind={value:0},transform=new THREE.Object3D(),batches=[];
 terrain.name='Blender sculpted forest terrain';
 terrain.traverse(o=>{if(o.isMesh){o.receiveShadow=true;o.userData.waterClipStatic=true;o.material.roughness=.94;o.material.envMapIntensity=.35;for(const key of ['map','normalMap'])if(o.material[key])o.material[key].anisotropy=8;}});
 scene.add(terrain);woodland.updateMatrixWorld(true);
 for(let species=0;species<3;species++)for(let lod=0;lod<2;lod++){
  const root=woodland.getObjectByName(`Woodland_${species}_${lod}`);
  if(!root)throw new Error(`Missing woodland prototype ${species}/${lod}`);
  const trees=layout.trees.filter(p=>p[5]===species&&p[6]===lod);
  const groves=new Map();for(const p of trees){const key=`${Math.floor(p[0]/40)},${Math.floor(p[1]/40)}`;if(!groves.has(key))groves.set(key,[]);groves.get(key).push(p);}
  for(const positions of groves.values()){
  root.traverse(part=>{
   if(!part.isMesh||!positions.length)return;
   const geometry=part.geometry.clone().applyMatrix4(part.matrixWorld),material=part.material.clone();
   const leaves=part.name.startsWith('Leaves_');
   material.envMapIntensity=.35;material.roughness=.91;
   for(const key of ['map','normalMap'])if(material[key])material[key].anisotropy=8;
   if(leaves){
    material.transparent=false;material.depthWrite=true;material.alphaTest=.42;material.side=THREE.DoubleSide;material.forceSinglePass=true;
    material.onBeforeCompile=shader=>{
     shader.uniforms.uWoodlandTime=wind;shader.vertexShader='uniform float uWoodlandTime;\n'+shader.vertexShader;
     shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
      #ifdef USE_INSTANCING
      vec3 root=instanceMatrix[3].xyz;
      float gust=sin(uWoodlandTime*.48+root.x*.21+root.z*.19);
      transformed.x+=gust*.035*max(0.,position.y-2.);
      transformed.z+=sin(uWoodlandTime*.73+position.x*1.7+root.z)*.045;
      #endif`);
    };
   }
   const mesh=new THREE.InstancedMesh(geometry,material,positions.length);mesh.name=`Woodland ${species}/${lod} ${leaves?'leaves':'branches'}`;
   positions.forEach(([x,y,z,scale,rotation],i)=>{transform.position.set(x,z,-y);transform.rotation.set(0,rotation,0);transform.scale.setScalar(scale);transform.updateMatrix();mesh.setMatrixAt(i,transform.matrix);});
   mesh.castShadow=positions.some(p=>Math.hypot(p[0],p[1])<38);mesh.receiveShadow=true;if(!leaves)mesh.userData.waterMotionPadding=.005;mesh.computeBoundingBox();mesh.computeBoundingSphere();scene.add(mesh);batches.push(mesh);
  });
  }
 }
 return {trees:layout.trees.length,batches,update(time){wind.value=time;}};
}
