import * as THREE from 'three';

// A rectangle's shadow cone is convex. Containing every box corner proves that
// the entire box is hidden; partial coverage and gaps always retain the object.
export function rectangleHidesBox(eye,box,r){
 const a=r.axis,b=(a+1)%3,c=(a+2)%3;
 const ea=eye.getComponent(a),eb=eye.getComponent(b),ec=eye.getComponent(c),plane=(r.lo[a]+r.hi[a])*.5,distance=plane-ea;
 if(Math.abs(distance)<.0001)return false;
 for(let bits=0;bits<8;bits++){
  const pa=(bits&(1<<a)?box.max:box.min).getComponent(a),t=distance/(pa-ea);
  if(!(t>0&&t<1-.00001))return false;
  const pb=(bits&(1<<b)?box.max:box.min).getComponent(b),pc=(bits&(1<<c)?box.max:box.min).getComponent(c);
  const qb=eb+t*(pb-eb),qc=ec+t*(pc-ec);
  if(qb<=r.lo[b]||qb>=r.hi[b]||qc<=r.lo[c]||qc>=r.hi[c])return false;
 }
 return true;
}
export function createHallOcclusion(scene,mainCamera,rectangles,{isInside=()=>false}={}){
 const view=new THREE.Matrix4(),lastView=new THREE.Matrix4(),frustum=new THREE.Frustum();let viewVersion=0;
 const eye=new THREE.Vector3(),stats={skippedDraws:0,savedTriangles:0,candidates:0},entries=[];let enabled=true;
 scene.traverse(o=>{
  // BatchedMesh owns per-camera subdraw lists; geometry.drawRange cannot hide
  // those lists. Its own instance frustum culling stays in charge.
  if(!o.isMesh||o.isWater||o.isBatchedMesh||o.isSkinnedMesh||o.geometry.morphAttributes.position?.length)return;
  // Only explicitly bounded static scenery or wind envelopes are eligible.
  if(!o.userData.waterClipStatic&&!Number.isFinite(o.userData.waterMotionPadding))return;
  const e={object:o,matrix:new THREE.Matrix4(),eye:new THREE.Vector3(Infinity,0,0),box:new THREE.Box3(),geometry:null,version:null,position:null,instance:null,viewVersion:-1,hidden:false};entries.push(e);
  const before=o.onBeforeRender,after=o.onAfterRender,stack=[];
  o.onBeforeRender=function(renderer,scene,camera,geometry,material,group){
   let restore=null;
   if(enabled&&camera===mainCamera&&isInside()){
    camera.getWorldPosition(eye);view.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);if(!lastView.equals(view)){lastView.copy(view);frustum.setFromProjectionMatrix(view,camera.coordinateSystem);viewVersion++;}
    const version=(o.instanceMatrix?.version??0)+'/'+geometry.attributes.position.version;
    if(e.geometry!==geometry||e.position!==geometry.attributes.position||e.instance!==o.instanceMatrix||e.version!==version||!e.matrix.equals(o.matrixWorld)){
     if(o.isInstancedMesh){o.computeBoundingBox();e.box.copy(o.boundingBox);}else{geometry.computeBoundingBox();e.box.copy(geometry.boundingBox);}
     e.box.applyMatrix4(o.matrixWorld).expandByScalar(o.userData.waterMotionPadding??.01);e.matrix.copy(o.matrixWorld);e.geometry=geometry;e.position=geometry.attributes.position;e.instance=o.instanceMatrix;e.version=version;e.eye.set(Infinity,0,0);
    }
    if(!e.eye.equals(eye)||e.viewVersion!==viewVersion){e.hidden=!frustum.intersectsBox(e.box)||rectangles.some(r=>rectangleHidesBox(eye,e.box,r));e.eye.copy(eye);e.viewVersion=viewVersion;}
    if(e.hidden){
     restore={start:geometry.drawRange.start,count:geometry.drawRange.count};
     stats.skippedDraws++;stats.savedTriangles+=Math.min(group?.count??Infinity,geometry.drawRange.count,geometry.index?.count??geometry.attributes.position.count)/3*(o.isInstancedMesh?o.count:1);
     geometry.setDrawRange(restore.start,0);
    }
   }
   stack.push(restore);before.call(this,renderer,scene,camera,geometry,material,group);
  };
  o.onAfterRender=function(renderer,scene,camera,geometry,material,group){const restore=stack.pop();if(restore)geometry.setDrawRange(restore.start,restore.count);after.call(this,renderer,scene,camera,geometry,material,group);};
 });
 stats.candidates=entries.length;
 return {stats,entries,set enabled(value){enabled=!!value;},beginFrame(){stats.skippedDraws=stats.savedTriangles=0;}};
}
