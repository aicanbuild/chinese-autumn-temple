import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const streamCode=fs.readFileSync(new URL('../dist/temple-stream.js',import.meta.url),'utf8');
const streamCore=streamCode.slice(streamCode.indexOf('export const STREAM_START'),streamCode.indexOf('export function installTempleStream')).replaceAll('export ','');
const {streamContains}=new Function(streamCore+';return {streamContains};')();
const source=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8');
const pool=source.slice(source.indexOf('function poolAt('),source.indexOf('function spawnLeaf('));
const walk=source.slice(source.indexOf('function walkGround('),source.indexOf('function moveWalk('));
const {walkGround,surfaceAt}=new Function('gardenGround','streamContains',`let handwash=null; ${pool}\n${walk}\nreturn {walkGround,surfaceAt};`)(null,streamContains);
test('a continuous route crosses the full bridge and reaches the open temple entry',()=>{
 for(let z=13.3;z>=-7.4;z-=.025)assert.notEqual(walkGround(0,z),null,`Blocked central route at z=${z}`);
});
test('the pond cannot be entered beside the bridge',()=>{
 for(const x of[-5,-2,2,5])for(const z of[2,5,8])assert.equal(walkGround(x,z),null);
});
test('walls, pillars, altar and outer boundary are solid',()=>{
 for(const [x,z]of[[5.4,-7],[3,-5.1],[-2.8,-3.85],[0,-8.2],[0,-10.3],[16,0],[0,18]])assert.equal(walkGround(x,z),null,`${x},${z}`);
});
test('restored porch columns and guardian plinths are solid without blocking the entry',()=>{
 for(const [x,z] of [[-11.4,-8.5],[11.6,-10],[6.12,-6],[-6.12,-6]])assert.equal(walkGround(x,z),null);
 for(const x of [-3.6,3.6])assert.equal(walkGround(x,-2.25),null);
 for(const x of [-2.65,2.65])assert.equal(walkGround(x,-2.35),null);
 for(const x of [-1,0,1])assert.notEqual(walkGround(x,-2.25),null);
});
test('sweep plane agrees with the bridge arch and temple platform',()=>{
 assert.ok(surfaceAt(0,5.75)>1.1);assert.equal(surfaceAt(0,-6),1.07);
 assert.ok(surfaceAt(4,5)<0);assert.equal(surfaceAt(4,-2),.505);
});
test('packaged binary scene and critical assets exist',()=>{
 for(const file of['temple.glb','garden.json','maple-leaf.png','ginkgo-leaf.png','water-normal-0.jpg','water-normal-1.jpg'])assert.ok(fs.statSync(new URL(`../dist/assets/${file}`,import.meta.url)).size>100);
 const glb=fs.readFileSync(new URL('../dist/assets/temple.glb',import.meta.url));assert.equal(glb.toString('utf8',0,4),'glTF');
 const json=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString());assert.ok(json.meshes.length>=12);assert.ok(json.extensionsUsed.includes('KHR_draco_mesh_compression'));
 assert.ok(glb.length<25*1024*1024,'single web asset stays under 25 MiB');
});

test('leaves and broom meet actual individual bridge boards within two millimetres',()=>{
 for(let j=0;j<71;j++){const z=12.4-j*.188,top=.52+.61*Math.sin(j*.188/13.3*Math.PI)+.07;assert.ok(Math.abs(surfaceAt(0,z)-top)<.00201);}
});
