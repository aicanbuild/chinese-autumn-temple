import * as THREE from 'three';

// Keep one draw per material. Logical cells select whole original triangles;
// neither the vertex buffers nor triangle order are changed by visibility.
export function createStaticCellCulling(root,camera,{cellSize=3,minTriangles=20000}={}){
 if(!Number.isFinite(cellSize)||cellSize<=0)throw new Error('Invalid cell size');
 const entries=[],frustum=new THREE.Frustum(),view=new THREE.Matrix4(),point=new THREE.Vector3();
 const stats={meshes:0,cells:0,selectedTriangles:0,savedTriangles:0,indexUpdates:0};let enabled=true;
 root.traverse(mesh=>{
  if(!mesh.isMesh||mesh.isInstancedMesh||mesh.isBatchedMesh||mesh.isSkinnedMesh)return;
  const g=mesh.geometry,p=g.attributes.position;
  if(!g.index||Array.isArray(mesh.material)||mesh.material.transparent||mesh.material.displacementMap||g.groups.length||Object.keys(g.morphAttributes).length||g.drawRange.start!==0||g.drawRange.count!==Infinity||g.index.count/3<minTriangles)return;
  const cells=[],lookup=new Map(),runs=[];let lastCell=-1;
  for(let i=0;i<g.index.count;i+=3){
   const vertices=[g.index.getX(i),g.index.getX(i+1),g.index.getX(i+2)];
   const key=[0,1,2].map(axis=>Math.floor(vertices.reduce((n,j)=>n+p.getComponent(j,axis),0)/(3*cellSize))).join('/');
   let cell=lookup.get(key);if(cell===undefined){cell=cells.length;lookup.set(key,cell);cells.push({local:new THREE.Box3(),world:new THREE.Box3(),visible:true});}
   for(const v of vertices)cells[cell].local.expandByPoint(point.fromBufferAttribute(p,v));
   if(cell===lastCell)runs.at(-1).count+=3;else{runs.push({cell,start:i,count:3});lastCell=cell;}
  }
  const original=g.index,filtered=new THREE.BufferAttribute(new original.array.constructor(original.array.length),1).setUsage(THREE.DynamicDrawUsage);
  const e={mesh,geometry:g,original,position:p,positionVersion:p.data?.version??p.version,indexVersion:original.version,cells,runs,filtered,count:original.count,matrix:new THREE.Matrix4(),view:new THREE.Matrix4(),valid:false};entries.push(e);
  const before=mesh.onBeforeRender,after=mesh.onAfterRender,stack=[];
  mesh.onBeforeRender=function(renderer,scene,drawCamera,geometry,material,group){
   // Unknown edits/draw ranges fall back to the unchanged authoritative mesh.
   const safe=geometry===g&&g.index===original&&(p.data?.version??p.version)===e.positionVersion&&original.version===e.indexVersion&&g.attributes.position===p&&g.drawRange.start===0&&g.drawRange.count===Infinity;
   let restore=null;
   if(enabled&&drawCamera===camera&&safe){
    view.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
    if(!e.valid||!e.matrix.equals(mesh.matrixWorld)||!e.view.equals(view)){
     frustum.setFromProjectionMatrix(view,camera.coordinateSystem);let changed=!e.valid;
     for(const cell of cells){cell.world.copy(cell.local).applyMatrix4(mesh.matrixWorld).expandByScalar(.002);const visible=frustum.intersectsBox(cell.world);changed ||= visible!==cell.visible;cell.visible=visible;}
     if(changed){let offset=0;for(const run of runs)if(cells[run.cell].visible){filtered.array.set(original.array.subarray(run.start,run.start+run.count),offset);offset+=run.count;}e.count=offset;filtered.needsUpdate=true;stats.indexUpdates++;}
     e.matrix.copy(mesh.matrixWorld);e.view.copy(view);e.valid=true;
    }
    if(e.count<original.count){restore={index:original,start:g.drawRange.start,count:g.drawRange.count};g.setIndex(filtered);g.setDrawRange(0,e.count);}
   }
   stack.push(restore);before.call(this,renderer,scene,drawCamera,geometry,material,group);
  };
  mesh.onAfterRender=function(renderer,scene,drawCamera,geometry,material,group){const restore=stack.pop();after.call(this,renderer,scene,drawCamera,geometry,material,group);if(restore){g.setIndex(restore.index);g.setDrawRange(restore.start,restore.count);}};
 });
 stats.meshes=entries.length;stats.cells=entries.reduce((n,e)=>n+e.cells.length,0);
 return {entries,stats,get enabled(){return enabled;},set enabled(v){enabled=!!v;},sample(){stats.selectedTriangles=entries.reduce((n,e)=>n+e.count/3,0);stats.savedTriangles=entries.reduce((n,e)=>n+(e.original.count-e.count)/3,0);return {...stats};}};
}
