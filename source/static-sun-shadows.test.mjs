import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/static-sun-shadows.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const create=new Function('THREE',source+';return createStaticSunShadows')(T);
function fixture(){
 const scene=new T.Scene(),sun=new T.DirectionalLight(),camera=new T.PerspectiveCamera(),root=new T.Group(),fixed=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial()),moving=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial());sun.castShadow=true;sun.position.set(2,5,4);fixed.castShadow=moving.castShadow=true;root.add(fixed);scene.add(root,moving,sun,sun.target);
 let target=new T.WebGLRenderTarget(10,10),face=2,mip=1;const caller=target,passes=[],copies=[],listeners=new Map();let queries=0;
 const gl={FRAMEBUFFER_BINDING:1,READ_FRAMEBUFFER:2,DRAW_FRAMEBUFFER:3,COLOR_BUFFER_BIT:16384,DEPTH_BUFFER_BIT:256,NEAREST:9728,getParameter(){queries++;return target;},bindFramebuffer(){},blitFramebuffer(...args){copies.push(args);}};
 const renderer={capabilities:{maxTextureSize:2048},clippingPlanes:[],localClippingEnabled:false,domElement:{addEventListener:(n,f)=>listeners.set(n,f),removeEventListener:n=>listeners.delete(n)},getRenderTarget:()=>target,getActiveCubeFace:()=>face,getActiveMipmapLevel:()=>mip,setRenderTarget:(t,f=0,m=0)=>{target=t;face=f;mip=m;},initRenderTarget(){},copyTextureToTexture(a,b){copies.push([a,b]);},clear(){},shadowMap:{enabled:true,autoUpdate:false,needsUpdate:true,type:T.PCFSoftShadowMap}};
 renderer.getContext=()=>gl;renderer.resetState=()=>{target=null;face=mip=0;};
 renderer.shadowMap.render=function(lights,s,c){if(!this.needsUpdate&&!this.autoUpdate)return;const previous=target,cf=face,cm=mip;for(const light of lights){renderer.setRenderTarget(light.shadow.map);renderer.clear();passes.push([fixed.castShadow,moving.castShadow]);if(renderer.fail)throw new Error('draw failed');}renderer.setRenderTarget(previous,cf,cm);this.needsUpdate=false;};
 const original=renderer.shadowMap.render,clear=renderer.clear,cache=create(renderer,scene,sun,[root]);
 const render=()=>{scene.updateMatrixWorld(true);renderer.shadowMap.needsUpdate=true;renderer.shadowMap.render([sun],scene,camera);};
 return {scene,sun,camera,root,fixed,moving,renderer,cache,render,passes,copies,caller,original,clear,listeners,get queries(){return queries;}};
}
test('static depth and color are saved and restored while dynamic casters render every update',()=>{
 const f=fixture();f.render();assert.deepEqual(f.passes,[[true,false],[false,true]]);assert.equal(f.copies.length,2);assert.equal(f.cache.stats.builds,1);assert.equal(f.queries,2);
 f.moving.position.x=3;f.render();assert.deepEqual(f.passes.at(-1),[false,true]);assert.equal(f.cache.stats.builds,1);assert.equal(f.cache.stats.reuses,1);assert.equal(f.copies.length,3);assert.equal(f.queries,2);
 assert.ok(f.copies.every(args=>args[8]===(16384|256)));assert.equal(f.renderer.getRenderTarget(),f.caller);assert.equal(f.renderer.getActiveCubeFace(),2);assert.equal(f.renderer.getActiveMipmapLevel(),1);assert.equal(f.fixed.castShadow,true);assert.equal(f.moving.castShadow,true);assert.equal(f.renderer.clear,f.clear);
});
test('static transform, visibility, alpha, geometry replacement, light and context changes rebuild the cached map',()=>{
 const f=fixture();f.render();let builds=1;
 for(const change of [()=>f.fixed.position.x=1,()=>f.root.visible=false,()=>f.root.visible=true,()=>f.fixed.material.alphaTest=.5,()=>f.fixed.geometry.setAttribute('position',f.fixed.geometry.attributes.position.clone()),()=>f.sun.position.x=4,()=>f.camera.layers.enable(2),()=>f.listeners.get('webglcontextrestored')()]){change();f.render();assert.equal(f.cache.stats.builds,++builds);}
});
test('animated or customized shadow meshes remain dynamic and failures restore renderer ownership',()=>{
 const f=fixture();f.fixed.customDepthMaterial=new T.MeshDepthMaterial();f.render();assert.equal(f.cache.stats.staticMeshes,0);assert.deepEqual(f.passes,[[false,false],[true,true]]);
 f.renderer.fail=true;assert.throws(f.render,/draw failed/);assert.equal(f.fixed.castShadow,true);assert.equal(f.moving.castShadow,true);assert.equal(f.renderer.clear,f.clear);assert.equal(f.renderer.getRenderTarget(),f.caller);assert.equal(f.renderer.shadowMap.needsUpdate,true);
 f.renderer.fail=false;f.cache.dispose();assert.equal(f.renderer.shadowMap.render,f.original);assert.equal(f.listeners.size,0);
});
test('disabled and unsupported VSM updates retain the original full shadow pass',()=>{
 const f=fixture();f.cache.enabled=false;f.render();assert.deepEqual(f.passes,[[true,true]]);assert.equal(f.cache.stats.builds,0);f.cache.enabled=true;f.renderer.shadowMap.type=T.VSMShadowMap;f.render();assert.equal(f.cache.stats.builds,0);assert.deepEqual(f.passes.at(-1),[true,true]);
});
test('a second light receives the complete caster list even while the sun reuses its static depth',()=>{
 const f=fixture(),spot=new T.SpotLight();spot.castShadow=true;spot.shadow.map=new T.WebGLRenderTarget(32,32);f.scene.add(spot);f.render();f.passes.length=0;f.renderer.shadowMap.needsUpdate=true;f.renderer.shadowMap.render([f.sun,spot],f.scene,f.camera);assert.deepEqual(f.passes,[[false,true],[true,true]]);assert.equal(f.renderer.clear,f.clear);assert.equal(f.renderer.getRenderTarget(),f.caller);
});
test('resized or disposed shadow storage reacquires framebuffers and rebuilds before reuse',()=>{
 const f=fixture();f.render();f.sun.shadow.mapSize.set(1024,1024);f.render();assert.equal(f.cache.stats.builds,2);assert.equal(f.queries,4);assert.equal(f.cache.stats.bytes,1024*1024*8);
 f.sun.shadow.map.dispose();f.render();assert.equal(f.cache.stats.builds,3);assert.equal(f.queries,6);f.render();assert.equal(f.cache.stats.builds,3);assert.equal(f.queries,6);
});
test('context restoration reconnects the new renderer shadow map and tracks interleaved vertex edits',()=>{
 const f=fixture(),buffer=new T.InterleavedBuffer(new Float32Array(9),3);f.fixed.geometry.setAttribute('position',new T.InterleavedBufferAttribute(buffer,3,0));f.render();buffer.needsUpdate=true;f.render();assert.equal(f.cache.stats.builds,2);
 f.renderer.shadowMap={...f.renderer.shadowMap,render:f.original};f.listeners.get('webglcontextrestored')();f.render();assert.equal(f.cache.stats.builds,3);assert.equal(f.queries,4);f.cache.dispose();assert.equal(f.renderer.shadowMap.render,f.original);
});
test('a garden LOD switch refreshes fixed shadows once and preserves dynamic foliage',()=>{
 const f=fixture(),lod=new T.LOD(),far=new T.Mesh(new T.BoxGeometry(),f.fixed.material);
 far.castShadow=true;lod.autoUpdate=false;lod.addLevel(f.fixed,0);lod.addLevel(far,25,.15);f.root.add(lod);
 // The cache sees the LOD's actual selected child, not the model's nominal distance.
 const select=distance=>{f.camera.position.set(0,0,distance);f.camera.updateMatrixWorld();lod.update(f.camera);};
 select(10);f.render();assert.equal(f.cache.stats.builds,1);assert.equal(f.fixed.visible,true);assert.equal(far.visible,false);
 select(30);f.render();assert.equal(f.cache.stats.builds,2);assert.equal(f.fixed.visible,false);assert.equal(far.visible,true);
 f.moving.position.x=2;f.render();assert.equal(f.cache.stats.builds,2);assert.deepEqual(f.passes.at(-1),[false,true]);
 select(24);f.render();assert.equal(f.cache.stats.builds,2);assert.equal(far.visible,true);
 select(20);f.render();assert.equal(f.cache.stats.builds,3);assert.equal(f.fixed.visible,true);assert.equal(far.visible,false);
 f.render();assert.equal(f.cache.stats.builds,3);assert.equal(f.moving.castShadow,true);
});
test('registered static pond depth is cached only while shader callbacks and optical state match',()=>{
 const f=fixture();let optical=1;f.fixed.customDepthMaterial=new T.MeshDepthMaterial();f.fixed.onBeforeShadow=()=>{};f.fixed.onAfterShadow=()=>{};
 f.fixed.userData.pondStaticShadow={depth:f.fixed.customDepthMaterial,before:f.fixed.onBeforeShadow,after:f.fixed.onAfterShadow,state:()=>[optical]};
 f.render();f.render();assert.equal(f.cache.stats.staticMeshes,1);assert.equal(f.cache.stats.builds,1);assert.equal(f.cache.stats.reuses,1);
 optical=2;f.render();assert.equal(f.cache.stats.builds,2);
 f.fixed.onBeforeShadow=()=>{};f.render();assert.equal(f.cache.stats.staticMeshes,0);assert.deepEqual(f.passes.at(-1),[true,true]);
});
