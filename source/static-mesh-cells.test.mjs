import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as T from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/static-mesh-cells.js',import.meta.url),'utf8').replace(/^import.*$/gm,'').replaceAll('export function','function');const {createStaticCellCulling}=new Function('THREE',code+';return {createStaticCellCulling}')(T);
function fixture(){const root=new T.Group(),g=new T.TorusKnotGeometry(4,.7,120,16),m=new T.Mesh(g,new T.MeshStandardMaterial());root.add(m);m.position.set(3,2,-5);m.rotation.set(.1,.3,.2);m.scale.set(2,1,3);root.updateMatrixWorld(true);const camera=new T.PerspectiveCamera(50,1,.1,100);camera.position.set(0,2,0);camera.lookAt(0,2,-5);camera.updateMatrixWorld();const c=createStaticCellCulling(root,camera,{cellSize:2,minTriangles:0});return {root,g,m,camera,c};}
function before(f,camera=f.camera){f.m.onBeforeRender(null,f.root,camera,f.g,f.m.material,null);}function after(f,camera=f.camera){f.m.onAfterRender(null,f.root,camera,f.g,f.m.material,null);}
test('visible index subsequence preserves all vertex records and original oriented triangle order, restoring after drawing',()=>{
 const f=fixture(),original=f.g.index,positions=f.g.attributes.position.array.slice();before(f);const selected=Array.from(f.g.index.array.slice(0,f.g.drawRange.count));assert.ok(selected.length>0&&selected.length<original.count);let cursor=0;for(let i=0;i<selected.length;i+=3){while(cursor<original.count&&!(original.getX(cursor)===selected[i]&&original.getX(cursor+1)===selected[i+1]&&original.getX(cursor+2)===selected[i+2]))cursor+=3;assert.ok(cursor<original.count);cursor+=3;}after(f);assert.equal(f.g.index,original);assert.equal(f.g.drawRange.count,Infinity);assert.deepEqual(f.g.attributes.position.array,positions);assert.equal(f.root.children.length,1);
 const updates=f.c.stats.indexUpdates;before(f);after(f);assert.equal(f.c.stats.indexUpdates,updates,'stationary views reuse the uploaded index');
});
test('cell bounds enclose every complete triangle and shadow/other cameras keep the full index',()=>{
 const f=fixture(),entry=f.c.entries[0];for(const run of entry.runs)for(let i=run.start;i<run.start+run.count;i++){const p=new T.Vector3().fromBufferAttribute(f.g.attributes.position,entry.original.getX(i));assert.ok(entry.cells[run.cell].local.containsPoint(p));}
 before(f);after(f);const shadow=new T.PerspectiveCamera();before(f,shadow);assert.equal(f.g.index,entry.original);assert.equal(f.g.drawRange.count,Infinity);after(f,shadow);
 f.g.attributes.position.needsUpdate=true;before(f);assert.equal(f.g.index,entry.original);after(f);
});
test('turning the camera updates selection and disabling culling restores complete drawings',()=>{
 const f=fixture();before(f);const first=f.g.drawRange.count;after(f);f.camera.position.set(100,2,0);f.camera.lookAt(110,2,0);f.camera.updateMatrixWorld();before(f);assert.equal(f.g.drawRange.count,0);after(f);assert.ok(first>0);f.c.enabled=false;before(f);assert.equal(f.g.drawRange.count,Infinity);after(f);
});
test('both callback orders cooperate with existing hall occlusion and restore index/range after every pass',()=>{
 const hallCode=fs.readFileSync(new URL('../dist/hall-occlusion.js',import.meta.url),'utf8').replace(/^import.*$/gm,'').replaceAll('export function','function');const {createHallOcclusion}=new Function('THREE',hallCode+';return {createHallOcclusion}')(T);
 for(const hallFirst of [false,true]){const root=new T.Group(),mesh=new T.Mesh(new T.SphereGeometry(2,32,16),new T.MeshStandardMaterial()),camera=new T.PerspectiveCamera(30,1,.1,50);mesh.position.set(1,0,-6);mesh.userData.waterClipStatic=true;root.add(mesh);root.updateMatrixWorld(true);camera.updateMatrixWorld();let inside=false;
 const installHall=()=>createHallOcclusion(root,camera,[{axis:2,lo:[-10,-10,-2],hi:[10,10,-2]}],{isInside:()=>inside});if(hallFirst)installHall();createStaticCellCulling(root,camera,{cellSize:.5,minTriangles:0});if(!hallFirst)installHall();const f={root,g:mesh.geometry,m:mesh,camera},index=f.g.index;
 for(const hidden of [false,true,false]){inside=hidden;before(f);assert.equal(f.g.drawRange.count===0,hidden);after(f);assert.equal(f.g.index,index);assert.equal(f.g.drawRange.count,Infinity);}
 }
});
