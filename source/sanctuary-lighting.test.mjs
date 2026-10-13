import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const source=fs.readFileSync(new URL('../dist/sanctuary-lighting.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {createSanctuaryLighting}=new Function('THREE',source+';return {createSanctuaryLighting}')(THREE);
test('indoor shadow refresh stays independent of camera frames and preserves pending captures',()=>{
 const lighting=createSanctuaryLighting(new THREE.Scene());assert.equal(lighting.key.shadow.needsUpdate,true);
 lighting.update(0);lighting.key.shadow.needsUpdate=false;
 for(const t of [.016,.033,.2,.499]){lighting.update(t);assert.equal(lighting.key.shadow.needsUpdate,false);}
 lighting.update(.5);assert.equal(lighting.key.shadow.needsUpdate,true);lighting.update(.52);assert.equal(lighting.key.shadow.needsUpdate,true,'pending map must not be cleared before renderer consumes it');
 lighting.key.shadow.needsUpdate=false;lighting.update(1.7);assert.equal(lighting.key.shadow.needsUpdate,true,'recover after a long frame');
});
test('finite indoor light volume covers the altar while shadow memory scales down on small screens',()=>{
 const scene=new THREE.Scene(),lighting=createSanctuaryLighting(scene,{shadowSize:1024});assert.equal(lighting.key.shadow.mapSize.x,1024);assert.equal(lighting.key.castShadow,true);assert.equal(lighting.key.shadow.autoUpdate,false);assert.equal(lighting.key.decay,2);
 const axis=lighting.key.target.position.clone().sub(lighting.key.position).normalize();
 for(const p of [new THREE.Vector3(0,3.7,-8.6),new THREE.Vector3(-2.6,2.2,-7.8),new THREE.Vector3(2.6,2.2,-7.8),new THREE.Vector3(0,1.07,-7)]){
  const delta=p.clone().sub(lighting.key.position);assert.ok(delta.length()<lighting.key.distance);assert.ok(axis.angleTo(delta)<lighting.key.angle);
 }
 assert.ok(lighting.fills.every(l=>!l.castShadow&&l.distance>0));lighting.dispose();assert.equal(scene.children.length,0);
});

test('lighting remains faint before ignition and brightens with each candle without changing exterior lights',()=>{
 const scene=new THREE.Scene(),sun=new THREE.DirectionalLight('white',3.7);scene.add(sun);
 const lighting=createSanctuaryLighting(scene);lighting.setCandleLevel(0);assert.ok(lighting.key.intensity<1);assert.ok(lighting.fills.every(l=>l.intensity<=.12));
 let previous=lighting.key.intensity;for(const level of [.25,.5,.75,1]){lighting.setCandleLevel(level);assert.ok(lighting.key.intensity>previous);previous=lighting.key.intensity;assert.equal(sun.intensity,3.7);}
 assert.equal(lighting.key.intensity,34);assert.deepEqual(lighting.fills.map(l=>l.intensity),[1.3,2.2,3.2,2.2]);
 lighting.setCandleLevel(0);assert.equal(lighting.key.intensity,.65);assert.equal(sun.intensity,3.7);
});
