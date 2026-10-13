import * as THREE from 'three';

// Static vegetation batches are stably ordered by their first relevant light.
// Each selected shadow camera draws through its last potentially visible instance.
// Prefixes can include extra instances; they never omit a required one. Color,
// water and other lights retain all instances and the authored wind materials.
export function createVegetationShadowInstances(meshes,lights,{reorder=true}={}){
 const views=lights.filter(l=>l.castShadow&&!l.isPointLight).map(light=>({light,camera:light.shadow.camera,view:new THREE.Matrix4(),frustum:new THREE.Frustum()})),lookup=new Map(views.map((v,i)=>[v.camera,i])),view=new THREE.Matrix4(),matrix=new THREE.Matrix4(),world=new THREE.Matrix4(),box=new THREE.Box3();
 const entries=[],stats={batches:0,instances:0,lightInstances:views.map(()=>0),savedTriangles:0,skippedInstances:0};let enabled=true;
 for(const mesh of meshes){
  if(!mesh.isInstancedMesh||!mesh.castShadow||mesh.morphTexture||(reorder&&Number.isInteger(mesh.userData.waterReflectionCount))||Object.values(mesh.geometry.attributes).some(a=>a.isInstancedBufferAttribute))continue;
  const e={mesh,geometry:null,position:null,positionVersion:-1,attribute:null,version:-1,color:null,colorVersion:-1,count:-1,world:new THREE.Matrix4(),views:[],prefix:[],padding:null},stack=[];entries.push(e);
  const before=mesh.onBeforeShadow,after=mesh.onAfterShadow;
  mesh.onBeforeShadow=function(renderer,object,mainCamera,shadowCamera,geometry,material,group){
   before.call(this,renderer,object,mainCamera,shadowCamera,geometry,material,group);let restore=null;
   const index=lookup.get(shadowCamera);view.multiplyMatrices(shadowCamera.projectionMatrix,shadowCamera.matrixWorldInverse);
   if(enabled&&index!==undefined&&geometry===e.geometry&&geometry.attributes.position===e.position&&geometry.attributes.position.version===e.positionVersion&&mesh.instanceMatrix===e.attribute&&mesh.instanceMatrix.version===e.version&&mesh.count===e.count&&e.world.equals(mesh.matrixWorld)&&e.views[index]?.equals(view)&&!material.displacementMap){
    restore=mesh.count;mesh.count=e.prefix[index];stats.skippedInstances+=restore-e.prefix[index];stats.savedTriangles+=(restore-e.prefix[index])*Math.min(group?.count??Infinity,geometry.drawRange.count,geometry.index?.count??geometry.attributes.position.count)/3;
   }
   stack.push(restore);
  };
  mesh.onAfterShadow=function(renderer,object,mainCamera,shadowCamera,geometry,material,group){const restore=stack.pop();if(restore!==null&&restore!==undefined)mesh.count=restore;after.call(this,renderer,object,mainCamera,shadowCamera,geometry,material,group);};
 }
 function update(){
  for(const v of views){v.light.updateWorldMatrix(true,false);v.light.target.updateWorldMatrix(true,false);v.light.shadow.updateMatrices(v.light);v.view.multiplyMatrices(v.camera.projectionMatrix,v.camera.matrixWorldInverse);v.frustum.setFromProjectionMatrix(v.view,v.camera.coordinateSystem);}
  stats.batches=entries.length;stats.instances=0;stats.lightInstances.fill(0);
  for(const e of entries){
   const o=e.mesh,g=o.geometry;o.updateWorldMatrix(true,false);const padding=(o.userData.waterMotionPadding??.01)*o.matrixWorld.getMaxScaleOnAxis()+(o.userData.refractedShadowPadding??0);
   if(e.geometry!==g||e.position!==g.attributes.position||e.positionVersion!==g.attributes.position.version||e.attribute!==o.instanceMatrix||e.version!==o.instanceMatrix.version||e.color!==o.instanceColor||e.colorVersion!==(o.instanceColor?.version??-1)||e.count!==o.count||e.padding!==padding||!e.world.equals(o.matrixWorld)||views.some((v,i)=>!e.views[i]?.equals(v.view))){
    g.computeBoundingBox();const needed=[];
    for(let i=0;i<o.count;i++){o.getMatrixAt(i,matrix);world.multiplyMatrices(o.matrixWorld,matrix);box.copy(g.boundingBox).applyMatrix4(world).expandByScalar(padding);needed.push(views.map(v=>v.frustum.intersectsBox(box)));}
    const priority=flags=>{const i=flags.indexOf(true);return i<0?views.length:i;};
    const order=needed.map((_,i)=>i);if(reorder)order.sort((a,b)=>priority(needed[a])-priority(needed[b]));
    e.prefix=views.map((_,j)=>{let n=0;order.forEach((id,i)=>{if(needed[id][j])n=i+1;});return n;});
    if(order.some((id,i)=>id!==i))for(const attribute of [o.instanceMatrix,o.instanceColor].filter(Boolean)){
     const original=attribute.array.slice();for(let i=0;i<order.length;i++)attribute.array.set(original.subarray(order[i]*attribute.itemSize,(order[i]+1)*attribute.itemSize),i*attribute.itemSize);attribute.needsUpdate=true;
    }
    e.geometry=g;e.position=g.attributes.position;e.positionVersion=g.attributes.position.version;e.attribute=o.instanceMatrix;e.version=o.instanceMatrix.version;e.color=o.instanceColor;e.colorVersion=o.instanceColor?.version??-1;e.count=o.count;e.padding=padding;e.world.copy(o.matrixWorld);e.views=views.map(v=>v.view.clone());
   }
   stats.instances+=e.count;e.prefix.forEach((n,i)=>stats.lightInstances[i]+=n);
  }
 }
 update();return {stats,update,beginFrame(){stats.savedTriangles=stats.skippedInstances=0;},set enabled(value){enabled=!!value;}};
}
