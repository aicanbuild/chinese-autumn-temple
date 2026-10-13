// Optional development diagnostics. Results are collected asynchronously; no
// gl.finish, blocking readback, or simultaneous TIME_ELAPSED queries are used.
export function createGpuProfiler(gl,{interval=3,maxPendingFrames=8,windowSize=144,targets=['frame']}={}){
 const ext=gl.getExtension('EXT_disjoint_timer_query_webgl2');
 const supported=!!ext&&gl.getQuery(ext.TIME_ELAPSED_EXT,ext.QUERY_COUNTER_BITS_EXT)>0;
 const pending=[],history=[];let frame=null,active=null,count=0,discarded=0,targetIndex=0;
 function close(){if(active){gl.endQuery(ext.TIME_ELAPSED_EXT);frame.segments.push(active);active=null;}}
 function open(name){const query=gl.createQuery();if(query){gl.beginQuery(ext.TIME_ELAPSED_EXT,query);active={name,query};}}
 function clear(){for(const f of pending)for(const s of f.segments)gl.deleteQuery(s.query);discarded+=pending.length;pending.length=0;}
 function poll(){
  if(!supported)return;
  if(gl.isContextLost()){clear();return;}
  if(gl.getParameter(ext.GPU_DISJOINT_EXT)){clear();return;}
  while(pending.length){const f=pending[0];if(!f.segments.every(s=>gl.getQueryParameter(s.query,gl.QUERY_RESULT_AVAILABLE)))break;
   pending.shift();const totals={};let valid=true;
   for(const s of f.segments){const ms=gl.getQueryParameter(s.query,gl.QUERY_RESULT)/1e6;gl.deleteQuery(s.query);valid=valid&&Number.isFinite(ms)&&ms>=0;totals[s.name]=(totals[s.name]??0)+ms;}
   if(valid){history.push(totals);if(history.length>windowSize)history.shift();}else discarded++;
  }
 }
 return {
  beginFrame(){poll();frame=supported&&!gl.isContextLost()&&count++%interval===0&&pending.length<maxPendingFrames?{segments:[],target:targets[targetIndex++%targets.length],used:false}:null;},
  // One scope per sampled frame avoids query-boundary overhead contaminating
  // every stage on tile-based GPUs. Parent scopes are inclusive, never additive.
  begin(name){if(!frame||frame.used||name!==frame.target)return ()=>{};frame.used=true;open(name);let done=false;return()=>{if(done)return;done=true;close();};},
  endFrame(){if(!frame)return;close();if(frame.segments.length)pending.push(frame);frame=null;},
  dispose(){close();if(frame){pending.push(frame);frame=null;}clear();},
  get stats(){const keys=[...new Set(history.flatMap(Object.keys))],stages={};for(const key of keys){const values=history.filter(h=>key in h).map(h=>h[key]).sort((a,b)=>a-b);stages[key]={samples:values.length,meanMs:values.reduce((a,b)=>a+b,0)/values.length,medianMs:values[Math.floor(values.length/2)],maxMs:values.at(-1)};}return {supported,method:'one inclusive scope per sampled frame',sampledFrames:history.length,pendingFrames:pending.length,discardedFrames:discarded,stages};}
 };
}

export function profileGpuMethod(profiler,target,key,name){
 const original=target[key];target[key]=function(...args){const end=profiler.begin(name);try{return original.apply(this,args);}finally{end();}};
}
