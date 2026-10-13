import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/hall-reflections.js',import.meta.url),'utf8').replace(/^import.*$/gm,'').replaceAll('export function','function');
const {applyHallReflection}=new Function('THREE',code+';return {applyHallReflection}')(T);
test('indoor reflection preserves authored material and existing shader hooks',()=>{
 const texture=new T.Texture(),m=new T.MeshPhysicalMaterial({roughness:.35,metalness:.8,clearcoat:.2});let calls=0;m.onBeforeCompile=s=>{calls++;s.uniforms.previous={value:1};s.fragmentShader+='\n// original finish';};m.customProgramCacheKey=()=> 'old-material';const map=new T.Texture();m.map=map;
 applyHallReflection(m,texture);assert.equal(m.envMap,texture);assert.deepEqual(m.envMapRotation.toArray(),[0,0,0,'XYZ']);assert.equal(m.map,map);assert.equal(m.roughness,.35);assert.equal(m.clearcoat,.2);assert.equal(m.metalness,.8);
 const shader={uniforms:{},vertexShader:'#include <worldpos_vertex>',fragmentShader:'#include <envmap_physical_pars_fragment>'};m.onBeforeCompile(shader);assert.equal(calls,1);assert.ok(shader.uniforms.previous);assert.ok(shader.vertexShader.includes('instanceMatrix*hallPoint'));assert.ok(shader.fragmentShader.includes('envMapRotation * hallProbeDirection( reflectVec )'));assert.ok(shader.fragmentShader.includes('envMapRotation * worldNormal'));assert.ok(shader.fragmentShader.includes('// original finish'));assert.equal(m.customProgramCacheKey(),'old-material|hall-box-probe-v1');
});
test('capture restores visibility and renderer state even if the capture fails',()=>{
 const scene=new T.Scene(),hero=new T.Group(),water=new T.Mesh(),sun=new T.DirectionalLight();sun.castShadow=true;water.isWater=true;water.visible=false;scene.add(hero,water,sun);
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:true},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};let disposed=0;
 class PMREMGenerator{fromScene(){assert.equal(hero.visible,false);assert.equal(water.visible,false);renderer.toneMapping=0;renderer.autoClear=false;renderer.xr.enabled=false;throw new Error('capture failure');}dispose(){disposed++;}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});assert.throws(()=>capture(renderer,scene,[hero],{exclude:[hero]}),/capture failure/);assert.equal(hero.visible,true);assert.equal(water.visible,false);assert.equal(renderer.toneMapping,3);assert.equal(renderer.autoClear,true);assert.equal(renderer.xr.enabled,true);assert.equal(renderer.shadowMap.needsUpdate,true);assert.equal(sun.shadow.needsUpdate,true);assert.equal(disposed,1);
});
test('one room capture is shared only by selected materials and is applied after capture',()=>{
 const scene=new T.Scene(),root=new T.Group(),material=new T.MeshStandardMaterial(),outside=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial());root.add(new T.Mesh(new T.BoxGeometry(),material),new T.Mesh(new T.BoxGeometry(),material));scene.add(root,outside);const target={texture:new T.Texture(),dispose(){}};let count=0;
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:false},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};
 class PMREMGenerator{fromScene(s,sigma,near,far,options){count++;assert.equal(material.envMap,null);assert.equal(s,scene);assert.equal(options.size,128);assert.deepEqual(options.position.toArray(),[0,2.8,-6.8]);return target;}dispose(){}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});const result=capture(renderer,scene,[root]);assert.equal(count,1);assert.equal(result.stats.materials,1);assert.equal(material.envMap,target.texture);assert.equal(outside.material.envMap,null);
});
test('side-aisle paving can share one probe while retaining its own projection bounds',()=>{
 const scene=new T.Scene(),floor=new T.Group(),altar=new T.Group();
 const stone=new T.MeshStandardMaterial({roughness:.36,metalness:0}),gold=new T.MeshStandardMaterial({metalness:1});
 const normal=new T.Texture(),roughness=new T.Texture();stone.normalMap=normal;stone.roughnessMap=roughness;
 floor.add(new T.Mesh(new T.BoxGeometry(),stone));altar.add(new T.Mesh(new T.BoxGeometry(),gold));scene.add(floor,altar);
 const target={texture:new T.Texture(),dispose(){}};let count=0;
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:false},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};
 class PMREMGenerator{fromScene(){count++;return target;}dispose(){}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});
 const bounds={min:new T.Vector3(-6.14,.939,-10.74),max:new T.Vector3(6.14,4.3,-3.46)};
 const result=capture(renderer,scene,[altar,floor],{projections:new Map([[floor,bounds]])});
 assert.equal(count,1);assert.equal(result.stats.materials,2);assert.equal(stone.envMap,gold.envMap);assert.equal(stone.normalMap,normal);assert.equal(stone.roughnessMap,roughness);assert.equal(stone.roughness,.36);assert.equal(stone.metalness,0);
 const shaders=[stone,gold].map(m=>{const s={uniforms:{},vertexShader:'#include <worldpos_vertex>',fragmentShader:'#include <envmap_physical_pars_fragment>'};m.onBeforeCompile(s);return s;});
 assert.equal(shaders[0].uniforms.hallProbeMin.value,bounds.min);assert.equal(shaders[0].uniforms.hallProbeMax.value,bounds.max);assert.equal(shaders[1].uniforms.hallProbeMin.value.x,-5.1);
 const metadata=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary-floor.json',import.meta.url)));const [xmin,xmax,ymin,ymax,zmin,zmax]=metadata.boundsNative;
 const projected=new T.Box3(bounds.min,bounds.max);for(const x of [xmin,xmax])for(const y of [ymin,ymax])for(const z of [zmin,zmax])assert.ok(projected.containsPoint(new T.Vector3(x,z,-y)));
});
test('floor reflection includes visible furnishings while other materials and diffuse lighting keep the original probe',()=>{
 const scene=new T.Scene(),floor=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial()),hero=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial()),hiddenHero=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial()),water=new T.Mesh();water.isWater=true;hiddenHero.visible=false;scene.add(floor,hero,hiddenHero,water);
 const targets=[0,1].map(()=>({texture:new T.Texture({width:384,height:512}),dispose(){this.disposed=true;}}));let captures=0;
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:false},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};
 class PMREMGenerator{fromScene(){assert.equal(hero.visible,captures===1);assert.equal(hiddenHero.visible,false);assert.equal(water.visible,false);assert.equal(floor.material.envMap,null);return targets[captures++];}dispose(){}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});const result=capture(renderer,scene,[floor,hero],{exclude:[hero,hiddenHero],specularRoots:[floor]});
 assert.equal(captures,2);assert.equal(result.stats.specularMaterials,1);assert.equal(hero.visible,true);assert.equal(hiddenHero.visible,false);assert.equal(water.visible,true);assert.equal(floor.material.envMap,hero.material.envMap);
 const shader={uniforms:{},vertexShader:'#include <worldpos_vertex>',fragmentShader:'#include <envmap_physical_pars_fragment>'};floor.material.onBeforeCompile(shader);assert.equal(shader.uniforms.hallSpecularMap.value,targets[1].texture);assert.ok(shader.fragmentShader.includes('textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 )'));assert.ok(shader.fragmentShader.includes('textureCubeUV( hallSpecularMap, envMapRotation * hallProbeDirection( reflectVec ), roughness )'));
 const heroShader={uniforms:{},vertexShader:'#include <worldpos_vertex>',fragmentShader:'#include <envmap_physical_pars_fragment>'};hero.material.onBeforeCompile(heroShader);assert.equal(heroShader.uniforms.hallSpecularMap,undefined);
 result.dispose();assert.ok(targets.every(t=>t.disposed));
});
test('a failed furnished capture releases the first atlas and restores original visibility',()=>{
 const scene=new T.Scene(),floor=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial()),hero=new T.Group();scene.add(floor,hero);let calls=0,disposed=0;
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:false},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};
 class PMREMGenerator{fromScene(){if(++calls===2)throw new Error('second capture failed');return {texture:new T.Texture(),dispose(){disposed++;}};}dispose(){}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});assert.throws(()=>capture(renderer,scene,[floor],{exclude:[hero],specularRoots:[floor]}),/second capture/);assert.equal(disposed,1);assert.equal(hero.visible,true);assert.equal(floor.material.envMap,null);
});
test('specular atlases reject mismatched CubeUV dimensions before modifying the material',()=>{
 const material=new T.MeshStandardMaterial();assert.throws(()=>applyHallReflection(material,new T.Texture({width:384,height:512}),{specularMap:new T.Texture({width:768,height:1024})}),/share CubeUV dimensions/);assert.equal(material.envMap,null);
});

