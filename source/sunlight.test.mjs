import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/sunlight.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replace('export class','class');
class Pass{};class Quad{constructor(m){this.material=m;}render(r){r.quads.push(this.material);}dispose(){}}
const SunlightPass=new Function('THREE','Pass','FullScreenQuad',code+';return SunlightPass;')(THREE,Pass,Quad);
test('sunlight follows the current camera, scene depth and changed sun instead of cached initial lighting',()=>{
 const camera=new THREE.PerspectiveCamera(43,1.5,.09,420),sun=new THREE.DirectionalLight('#ffe7c2',5.2);sun.position.set(-24,21,10);sun.target.position.set(0,0,-1);sun.shadow.map={texture:new THREE.Texture()};
 camera.position.set(14,8.5,26);camera.updateMatrixWorld();const pass=new SunlightPass(camera,sun);pass.setSize(1280,720);assert.equal(pass.volume.width,320);assert.equal(pass.volume.height,180);
 const renderer={quads:[],targets:[],setRenderTarget(t){this.targets.push(t);}},read={texture:new THREE.Texture(),depthTexture:new THREE.DepthTexture()},write={};
 pass.render(renderer,write,read);assert.equal(pass.integrate.uniforms.depth.value,read.depthTexture);assert.ok(pass.integrate.uniforms.cameraWorld.value.equals(camera.matrixWorld));assert.equal(pass.composite.uniforms.tDiffuse.value,read.texture);assert.deepEqual(renderer.targets,[pass.volume,write]);assert.equal(renderer.quads.length,2);
 const before=pass.composite.uniforms.sunColor.value.clone();sun.intensity*=.5;camera.position.z=4;camera.updateMatrixWorld();const next={texture:new THREE.Texture(),depthTexture:new THREE.DepthTexture()};pass.render(renderer,write,next);
 assert.ok(pass.composite.uniforms.sunColor.value.equals(before.multiplyScalar(.5)));assert.equal(pass.integrate.uniforms.depth.value,next.depthTexture);assert.ok(pass.integrate.uniforms.eye.value.equals(camera.position));pass.dispose();
});
