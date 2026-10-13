import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/lotus-lighting.js',import.meta.url),'utf8').replaceAll('export function','function');const{finishLotusLighting,lotusLightingChunk}=new Function(code+';return {finishLotusLighting,lotusLightingChunk} ')();
test('thin transport keeps the source pigment, normal maps and opaque depth path',()=>{
 const source=new THREE.MeshStandardMaterial({color:'#f6b6cd',roughness:.62,side:THREE.DoubleSide});source.map=new THREE.Texture();source.normalMap=new THREE.Texture();
 const material=finishLotusLighting(source,THREE.ShaderChunk.lights_fragment_begin);
 assert.notEqual(material,source);assert.equal(material.map,source.map);assert.equal(material.normalMap,source.normalMap);assert.deepEqual(material.color,source.color);assert.equal(material.transparent,false);assert.equal(material.depthWrite,true);assert.equal(material.emissive.getHex(),0);assert.equal(material.transmission,undefined);assert.equal(finishLotusLighting(material,''),material);
 const shader={vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};material.onBeforeCompile(shader);
 assert.ok(shader.vertexShader.includes('lotusExitPosition'));assert.ok(shader.fragmentShader.includes('RE_Direct_Lotus'));assert.ok(shader.fragmentShader.includes('reflected * ( 1.0 - fraction )'));assert.ok(shader.fragmentShader.includes('fraction * backCosine * directLight.color'));
});
test('one shadow lookup per source remains, including point-light near/far and spot projector maps',()=>{
 const before=THREE.ShaderChunk.lights_fragment_begin,after=lotusLightingChunk(before);
 for(const name of ['getShadow(','getPointShadow('])assert.equal(after.split(name).length,before.split(name).length);
 for(const pair of [['DirectionalShadowCoord','DirectionalShadow'],['SpotLightCoord','SpotShadow'],['PointShadowCoord','PointShadow']])assert.ok(after.includes(`? vLotus${pair[1]}[ i ] : v${pair[0]}[ i ]`));
 assert.ok(after.includes('spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;'));assert.ok(after.includes('pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar'));
});
test('export includes local transport and thickness only on the two botanical surfaces',()=>{
 const bytes=fs.readFileSync(new URL('../dist/assets/lotus-surfaces.glb',import.meta.url)),length=bytes.readUInt32LE(12),glb=JSON.parse(bytes.subarray(20,20+length));let surfaces=0;
 for(const n of glb.nodes.filter(n=>n.mesh!==undefined)){
  const p=glb.meshes[n.mesh].primitives[0],keys=Object.keys(p.attributes),isSurface=n.extras.sourceMaterial.includes('living lotus');
  for(const name of ['_LOTUS_TRANSMITTANCE','_LOTUS_THICKNESS']){
   assert.equal(keys.includes(name),isSurface);
   if(isSurface){const attr=glb.accessors[p.attributes[name]],position=glb.accessors[p.attributes.POSITION];assert.equal(attr.count,position.count);assert.equal(attr.type,'SCALAR');}
  }
  if(isSurface)surfaces++;
 }
 assert.equal(surfaces,2);
});
