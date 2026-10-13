import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/water-ao.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export function','function');const {installWaterAOMask}=new Function('THREE',source+';return {installWaterAOMask};')(THREE);
function fixture(){
 const water=new THREE.Mesh(new THREE.PlaneGeometry(4,4));water.position.set(0,-.025,5.8);const camera=new THREE.PerspectiveCamera();let target={name:'color'},fail=false;const calls=[];
 const renderer={autoClear:true,shadowMap:{enabled:true},getRenderTarget:()=>target,setRenderTarget:t=>{target=t;},render(scene,cam){calls.push({scene,cam,target,autoClear:this.autoClear,shadows:this.shadowMap.enabled});if(fail)throw new Error('draw failed');}};
 const ao={camera,output:0,normalMaterial:{},normalRenderTarget:{texture:{}},ssaoMaterial:{uniforms:{},fragmentShader:'void main() {float realDepth = getLinearDepth( samplePointUv );}'},copyMaterial:{uniforms:{},fragmentShader:'vec4 texel = texture2D( tDiffuse, vUv );'},_renderOverride(){},render(r){this._renderOverride(r,this.normalMaterial,this.normalRenderTarget);}};
 const original={render:ao.render,override:ao._renderOverride,ssao:ao.ssaoMaterial.fragmentShader,copy:ao.copyMaterial.fragmentShader},mask=installWaterAOMask(ao,water);
 return {water,camera,renderer,ao,mask,calls,original,get target(){return target;},fail(){fail=true;}};
}
test('only AO depth receives the borrowed water surface and renderer state is restored even on failure',()=>{
 const f=fixture(),color=f.target;f.ao.render(f.renderer);assert.equal(f.calls.length,1);assert.equal(f.calls[0].target,f.ao.normalRenderTarget);assert.equal(f.calls[0].autoClear,false);assert.equal(f.calls[0].shadows,false);assert.equal(f.target,color);assert.equal(f.renderer.autoClear,true);assert.equal(f.renderer.shadowMap.enabled,true);
 const proxy=f.calls[0].scene.children[0];assert.equal(proxy.geometry,f.water.geometry);assert.ok(proxy.matrix.equals(f.water.matrixWorld));assert.notEqual(proxy,f.water);assert.equal(f.water.visible,true);
 f.fail();assert.throws(()=>f.ao.render(f.renderer),/draw failed/);assert.equal(f.target,color);assert.equal(f.renderer.autoClear,true);assert.equal(f.renderer.shadowMap.enabled,true);
});
test('visibility, transform and geometry changes invalidate the cached mask without touching the source water',()=>{
 const f=fixture();f.ao.render(f.renderer);f.ao.invalidated=false;f.ao.render(f.renderer);assert.equal(f.ao.invalidated,false);
 f.water.position.x=1;f.ao.render(f.renderer);assert.equal(f.ao.invalidated,true);f.ao.invalidated=false;
 f.water.visible=false;const count=f.calls.length;f.ao.render(f.renderer);assert.equal(f.calls.length,count);assert.equal(f.ao.invalidated,true);assert.equal(f.ao.copyMaterial.uniforms.waterMaskEnabled.value,false);
 f.water.visible=true;f.ao.render(f.renderer);f.ao.invalidated=false;f.water.geometry=new THREE.PlaneGeometry(3,3);f.ao.render(f.renderer);assert.equal(f.ao.invalidated,true);assert.equal(f.calls.at(-1).scene.children[0].geometry,f.water.geometry);
});
test('disable and disposal restore the pass without disposing shared geometry or leaking uniforms',()=>{
 const f=fixture();let disposed=false;f.water.geometry.addEventListener('dispose',()=>disposed=true);f.mask.enabled=false;f.ao.render(f.renderer);assert.equal(f.calls.length,0);
 f.mask.dispose();assert.equal(f.ao.render,f.original.render);assert.equal(f.ao._renderOverride,f.original.override);assert.equal(f.ao.ssaoMaterial.fragmentShader,f.original.ssao);assert.equal(f.ao.copyMaterial.fragmentShader,f.original.copy);assert.equal(f.ao.copyMaterial.uniforms.waterMaskNormals,undefined);assert.equal(disposed,false);
});
