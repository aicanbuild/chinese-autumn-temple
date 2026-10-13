import * as THREE from 'three';

// Cache explicitly selected, ordinary mesh casters. Keep packed shadow color
// AND the depth attachment so dynamic casters retain the usual depth test.
// One WebGL2 framebuffer blit preserves both attachments. Renderer state is
// reset after this external GL operation; no private renderer fields are used.
export function createStaticSunShadows(renderer,scene,light,roots){
 let shadowMap=renderer.shadowMap,original=shadowMap.render;const stats={builds:0,reuses:0,staticMeshes:0,bytes:0},view=new THREE.Matrix4();
 let enabled=true,signature=null,cache=null,ownedMap=null,framebuffers=null,nextId=0;const identities=new WeakMap(),gl=renderer.getContext();
 const storageDisposed=()=>{signature=null;framebuffers=null;};
 const id=o=>{if(!o)return null;if(!identities.has(o))identities.set(o,++nextId);return identities.get(o);};
 const textureState=t=>t?[t.uuid,t.version,t.source.version,...t.matrix.elements,t.wrapS,t.wrapT,t.channel]:null;
 function snapshot(camera){
  const meshes=[],ids=new Set();
  for(const root of roots)root.traverse(o=>{
   const pond=o.userData.pondStaticShadow,pondSafe=pond&&pond.depth===o.customDepthMaterial&&pond.before===o.onBeforeShadow&&pond.after===o.onAfterShadow;
   if(ids.has(o.id)||!o.isMesh||o.isInstancedMesh||o.isBatchedMesh||o.isSkinnedMesh||Object.values(o.geometry.morphAttributes).some(a=>a.length)||(!pondSafe&&(o.customDepthMaterial||o.onBeforeShadow!==THREE.Object3D.prototype.onBeforeShadow||o.onAfterShadow!==THREE.Object3D.prototype.onAfterShadow))||o.customDistanceMaterial)return;
   ids.add(o.id);meshes.push(o);
  });
  const state=[shadowMap.type,camera.layers.mask,renderer.localClippingEnabled,renderer.clippingPlanes.map(p=>[...p.normal.toArray(),p.constant]),light.shadow.mapSize.toArray(),view.elements];
  for(const o of meshes){
   let visible=true;for(let parent=o;parent;parent=parent.parent)visible&&=parent.visible;
   const g=o.geometry,materials=Array.isArray(o.material)?o.material:[o.material];
   state.push([o.userData.pondStaticShadow?.state?.(),o.customDepthMaterial?.version,o.id,o.castShadow,visible,o.layers.mask,o.frustumCulled,...o.matrixWorld.elements,g.uuid,id(g.index),g.index?.version,g.drawRange.start,g.drawRange.count,g.groups,Object.entries(g.attributes).map(([k,a])=>[k,id(a),a.version,id(a.data),a.data?.version,a.count,a.itemSize]),materials.map(m=>{
    for(const t of [m.map,m.alphaMap,m.displacementMap])if(t?.matrixAutoUpdate)t.updateMatrix();
    return [m.uuid,m.version,m.visible,m.side,m.shadowSide,m.alphaTest,m.alphaHash,m.opacity,m.displacementScale,m.displacementBias,m.clipShadows,m.clippingPlanes?.map(p=>[...p.normal.toArray(),p.constant]),textureState(m.map),textureState(m.alphaMap),textureState(m.displacementMap)];
   })]);
  }
  return {meshes,key:JSON.stringify(state)};
 }
 function initialize(){
  const shadow=light.shadow,w=Math.min(shadow.mapSize.x,renderer.capabilities.maxTextureSize),h=Math.min(shadow.mapSize.y,renderer.capabilities.maxTextureSize);shadow.mapSize.set(w,h);
  if(!shadow.map){shadow.map=new THREE.WebGLRenderTarget(w,h,{minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter});shadow.camera.updateProjectionMatrix();}
  const map=shadow.map;if(map.width!==w||map.height!==h)map.setSize(w,h);
  if(ownedMap!==map){ownedMap?.removeEventListener('dispose',storageDisposed);ownedMap=map;map.addEventListener('dispose',storageDisposed);storageDisposed();cache?.dispose();cache=null;}
  renderer.initRenderTarget(map);
  if(!cache||cache.width!==w||cache.height!==h){cache?.dispose();cache=map.clone();signature=null;framebuffers=null;stats.bytes=w*h*8;}
  renderer.initRenderTarget(cache);
  if(!framebuffers){renderer.setRenderTarget(map);const live=gl.getParameter(gl.FRAMEBUFFER_BINDING);renderer.setRenderTarget(cache);framebuffers={live,cached:gl.getParameter(gl.FRAMEBUFFER_BINDING)};}
  return map;
 }
 function copy(from,to){
  gl.bindFramebuffer(gl.READ_FRAMEBUFFER,from===cache?framebuffers.cached:framebuffers.live);gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER,to===cache?framebuffers.cached:framebuffers.live);
  gl.blitFramebuffer(0,0,from.width,from.height,0,0,to.width,to.height,gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT,gl.NEAREST);
  // Public interoperability boundary: invalidate GL/program/material caches
  // before normal Three shadow drawing resumes. Handles are queried only on
  // allocation/restoration, never in the per-update copy path.
  renderer.resetState();
  renderer.setRenderTarget(to);
 }
 function render(lights,currentScene,camera){
  if(!enabled||currentScene!==scene||!light.isDirectionalLight||!lights.includes(light)||!shadowMap.enabled||(!shadowMap.autoUpdate&&!shadowMap.needsUpdate)||(light.shadow.autoUpdate===false&&!light.shadow.needsUpdate)||![THREE.BasicShadowMap,THREE.PCFShadowMap,THREE.PCFSoftShadowMap].includes(shadowMap.type))return original.call(this,lights,currentScene,camera);
  const target=renderer.getRenderTarget(),face=renderer.getActiveCubeFace(),mip=renderer.getActiveMipmapLevel();
  const map=initialize();light.shadow.updateMatrices(light);view.multiplyMatrices(light.shadow.camera.projectionMatrix,light.shadow.camera.matrixWorldInverse);
  const current=snapshot(camera),set=new Set(current.meshes),changed=[];const clear=renderer.clear;renderer.setRenderTarget(target,face,mip);
  const hide=predicate=>{scene.traverse(o=>{if(o.castShadow&&predicate(o)){changed.push(o);o.castShadow=false;}});};
  const restore=()=>{for(const o of changed)o.castShadow=true;changed.length=0;};
  try{
   if(signature!==current.key){
    hide(o=>!set.has(o));original.call(this,[light],scene,camera);restore();copy(map,cache);renderer.setRenderTarget(target,face,mip);signature=current.key;stats.builds++;
   }else stats.reuses++;
   stats.staticMeshes=current.meshes.filter(o=>o.castShadow).length;
   hide(o=>set.has(o));shadowMap.needsUpdate=true;light.shadow.needsUpdate=true;
   renderer.clear=function(...args){if(renderer.getRenderTarget()===map){copy(cache,map);return;}return clear.apply(this,args);};
   original.call(this,[light],currentScene,camera);
   // Other lights must see every caster. Their shadow maps are independent
   // and must never inherit the sun's temporary static-caster exclusion.
   restore();renderer.clear=clear;const remaining=lights.filter(l=>l!==light);
   if(remaining.length){shadowMap.needsUpdate=true;original.call(this,remaining,currentScene,camera);}
  }catch(error){signature=null;shadowMap.needsUpdate=true;light.shadow.needsUpdate=true;throw error;}
  finally{restore();renderer.clear=clear;renderer.setRenderTarget(target,face,mip);}
 }
 shadowMap.render=render;
 const invalidate=()=>{signature=null;},restored=()=>{storageDisposed();if(renderer.shadowMap!==shadowMap){shadowMap=renderer.shadowMap;original=shadowMap.render;shadowMap.render=render;}};renderer.domElement.addEventListener('webglcontextrestored',restored);
 return {stats,invalidate,get enabled(){return enabled;},set enabled(value){enabled=!!value;},dispose(){if(shadowMap.render===render)shadowMap.render=original;renderer.domElement.removeEventListener('webglcontextrestored',restored);ownedMap?.removeEventListener('dispose',storageDisposed);cache?.dispose();shadowMap.needsUpdate=true;light.shadow.needsUpdate=true;}};
}
