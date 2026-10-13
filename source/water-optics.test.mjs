import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {pondTransmittanceGLSL} from '../dist/water-medium.js';
const refractionSource=fs.readFileSync(new URL('../dist/water-refraction.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function').replaceAll('export const','const');
const {applyWaterRefraction}=new Function('THREE',refractionSource+';return {applyWaterRefraction};')(THREE);
const code=fs.readFileSync(new URL('../dist/water-optics.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {capturedWaterPath,depthWaterFragment}=new Function('THREE','applyWaterRefraction','pondTransmittanceGLSL',code+';return {capturedWaterPath,depthWaterFragment};')(THREE,applyWaterRefraction,pondTransmittanceGLSL);
const rc=fs.readFileSync(new URL('../dist/vendor/three/addons/objects/Refractor.js',import.meta.url),'utf8').replace(/import\s*\{([\s\S]*?)\}\s*from 'three';/,'const {$1}=THREE;').replace(/export\s*\{[^}]+\};?/g,'');
const Refractor=new Function('THREE',rc+';return Refractor;')(THREE);
test('actual oblique refraction camera reconstructs fish and bed water paths at different view angles',()=>{
 const plane=new Refractor(new THREE.PlaneGeometry(25,15));plane.rotation.x=-Math.PI/2;plane.position.y=-.025;plane.updateMatrixWorld();
 const renderer={xr:{enabled:false},shadowMap:{autoUpdate:false},getRenderTarget:()=>null,setRenderTarget(){},render(){},autoClear:true};
 for(const eye of [[0,8,16],[8,1.5,20],[-4,3,12]]){
  const camera=new THREE.PerspectiveCamera(43,1.7,.09,420);camera.position.set(...eye);camera.lookAt(0,0,5.8);camera.updateMatrixWorld();
  plane.onBeforeRender(renderer,new THREE.Scene(),camera);
  const vp=new THREE.Matrix4().multiplyMatrices(plane.camera.projectionMatrix,plane.camera.matrixWorldInverse),inv=vp.clone().invert();
  const paths=[];
  for(const y of [-.10,-.33,-.90,-1.8]){
   const p=new THREE.Vector3(0,y,5.8),clip=new THREE.Vector4(p.x,p.y,p.z,1).applyMatrix4(vp);clip.multiplyScalar(1/clip.w);
   const path=capturedWaterPath(new THREE.Vector2(clip.x*.5+.5,clip.y*.5+.5),clip.z*.5+.5,inv,camera.position);
   const direction=p.clone().sub(camera.position).normalize(),expected=Math.min(8,(-.025-y)/Math.max(Math.abs(direction.y),.08));assert.ok(Math.abs(path-expected)<1e-8);paths.push(path);
  }
  assert.ok(paths.every((p,i)=>i===0||p>=paths[i-1]));
 }plane.dispose();
});
test('depth and inverse projection track the exact refraction capture while default Water stays compatible',()=>{
 const text=fs.readFileSync(new URL('../dist/vendor/three/addons/objects/Water2.js',import.meta.url),'utf8').replace(/import[\s\S]*?from ['"][^'"]+['"];\n/g,'').replace(/export\s*\{[^}]+\};?/g,'');
 const captures=[];class Capture{constructor(){this.matrixWorld=new THREE.Matrix4();this.camera=new THREE.PerspectiveCamera(60,1,.1,100);this.camera.position.set(2,3,4);this.camera.updateMatrixWorld();this.target={texture:new THREE.Texture()};captures.push(this);}getRenderTarget(){return this.target;}onBeforeRender(){this.camera.projectionMatrix.elements[6]=.14;}}
 const names=['Clock','DepthTexture','UnsignedIntType','Color','Matrix4','Mesh','RepeatWrapping','ShaderMaterial','TextureLoader','UniformsLib','UniformsUtils','Vector2','Vector4'];
 const Water=new Function(...names,'Reflector','Refractor',text+';return Water;')(...names.map(n=>THREE[n]),Capture,Capture);
 const water=new Water(new THREE.PlaneGeometry(),{normalMap0:new THREE.Texture(),normalMap1:new THREE.Texture(),refractionDepth:true,textureWidth:640,textureHeight:320});
 const camera=new THREE.PerspectiveCamera();camera.updateMatrixWorld();water.onBeforeRender({},new THREE.Scene(),camera);
 const u=water.material.uniforms,r=captures[1];assert.equal(u.tRefractionDepth.value,r.target.depthTexture);assert.equal(u.tRefractionMap.value,r.target.texture);assert.equal(u.tRefractionDepth.value.image.width,640);
 assert.ok(u.refractionInverseViewProjection.value.equals(r.camera.projectionMatrix.clone().invert().premultiply(r.camera.matrixWorld)));
 assert.ok(u.refractionViewProjection.value.equals(r.camera.projectionMatrix.clone().multiply(r.camera.matrixWorldInverse)));
 const fragment=depthWaterFragment(Water.WaterShader.fragmentShader);
 const expression=fragment.match(/vec3 normal = (normalize\(vec3\([^\n;]+\)\));/)[1];
 const decode=new Function('normalColor','normalize','vec3','max','return '+expression);
 for(const [gx,gy] of [[0,0],[.3,-.2],[-.4,.5]]){
  const length=Math.hypot(gx,gy,1),encoded={r:(1-.65*gx/length)/2,g:(1-.65*gy/length)/2,b:(1+1/length)/2};
  const actual=decode(encoded,v=>v.normalize(),(x,y,z)=>new THREE.Vector3(x,y,z),Math.max),expected=new THREE.Vector3(-.273*gx,1,-.273*gy).normalize();
  assert.ok(actual.distanceTo(expected)<1e-12,'shader decodes signed Z and matches the photon-bake slope strength');
 }
assert.ok(fragment.includes('uniform sampler2D tRefractionDepth'));assert.ok(fragment.includes('refractionInverseViewProjection*vec4'));assert.ok(!fragment.includes('waterDepth=.18'));assert.ok(fragment.includes('mix(submerged,reflectColor.rgb,reflectance)'));
assert.ok(fragment.includes(pondTransmittanceGLSL()));assert.ok(fragment.includes('vec3 transmission=pondBeamTransmittance(waterPath)'));assert.ok(fragment.includes('float waterPath=refractionTravel;'));
});
