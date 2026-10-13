import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const ritual=fs.readFileSync(new URL('../dist/rituals.js',import.meta.url),'utf8');
const extractRegion=new Function('THREE',ritual.slice(ritual.indexOf('export function extractRegion'),ritual.indexOf('export function createRituals')).replace('export ','')+';return extractRegion;')(THREE);
const source=fs.readFileSync(new URL('../dist/sanctuary.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const candleSource=fs.readFileSync(new URL('../dist/candlelight.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createCandlelight,finishCandleWax}=new Function('THREE',candleSource+';return {createCandlelight,finishCandleWax}')(THREE);
const {installSanctuary,sanctuaryRegionContains}=new Function('THREE','extractRegion','createCandlelight','finishCandleWax',source+';return {installSanctuary,sanctuaryRegionContains};')(THREE,extractRegion,createCandlelight,finishCandleWax);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary.json',import.meta.url)));
test('interior replacement preserves boundary-crossing architecture and the accepted sculpture',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene(),asset=new THREE.Group();
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([-4,2,-10.2,-3,2,-10.2,-3.5,3,-10.2, -4,2,-10.2,-3,2,-10.2,-3.5,5,-10.2, 0,2,-8.6,.5,2,-8.6,0,3,-8.6],3));
 const material=new THREE.MeshStandardMaterial();material.name='Satin gilded bronze';root.add(new THREE.Mesh(g,material));
 const result=installSanctuary(root,asset,layout,scene);assert.equal(result.removedTriangles,1);assert.equal(g.index.count,6);assert.equal(result.flames,4);assert.ok(scene.children.includes(asset));
 assert.ok(result.candles.flames.every(f=>!f.visible));result.candles.enter();for(let i=0;i<4;i++)result.candles.light(i);
 for(let t=0;t<600;t+=.1)result.update(t,.1);
 assert.equal(scene.children.filter(o=>o.name==='Red candle flame'&&o.visible).length,4);
 assert.ok(!layout.removeRegionsNative.some(r=>sanctuaryRegionContains(new THREE.Vector3(0,2.6,-8.6),r)));
});
test('sanctuary asset carries original mural UVs, modest material batches and a recessed ceiling',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));assert.ok(b.length<25*1024*1024);
 const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));assert.ok(d.meshes.length<=21);assert.equal(d.images.length,22);assert.ok(d.images.every(i=>i.bufferView!==undefined));
 const mural=d.materials.findIndex(m=>m.name.includes('original mineral mural'));const primitives=d.meshes.flatMap(m=>m.primitives).filter(p=>p.material===mural);
 assert.equal(primitives.length,1);assert.ok(primitives[0].attributes.TEXCOORD_0!==undefined);assert.equal(d.accessors[primitives[0].indices].count,12);
 assert.equal(layout.preservedSculpture,38);assert.equal(layout.preservedIncense,196);assert.ok(layout.caissonTop>5.5);assert.equal(layout.flames.length,4);
});
test('crafted finishes preserve tint, non-collapsed UVs and valid PBR factors in portable GLB',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const names=['carved rosewood','oxblood lacquer','hand burnished gold','antique gilt bronze','azurite painted wood','malachite painted wood'];
 for(const name of names){
  const index=d.materials.findIndex(m=>m.name.endsWith(name)),m=d.materials[index],p=m.pbrMetallicRoughness;
  assert.ok(m.normalTexture);
  if(name.endsWith('painted wood')){
   assert.equal(p.metallicFactor,0);assert.equal(p.metallicRoughnessTexture,undefined);assert.ok(p.roughnessFactor>=.6&&p.roughnessFactor<=.8);
   const scale=m.normalTexture.extensions?.KHR_texture_transform?.scale;assert.ok(scale?.every(v=>v>=4&&v<=8));assert.ok(m.normalTexture.scale>0&&m.normalTexture.scale<.1);
  }else assert.ok(p.metallicRoughnessTexture);
  const roughness=p.roughnessFactor??1;assert.ok(roughness>=0&&roughness<=1);
  for(const mesh of d.meshes)for(const prim of mesh.primitives)if(prim.material===index){
   const uv=d.accessors[prim.attributes.TEXCOORD_0];assert.ok(uv&&uv.count>0);
  }
 }
 const lacquer=d.materials.find(m=>m.name.endsWith('oxblood lacquer')).pbrMetallicRoughness;
 for(const [i,value] of [.42,.12,.095,1].entries())assert.ok(Math.abs(lacquer.baseColorFactor[i]-value)<1e-5);assert.ok(lacquer.baseColorTexture);
 assert.equal(layout.dougongClusters,96);assert.equal(layout.surfaceRevision,2);
});

