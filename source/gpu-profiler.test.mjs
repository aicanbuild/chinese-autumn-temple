import test from 'node:test';import assert from 'node:assert/strict';import {createGpuProfiler,profileGpuMethod} from '../dist/gpu-profiler.js';
function driver(){
 const ext={TIME_ELAPSED_EXT:1,QUERY_COUNTER_BITS_EXT:2,GPU_DISJOINT_EXT:3};let active=null,created=0,deleted=0,reads=0;
 const gl={QUERY_RESULT_AVAILABLE:4,QUERY_RESULT:5,available:true,disjoint:false,lost:false,getExtension:()=>ext,getQuery:()=>64,isContextLost(){return this.lost;},getParameter(){return this.disjoint;},createQuery(){return {id:++created};},beginQuery(type,q){assert.equal(active,null);active=q;},endQuery(){assert.ok(active);active=null;},getQueryParameter(q,type){if(type===4)return this.available;assert.equal(this.available,true);reads++;return 1e6;},deleteQuery(){deleted++;}};
 return {gl,get created(){return created;},get deleted(){return deleted;},get reads(){return reads;},get active(){return active;}};
}
test('one selected scope remains inclusive without nested queries',()=>{
 const d=driver(),p=createGpuProfiler(d.gl,{interval:100,targets:['main']});p.beginFrame();const main=p.begin('main'),reflection=p.begin('reflection');reflection();main();p.endFrame();assert.equal(d.active,null);assert.equal(d.created,1);assert.equal(d.reads,0);p.beginFrame();assert.equal(p.stats.sampledFrames,1);assert.equal(p.stats.stages.main.meanMs,1);assert.equal(p.stats.stages.reflection,undefined);assert.equal(d.deleted,1);
});
test('unavailable results never block or grow beyond the pending frame limit',()=>{
 const d=driver(),p=createGpuProfiler(d.gl,{interval:1,maxPendingFrames:2,targets:['main']});d.gl.available=false;
 for(let i=0;i<20;i++){p.beginFrame();const end=p.begin('main');end();p.endFrame();}
 assert.equal(d.reads,0);assert.equal(d.created,2);assert.equal(p.stats.pendingFrames,2);d.gl.available=true;p.beginFrame();assert.equal(p.stats.sampledFrames,2);assert.equal(d.deleted,2);p.endFrame();
});
test('disjoint and context-loss frames are discarded and their queries released',()=>{
 const d=driver(),p=createGpuProfiler(d.gl,{interval:1,targets:['main']});p.beginFrame();p.begin('main')();p.endFrame();d.gl.disjoint=true;p.beginFrame();assert.equal(p.stats.sampledFrames,0);assert.equal(p.stats.discardedFrames,1);assert.equal(d.deleted,1);p.endFrame();d.gl.disjoint=false;
 p.beginFrame();p.begin('main')();p.endFrame();d.gl.lost=true;p.beginFrame();assert.equal(p.stats.discardedFrames,2);assert.equal(d.deleted,2);
});
test('wrapping preserves receiver and return value and closes timing scopes on errors',()=>{
 const d=driver(),p=createGpuProfiler(d.gl,{interval:1,targets:['main']}),target={value:7,render(x){if(x<0)throw new Error('draw failed');return this.value+x;}};profileGpuMethod(p,target,'render','main');assert.equal(target.render(3),10);p.beginFrame();assert.throws(()=>target.render(-1),/draw failed/);p.endFrame();assert.equal(d.active,null);p.dispose();assert.equal(d.deleted,1);
});
test('unsupported timer extensions preserve ordinary rendering without queries',()=>{
 const d=driver();d.gl.getExtension=()=>null;const p=createGpuProfiler(d.gl);p.beginFrame();p.begin('main')();p.endFrame();assert.equal(p.stats.supported,false);assert.equal(d.created,0);p.dispose();
});
