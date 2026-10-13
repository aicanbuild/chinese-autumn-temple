import {Matrix4,Frustum,Box3,CustomBlending} from 'three';
import {SSAOPass} from 'three/addons/postprocessing/SSAOPass.js';
import {AOSceneState} from './ao-scene-state.js';

// Architectural contact shading is reused only while the camera is unchanged.
// Movement/zoom/resize and normal/depth input changes refresh immediately.
export class CachedSSAOPass extends SSAOPass{
 constructor(scene,camera,width,height,kernelSize=16,clock=()=>performance.now()){
  super(scene,camera,width,height,kernelSize);
  this.clock=clock;this.lastView=new Matrix4();this.lastProjection=new Matrix4();
  this.refreshAt=0;this.invalidated=true;this.captures=0;this.reuses=0;
  this.animatedBox=new Box3();this.animatedFrustum=new Frustum();this.animatedView=new Matrix4();this.sceneState=new AOSceneState();this.excludeFromAO=()=>false;this.lastSettings='';
 }
 setSize(width,height){super.setSize(width,height);this.invalidated=true;}
 render(renderer,writeBuffer,readBuffer,...args){
  const now=this.clock(),camera=this.camera;
  this.animatedView.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);this.animatedFrustum.setFromProjectionMatrix(this.animatedView,camera.coordinateSystem);
  let animationInterval=Infinity;
  const sceneChanged=this.sceneState.changed(this.scene,camera,this.excludeFromAO,o=>{
   if(!o.isSkinnedMesh&&o.frustumCulled!==false&&!this.animatedFrustum.intersectsObject(o))return false;
   let interval=80;
   if(!o.isSkinnedMesh&&Number.isFinite(o.userData.aoMotionSpeed)&&o.userData.aoMotionSpeed>0){
    const g=o.geometry;if(!g.boundingBox)g.computeBoundingBox();
    this.animatedView.multiplyMatrices(camera.matrixWorldInverse,o.matrixWorld);
    const b=this.animatedBox.copy(g.boundingBox).applyMatrix4(this.animatedView).expandByScalar(o.userData.waterMotionPadding??0);
    const depth=-b.max.z,offAxis=Math.max(Math.abs(b.min.x),Math.abs(b.max.x),Math.abs(b.min.y),Math.abs(b.max.y));
    const focal=Math.max(Math.abs(camera.projectionMatrix.elements[0])*(this.width??1),Math.abs(camera.projectionMatrix.elements[5])*(this.height??1))/2;
    const pixelsPerSecond=depth>camera.near?focal*o.userData.aoMotionSpeed*o.matrixWorld.getMaxScaleOnAxis()/depth*(1+offAxis/depth):Infinity;
    interval=Math.max(16,Math.min(400,350/pixelsPerSecond));
   }
   animationInterval=Math.min(animationInterval,interval);return true;
  });
  const settings=[this.kernelRadius,this.minDistance,this.maxDistance,camera.near,camera.far].join('/');
  const refresh=this.invalidated||sceneChanged||settings!==this.lastSettings||(this.sceneState.animated&&now>=this.refreshAt)||!this.lastView.equals(camera.matrixWorld)||!this.lastProjection.equals(camera.projectionMatrix)||this.output!==SSAOPass.OUTPUT.Default;
  if(refresh){
   super.render(renderer,writeBuffer,readBuffer,...args);
   this.lastView.copy(camera.matrixWorld);this.lastProjection.copy(camera.projectionMatrix);
   this.refreshAt=now+(Number.isFinite(animationInterval)?animationInterval:80);this.invalidated=false;this.lastSettings=settings;this.captures++;
  }else{
   this.copyMaterial.uniforms.tDiffuse.value=this.blurRenderTarget.texture;
   this.copyMaterial.blending=CustomBlending;
   this._renderPass(renderer,this.copyMaterial,this.renderToScreen?null:readBuffer);this.reuses++;
  }
 }
}