test('lotus bouquets carry real curved petals and peltate leaves with embedded vein maps',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 for(const name of ['living lotus petals','living lotus leaves']){
  const index=d.materials.findIndex(m=>m.name.endsWith(name));assert.ok(index>=0);const m=d.materials[index];assert.equal(m.pbrMetallicRoughness.metallicFactor,0);assert.ok(m.pbrMetallicRoughness.baseColorTexture);assert.ok(m.normalTexture);
  const p=d.meshes.flatMap(m=>m.primitives).filter(p=>p.material===index);assert.equal(p.length,1);assert.ok(p[0].attributes.NORMAL!==undefined&&p[0].attributes.TEXCOORD_0!==undefined);assert.ok(d.accessors[p[0].indices].count>30000);
 }
 assert.deepEqual(layout.lotusBotany,{openFlowers:6,buds:4,peltateLeaves:6,petals:120,stamens:288});
});

test('altar fruit retains scanned apple and original citrus PBR maps in the portable scene',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 for(const name of ['scanned apple offering','textured citrus offering']){
  const i=d.materials.findIndex(m=>m.name.endsWith(name));assert.ok(i>=0);const m=d.materials[i];assert.equal(m.pbrMetallicRoughness.metallicFactor,0);assert.ok(m.normalTexture);assert.ok(m.pbrMetallicRoughness.baseColorTexture);assert.ok(m.pbrMetallicRoughness.metallicRoughnessTexture);
  const primitives=d.meshes.flatMap(m=>m.primitives).filter(p=>p.material===i);assert.equal(primitives.length,1);const p=primitives[0];assert.ok(p.attributes.NORMAL!==undefined&&p.attributes.TEXCOORD_0!==undefined);assert.ok(d.accessors[p.indices].count>=90000);
 }
 assert.deepEqual(layout.fruitDetails,{apples:6,citrus:6,contactGap:.0005});
});

test('sanctuary preserves authored physical coats and exports separate gold leaf textures',()=>{
 const original=new THREE.MeshPhysicalMaterial({clearcoat:.45,clearcoatRoughness:.20});original.name='Sanctuary | oxblood lacquer';
 const asset=new THREE.Group();const mesh=new THREE.Mesh(new THREE.BoxGeometry(),original);asset.add(mesh);
 installSanctuary(new THREE.Group(),asset,layout,new THREE.Scene());
 assert.equal(mesh.material,original);assert.equal(mesh.material.clearcoat,.45);assert.equal(mesh.material.clearcoatRoughness,.20);
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const gold=d.materials.find(m=>m.name.endsWith('hand burnished gold')),bronze=d.materials.find(m=>m.name.endsWith('antique gilt bronze'));
 assert.equal(gold.pbrMetallicRoughness.metallicFactor??1,1);assert.ok(gold.pbrMetallicRoughness.baseColorTexture);
 assert.notEqual(d.textures[gold.normalTexture.index].source,d.textures[bronze.normalTexture.index].source);
 const coat=d.materials.find(m=>m.name.endsWith('oxblood lacquer')).extensions.KHR_materials_clearcoat;
 assert.ok(Math.abs(coat.clearcoatFactor-.45)<1e-5&&Math.abs(coat.clearcoatRoughnessFactor-.20)<1e-5);
});

