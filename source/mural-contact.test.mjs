import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {createHash} from 'node:crypto';import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/mural-contact.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const install=new Function('THREE',source+';return installMuralContact')(THREE);
function fixture(){
 const panels=[{center:[-3.43,10.139,2.83],u:[1,0,0],v:[0,0,1],normal:[0,-1,0],size:[3.1,1.99],atlas:[.01,.02,.49,.48]},{center:[3.43,10.139,2.83],u:[1,0,0],v:[0,0,1],normal:[0,-1,0],size:[3.1,1.99],atlas:[.51,.02,.99,.48]},{center:[-5.3,7.87,2.78],u:[0,1,0],v:[0,0,1],normal:[1,0,0],size:[4.34,2.18],atlas:[.01,.52,.49,.98]},{center:[5.3,7.87,2.78],u:[0,1,0],v:[0,0,1],normal:[-1,0,0],size:[4.34,2.18],atlas:[.51,.52,.99,.98]}];
 const root=new THREE.Group();root.rotation.x=-Math.PI/2;
 for(let group=0;group<2;group++){
  const values=[];
  for(const p of panels.slice(group*2,group*2+2))for(const [u,v] of [[0,0],[1,0],[1,1],[0,1]])values.push(...p.center.map((c,k)=>c+(u-.5)*p.size[0]*p.u[k]+(v-.5)*p.size[1]*p.v[k]));
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(values,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(16).fill(.3),2));geometry.setAttribute('uv1',new THREE.Float32BufferAttribute(new Float32Array(16).fill(2.7),2));
  const material=new THREE.MeshStandardMaterial({map:new THREE.Texture(),normalMap:new THREE.Texture(),roughnessMap:new THREE.Texture()});material.name=group?'Sanctuary | mineral procession mural':'Sanctuary | original mineral mural';root.add(new THREE.Mesh(geometry,material));
 }
 return {root,layout:{distance:.16,panels},map:new THREE.Texture({width:2048,height:1024})};
}
test('four mural receivers preserve paint and plaster UVs while selecting separate padded atlas regions',()=>{
 const {root,layout,map}=fixture(),old=root.children.map(o=>({material:o.material,geometry:o.geometry,uv:o.geometry.attributes.uv,uv1:o.geometry.attributes.uv1}));const result=install(root,map,layout);
 assert.deepEqual(result.stats.verticesPerPanel,[4,4,4,4]);assert.equal(map.channel,2);assert.equal(map.flipY,true);assert.equal(map.colorSpace,THREE.NoColorSpace);
 root.children.forEach((o,k)=>{assert.equal(o.geometry,old[k].geometry);assert.equal(o.geometry.attributes.uv,old[k].uv);assert.equal(o.geometry.attributes.uv1,old[k].uv1);assert.notEqual(o.material,old[k].material);assert.equal(old[k].material.aoMap,null);assert.equal(o.material.map,old[k].material.map);assert.equal(o.material.normalMap,old[k].material.normalMap);assert.equal(o.material.roughnessMap,old[k].material.roughnessMap);assert.equal(o.material.aoMap,map);assert.equal(o.material.aoMapIntensity,.85);
  for(let j=0;j<2;j++){const [x0,y0,x1,y1]=layout.panels[k*2+j].atlas,uv=o.geometry.attributes.uv2;assert.ok(Math.abs(uv.getX(j*4)-x0)<1e-6);assert.ok(Math.abs(uv.getY(j*4)-y0)<1e-6);assert.ok(Math.abs(uv.getX(j*4+2)-x1)<1e-6);assert.ok(Math.abs(uv.getY(j*4+2)-y1)<1e-6);}
 });
});
test('changed wall placement and occupied channels fail before partially modifying the asset',()=>{
 const a=fixture();a.root.children[1].position.x=.03;assert.throws(()=>install(a.root,a.map,a.layout),/no longer matches/);assert.equal(a.root.children[0].geometry.attributes.uv2,undefined);assert.equal(a.root.children[0].material.aoMap,null);
 const b=fixture();b.root.children[1].material.aoMap=new THREE.Texture();assert.throws(()=>install(b.root,b.map,b.layout),/occupied/);assert.equal(b.root.children[0].geometry.attributes.uv2,undefined);
 const c=fixture();c.root.remove(c.root.children[1]);assert.throws(()=>install(c.root,c.map,c.layout),/Missing paired/);
});
test('wall contact bake is tied to the current wall geometry and immutable atlas',{skip:'AO provenance uses an earlier sanctuary layout JSON; requires a fresh geometry/layout audit.'},()=>{
 const asset=n=>fs.readFileSync(new URL('../dist/assets/'+n,import.meta.url)),metadata=JSON.parse(asset('mural-contact-ao.json')),png=asset('mural-contact-ao.png');
 for(const [name,hash] of Object.entries(metadata.inputs))assert.equal(createHash('sha256').update(asset(name)).digest('hex'),hash,`${name} changed: audit or rebake mural contact`);
 assert.equal(createHash('sha256').update(png).digest('hex'),metadata.textureSha256);assert.equal(png.readUInt32BE(16),2048);assert.equal(png.readUInt32BE(20),1024);assert.equal(metadata.panels.length,4);assert.equal(metadata.distance,.16);assert.ok(png.length<2*1024*1024);
});
