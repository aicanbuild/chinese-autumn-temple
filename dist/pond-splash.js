import * as THREE from 'three';

// Only the few airborne drops need separate geometry. The depression, rebound
// and spreading wave train belong to the pond's own displaced water surface.
export function createPondSplash(scene,isWet){
 const capacity=96,drops=Array.from({length:96},()=>({age:99})),dummy=new THREE.Object3D();
 let next=0,total=0,awake=0,active=0;
 const material=new THREE.MeshPhysicalMaterial({color:'#c5dbd4',roughness:.035,metalness:0,clearcoat:1,ior:1.333,transparent:true,opacity:.24,depthWrite:false,envMapIntensity:1.1});
 const mesh=new THREE.InstancedMesh(new THREE.SphereGeometry(1,12,8),material,capacity);
 mesh.name='Fine airborne pond droplets';mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;mesh.visible=false;mesh.userData.noAO=true;mesh.userData.waterSide='above';mesh.userData.waterMotionPadding=.5;scene.add(mesh);
 for(let i=0;i<capacity;i++){dummy.scale.setScalar(0);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);}
 function splash(x,z){
  total++;awake=.7;
  for(let i=0;i<12;i++){
   const a=Math.random()*Math.PI*2,s=.22+Math.random()*.55;
   drops[next]={x,z,vx:Math.cos(a)*s,vz:Math.sin(a)*s,vy:.65+Math.random()*1.05,size:.005+Math.random()*.006,age:0};next=(next+1)%capacity;
  }
 }
 function update(dt){
  if(awake<=0)return;awake-=dt;active=0;
  for(let i=0;i<capacity;i++){
   const d=drops[i];d.age+=dt;const a=d.age,y=-.012+d.vy*a-4.9*a*a;
   if(a<.65&&y>-.025&&isWet(d.x+d.vx*a,d.z+d.vz*a)){
    dummy.position.set(d.x+d.vx*a,y,d.z+d.vz*a);
    dummy.scale.set(d.size,d.size*(1+.18*Math.abs(d.vy-9.8*a)),d.size);active++;
   }else dummy.scale.setScalar(0);
   dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);
  }
  mesh.visible=active>0;mesh.instanceMatrix.needsUpdate=true;
 }
 return {splash,update,get stats(){return {clicks:total,active};}};
}