test('crafted candlesticks retain enamel, four fixed candle origins and physical support metadata',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url));const d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const m=d.materials.find(m=>m.name.endsWith('deep blue cloisonne enamel'));assert.ok(m.normalTexture);assert.equal(m.pbrMetallicRoughness.metallicFactor,0);assert.ok(m.extensions.KHR_materials_clearcoat.clearcoatFactor>.3);
 assert.equal(layout.candlesticks.stands.length,4);assert.equal(layout.candlesticks.parts,248);
 for(const stand of layout.candlesticks.stands){assert.equal(stand.parts,62);assert.ok(Math.abs(stand.candleBase-(stand.positionNative[2]+stand.scale*.9))<1e-9);assert.ok(stand.supportTop<stand.candleBase);}
});
test('long-wall painting is distinct and both mineral murals export metre-scale plaster UVs',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 const rear=d.materials.find(m=>m.name.includes('original mineral mural')),side=d.materials.find(m=>m.name.includes('mineral procession mural'));assert.ok(rear&&side);
 assert.notEqual(rear.pbrMetallicRoughness.baseColorTexture.index,side.pbrMetallicRoughness.baseColorTexture.index);
 for(const m of [rear,side]){assert.equal(m.pbrMetallicRoughness.metallicFactor,0);assert.ok(m.normalTexture);assert.ok(Math.abs(m.normalTexture.scale-.7)<1e-6);assert.equal(m.normalTexture.texCoord,1);assert.equal(m.pbrMetallicRoughness.metallicRoughnessTexture.texCoord,1);const mi=d.materials.indexOf(m),p=d.meshes.flatMap(m=>m.primitives).filter(p=>p.material===mi);assert.equal(p.length,1);assert.ok(p[0].attributes.TEXCOORD_1!==undefined);assert.equal(d.accessors[p[0].indices].count,12);}
 assert.equal(layout.muralRevision,1);assert.equal(layout.muralArtworks,2);
});

test('offering water keeps authored glaze parameters and does not cast an opaque shadow',()=>{
 const asset=new THREE.Group(),material=new THREE.MeshPhysicalMaterial({transparent:true,opacity:.27,roughness:.035,clearcoat:1,ior:1.333});material.name='Sanctuary | clear offering water';const mesh=new THREE.Mesh(new THREE.BoxGeometry(),material);asset.add(mesh);
 installSanctuary(new THREE.Group(),asset,layout,new THREE.Scene());assert.equal(mesh.castShadow,false);assert.equal(mesh.material.depthWrite,false);assert.equal(mesh.material.side,THREE.FrontSide);assert.equal(mesh.material.opacity,.27);assert.equal(mesh.material.ior,1.333);
});
test('seven closed celadon offerings export independent glaze, bare foot and transparent water',()=>{
 const b=fs.readFileSync(new URL('../dist/assets/sanctuary.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
 assert.equal(layout.offeringCups.cups,7);assert.equal(layout.offeringCups.parts,21);assert.equal(layout.offeringCups.supportTop,1.895);
 const glaze=d.materials.find(m=>m.name.includes('jade celadon offering')),foot=d.materials.find(m=>m.name.includes('unglazed celadon foot')),water=d.materials.find(m=>m.name.includes('clear offering water'));
 assert.equal(glaze.pbrMetallicRoughness.metallicFactor,0);assert.ok(glaze.extensions.KHR_materials_clearcoat.clearcoatFactor>.6);assert.ok(foot.pbrMetallicRoughness.roughnessFactor>.75);assert.equal(water.alphaMode,'BLEND');assert.ok(water.pbrMetallicRoughness.baseColorFactor[3]>.2&&water.pbrMetallicRoughness.baseColorFactor[3]<.3);
 for(const m of [glaze,foot,water]){
  const primitive=d.meshes.flatMap(m=>m.primitives).filter(p=>p.material===d.materials.indexOf(m));assert.equal(primitive.length,1);assert.ok(d.accessors[primitive[0].indices].count>1000);
 }
 assert.equal(d.meshes.flatMap(m=>m.primitives).length,22);assert.ok(b.length<25*1024*1024);
});
test('crafted tabletop replaces all twelve legacy gold-block triangles while preserving nearby furniture',()=>{
 const root=new THREE.Group(),gold=new THREE.MeshStandardMaterial();gold.name='Satin gilded bronze';
 const block=new THREE.Mesh(new THREE.BoxGeometry(3.5,.11,1.6),gold);block.position.set(0,1.84,-8.65);root.add(block);
 const wood=new THREE.MeshStandardMaterial();wood.name='Polished ebony cedar';
 const base=new THREE.Mesh(new THREE.BoxGeometry(3.3,.77,1.45),wood);base.position.set(0,1.39,-8.65);root.add(base);
 const side=new THREE.Mesh(new THREE.BoxGeometry(1.1,.14,1.18),wood);side.position.set(2.3,1.875,-8.3);root.add(side);
 const result=installSanctuary(root,new THREE.Group(),layout,new THREE.Scene());assert.equal(result.removedTriangles,12);assert.equal(block.geometry.index.count,0);assert.equal(base.geometry.index.count,36);assert.equal(side.geometry.index.count,36);
 assert.equal(layout.altarTabletop.top,layout.offeringCups.supportTop);assert.equal(layout.altarTabletop.parts,8);assert.equal(layout.altarTabletop.mitredRails,4);
});
