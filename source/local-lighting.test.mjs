import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/local-lighting.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
const {boundedLocalLighting}=new Function('THREE',code+';return {boundedLocalLighting}')(THREE);
test('local-light guard preserves directional/area/hemisphere lighting and applies once',()=>{
 const original=THREE.ShaderChunk.lights_fragment_begin,guarded=boundedLocalLighting(original),boundary='#if ( NUM_DIR_LIGHTS';
 assert.equal(guarded.slice(guarded.indexOf(boundary)),original.slice(original.indexOf(boundary)));
 assert.equal((guarded.match(/if \( directLight.visible \) \{/g)||[]).length,2);
 assert.equal(boundedLocalLighting(guarded),guarded);assert.throws(()=>boundedLocalLighting(''),/Unsupported/);
});
