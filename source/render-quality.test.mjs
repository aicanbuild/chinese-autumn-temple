import test from 'node:test';
import assert from 'node:assert/strict';
import {createRenderQuality} from '../dist/render-quality.js';
test('quality recovers after sustained headroom but never exceeds device resolution',()=>{
 const q=createRenderQuality(2);assert.equal(q.pixelRatio,1.6);assert.equal(q.sample(48,5),1.35);assert.equal(q.sample(47,18),1.1);
 assert.equal(q.sample(19,31),null);assert.equal(q.sample(20,36),1.35);
 assert.equal(q.sample(21,49),null);assert.equal(q.sample(23,55),1.6);assert.equal(q.sample(16,70),null);assert.equal(q.sample(16,76),null);
 const low=createRenderQuality(1);assert.equal(low.pixelRatio,1);assert.equal(low.sample(70,1),null);assert.equal(low.sample(15,50),null);assert.equal(low.sample(15,60),null);
});
test('thresholds and cooldown prevent resolution oscillation',()=>{
 const q=createRenderQuality(2);q.sample(50,10);assert.equal(q.sample(55,11),null);assert.equal(q.sample(20,22),null);assert.equal(q.sample(29,29),null);assert.equal(q.sample(24,36),null);assert.equal(q.sample(35,43),null);assert.equal(q.pixelRatio,1.35);assert.equal(q.sample(NaN,55),null);
});
