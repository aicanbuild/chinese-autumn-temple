import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
import {IncenseCycle} from '../dist/ritual-state.js';

const load=name=>fs.readFileSync(new URL(`../dist/${name}.js`,import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createCandlelight}=new Function('THREE',load('candlelight')+';return {createCandlelight};')(THREE);
const layout=JSON.parse(fs.readFileSync(new URL('../dist/assets/sanctuary.json',import.meta.url)));
const element={classList:{add(){},remove(){}},dataset:{}};
const createRituals=new Function('THREE','document','IncenseCycle','createWoodenFish','createTempleBell','createIncenseSmoke','mergeGeometries',load('rituals')+';return createRituals;')(
 THREE,{querySelector:()=>element},IncenseCycle,
 ()=>({held:false,stats:{},update(){},putBack(){}}),()=>({update(){},ring(){},rings:0,parts:0}),()=>({update(){}}),()=>{throw new Error('Unexpected broom geometry');}
);

test('actual room entry, four ray-picked candles, exit and re-entry reset the same candle system',()=>{
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(43,1.5,.09,420);
 camera.position.set(14,8.5,26);
 const controls={target:new THREE.Vector3(0,2,0),minDistance:5,maxDistance:65,minPolarAngle:.2,maxPolarAngle:1.4,screenSpacePanning:false,update(){}};
 const candles=createCandlelight(layout,scene);
 const rituals=createRituals({scene,model:new THREE.Group(),camera,controls,broom:new THREE.Group(),candlePositions:layout.flames,onEnter:()=>candles.enter(),onLeave:()=>candles.leave()});
 for(let visit=0;visit<3;visit++){
  rituals.enter();assert.equal(rituals.inside,true);assert.deepEqual(candles.stats.lit,[false,false,false,false]);
  assert.equal(rituals.pick(new THREE.Vector2(),false),null,'camera transition does not accept clicks');
  rituals.update(1,visit,{sweeping:false});camera.updateMatrixWorld(true);
  for(let i=0;i<4;i++){
   const [x,y,z]=layout.flames[i],point=new THREE.Vector3(x,y-.035,z).project(camera);
   assert.ok(Math.abs(point.x)<1&&Math.abs(point.y)<1,'candle is in the entry view');
   const action=rituals.pick(new THREE.Vector2(point.x,point.y),false);
   assert.equal(action,`candle-${i}`);assert.equal(candles.light(Number(action.slice(7))),true);candles.update(visit+i,1);
  }
  assert.equal(candles.strength,1);assert.equal(candles.stats.count,4);
  rituals.enter();assert.equal(candles.stats.count,4,'redundant enter call during a visit does not extinguish candles');
  rituals.leave();assert.equal(rituals.inside,false);assert.equal(candles.stats.count,0);assert.equal(candles.strength,0);
  assert.ok(candles.flames.every(f=>!f.visible));assert.ok(candles.lights.every(l=>l.intensity===0));
 }
});
