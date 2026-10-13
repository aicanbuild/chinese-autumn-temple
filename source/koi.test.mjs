import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {sampleKoiMotion} from '../dist/koi-motion.js';
import {applyKoiReaction} from '../dist/koi-reaction.js';
const data=fs.readFileSync(new URL('../dist/assets/koi/koi.glb',import.meta.url));
const gltf=JSON.parse(data.subarray(20,20+data.readUInt32LE(12)).toString());
test('all four Blender koi variants contain body, mouth, gill and fin geometry',()=>{
 for(const kind of ['kohaku','sanke','yamabuki','platinum']){
  const root=gltf.nodes.find(n=>n.name===`Koi_${kind}`);assert.ok(root,kind);
  const parts=root.children.map(i=>gltf.nodes[i].name).join(' ');
  for(const name of ['Body','Caudal','Pectoral','Pelvic','Dorsal','Pupil','Sensory','Operculum','Mouth'])assert.ok(parts.includes(name),`${kind}: ${name}`);
 }
 assert.ok(data.length<4*1024*1024,'detailed fish remain a compact web asset');
});
test('the caudal fin is vertical and the body has a smooth, dense silhouette',()=>{
 const tail=gltf.meshes.find(m=>m.name.startsWith('Caudal'));
 const bounds=gltf.accessors[tail.primitives[0].attributes.POSITION];
 const size=bounds.max.map((v,i)=>v-bounds.min[i]);
 assert.ok(size[1]>.4&&size[0]<.025,`vertical tail bounds: ${size}`);
 const body=gltf.meshes.find(m=>m.name.startsWith('Body'));
 assert.ok(gltf.accessors[body.primitives[0].attributes.POSITION].count>3000);
});
test('animated routes remain inside the pond and beneath the surface',()=>{
 const source=fs.readFileSync(new URL('../dist/koi.js',import.meta.url),'utf8');
 const fn=new Function('sampleKoiMotion','applyKoiReaction',`${source.slice(source.indexOf('export function updateKoi')).replace('export ','')};return updateKoi;`)(sampleKoiMotion,applyKoiReaction);
 const group={position:{set(x,y,z){this.x=x;this.y=y;this.z=z;}},rotation:{set(x,y,z){this.x=x;this.y=y;this.z=z;}}};
 const fish=[{group,time:{value:0},phase:1,speed:.09,rx:8.1,rz:4.5,depth:-.33,drift:2}];
 for(let t=0;t<1200;t+=.5){
  fn(fish,t);const p=group.position;
  assert.ok(Number.isFinite(group.rotation.y));assert.ok((p.x/11.5)**2+((p.z-5.8)/6.9)**2<.9);
  assert.ok(p.y<-.25&&p.y>-.8);
 }
});