test('new caisson finish receives indoor reflection without changing shared altar gilding projection',()=>{
 const scene=new T.Scene(),altar=new T.Group(),ceiling=new T.Group();
 const gold=new T.MeshStandardMaterial({metalness:1}),lacquer=new T.MeshPhysicalMaterial({clearcoat:.52,clearcoatRoughness:.23,roughness:.32});
 altar.add(new T.Mesh(new T.BoxGeometry(),gold));ceiling.add(new T.Mesh(new T.BoxGeometry(),gold),new T.Mesh(new T.BoxGeometry(),lacquer));scene.add(altar,ceiling);
 const target={texture:new T.Texture(),dispose(){}};let captures=0;
 const renderer={toneMapping:3,autoClear:true,xr:{enabled:false},shadowMap:{needsUpdate:false},getRenderTarget:()=>null,getActiveCubeFace:()=>0,getActiveMipmapLevel:()=>0,setRenderTarget:()=>{}};
 class PMREMGenerator{fromScene(){captures++;return target;}dispose(){}}
 const capture=new Function('THREE',code+';return captureHallReflections')({...T,PMREMGenerator});
 const vault={min:new T.Vector3(-5.18,1.07,-10.43),max:new T.Vector3(5.18,5.85,-3.6)};
 const result=capture(renderer,scene,[altar,ceiling],{projections:new Map([[ceiling,vault]])});
 assert.equal(captures,1);assert.equal(result.stats.materials,2);assert.equal(lacquer.envMap,target.texture);assert.equal(lacquer.clearcoat,.52);assert.equal(lacquer.roughness,.32);
 for(const [material,expectedHeight]of [[gold,4.3],[lacquer,5.85]]){const shader={uniforms:{},vertexShader:'#include <worldpos_vertex>',fragmentShader:'#include <envmap_physical_pars_fragment>'};material.onBeforeCompile(shader);assert.equal(shader.uniforms.hallProbeMax.value.y,expectedHeight);}
});
