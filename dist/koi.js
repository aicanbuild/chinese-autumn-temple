import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {sampleKoiMotion} from './koi-motion.js';
import {applyKoiReaction} from './koi-reaction.js';

// Geometry and four original skin variations come from the editable Blender asset.
export function createKoi(root,scene,random){
 const variants=[];root.updateMatrixWorld(true);
 for(const name of ['kohaku','sanke','yamabuki','platinum']){
  const source=root.getObjectByName(`Koi_${name}`),batches=new Map();
  if(!source)throw new Error(`Missing Blender koi variant: ${name}`);
  source.traverse(o=>{
   if(!o.isMesh)return;
   const key=o.material.name+(o.name.includes('Pectoral')?' pectoral':'');
   if(!batches.has(key))batches.set(key,{geometries:[],material:o.material,pectoral:o.name.includes('Pectoral')});
   batches.get(key).geometries.push(o.geometry.clone().applyMatrix4(o.matrixWorld));
  });
  const prototype=new THREE.Group();prototype.name=`Detailed ${name} koi`;
  for(const [name,b]of batches){
   // Exported parts differ in UV presence; the common layout keeps batching deterministic.
   for(const g of b.geometries){
    for(const key of Object.keys(g.attributes))if(!['position','normal','uv'].includes(key))g.deleteAttribute(key);
    if(!g.attributes.uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count*2),2));
   }
   const mesh=new THREE.Mesh(mergeGeometries(b.geometries),b.material);mesh.name=name;mesh.userData.pectoral=b.pectoral;prototype.add(mesh);
   b.geometries.forEach(g=>g.dispose());
  }
  variants.push(prototype);
 }
 const fish=[],time={value:0},batches=[];
 // Four fish of each skin share draw calls; vertex count and individual motion stay intact.
 for(let kind=0;kind<4;kind++){
  const meshes=[];
  const motion=new THREE.InstancedBufferAttribute(new Float32Array(16),4);motion.setUsage(THREE.DynamicDrawUsage);
  variants[kind].traverse(o=>{
   if(!o.isMesh)return;
   const geometry=o.geometry.clone();
   geometry.setAttribute('koiMotion',motion);
   const material=o.material.clone();material.envMapIntensity=.28;
   if(material.map)material.map.anisotropy=8;
   if(material.normalMap)material.normalScale.setScalar(material.name.includes('fin')?.65:1);
   const membrane=material.name.includes('fin');
   const mesh=new THREE.InstancedMesh(geometry,material,4);mesh.name=o.name+' instanced';
   mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;mesh.userData.waterSide='below';
   mesh.castShadow=!membrane;mesh.receiveShadow=true;
   if(membrane){material.side=THREE.DoubleSide;material.depthWrite=false;material.alphaTest=.05;material.forceSinglePass=true;}
   const deform=shader=>{
    shader.vertexShader=`attribute vec4 koiMotion;
      float koiBend(float z){float w=clamp((.40-z)/1.40,0.,1.);return (sin(koiMotion.x+z*5.3)*koiMotion.y+koiMotion.z)*w*w;}
      ${shader.vertexShader}`;
    shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>',`#include <beginnormal_vertex>
      float bendDerivative=(koiBend(position.z+.006)-koiBend(position.z-.006))/.012;
      ${o.userData.pectoral?'float finDerivative=sin(koiMotion.w)*2.0*sign(position.x)*max(abs(position.x)-.115,0.0)/.0625*.035;objectNormal.x-=finDerivative*objectNormal.y;':''}
      objectNormal.z-=bendDerivative*objectNormal.x;`);
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
      transformed.x+=koiBend(position.z);
      ${o.userData.pectoral?'transformed.y+=sin(koiMotion.w)*pow(max(abs(position.x)-.115,0.0)/.25,2.0)*.035;':''}`);
   };
   material.onBeforeCompile=deform;material.customProgramCacheKey=()=>o.userData.pectoral?'koi-pectoral-instanced-v3':'koi-body-instanced-v3';
   if(mesh.castShadow){mesh.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});mesh.customDepthMaterial.onBeforeCompile=deform;}
   scene.add(mesh);meshes.push(mesh);
  });
  batches.push(meshes);
 }
 for(let i=0;i<16;i++){
  const group=new THREE.Object3D();group.scale.setScalar(.70+random()*.35);
  fish.push({group,time,meshes:batches[i%4],index:Math.floor(i/4),schoolIndex:i,phase:i/16*Math.PI*2,tailOffset:i*1.73,speed:.055+random()*.035,rx:3.2+random()*4.9,rz:2.2+random()*2.3,depth:-.33-random()*.25,drift:random()*6.28});
 }
 updateKoi(fish,0);
 return fish;
}
export function updateKoi(fish,t){
 for(const f of fish){
  const m=applyKoiReaction(f,sampleKoiMotion(f,t,f.motion??(f.motion={})),t);
  f.group.position.set(m.x,m.y,m.z);
  f.group.rotation.set(m.pitch,m.yaw,m.roll,'YXZ');
  f.time.value=t;
  if(f.meshes){
   const attribute=f.meshes[0].geometry.attributes.koiMotion;
   attribute.setXYZW(f.index,m.tailPhase%(Math.PI*2),m.tailAmplitude,m.turnBend,m.finPhase%(Math.PI*2));attribute.needsUpdate=true;
   f.group.updateMatrix();for(const mesh of f.meshes){mesh.setMatrixAt(f.index,f.group.matrix);mesh.instanceMatrix.needsUpdate=true;}
  }
 }
}
