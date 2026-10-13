// Short inharmonic shell modes with a tiny broadband wooden contact transient.
export function playWoodenFish(ctx,master,reverb){
 const t=ctx.currentTime,bus=ctx.createGain();bus.gain.value=.72;bus.connect(master);
 const wet=ctx.createGain();wet.gain.value=.075;bus.connect(wet);if(reverb)wet.connect(reverb);
 for(const [f,a,decay]of [[520,.33,.16],[846,.19,.095],[1378,.075,.052],[2030,.025,.032]]){
  const o=ctx.createOscillator(),g=ctx.createGain();o.frequency.setValueAtTime(f,t);o.frequency.exponentialRampToValueAtTime(f*.985,t+.045);g.gain.setValueAtTime(.00001,t);g.gain.linearRampToValueAtTime(a,t+.0015);g.gain.exponentialRampToValueAtTime(.00001,t+decay);o.connect(g).connect(bus);o.start(t);o.stop(t+decay+.02);
 }
 const buffer=ctx.createBuffer(1,Math.ceil(ctx.sampleRate*.024),ctx.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*Math.exp(-i/(ctx.sampleRate*.003))*.16;
 const src=ctx.createBufferSource(),filter=ctx.createBiquadFilter();src.buffer=buffer;filter.type='bandpass';filter.frequency.value=1650;filter.Q.value=.65;src.connect(filter).connect(bus);src.start(t);src.onended=()=>{src.disconnect();filter.disconnect();};setTimeout(()=>{bus.disconnect();wet.disconnect();},800);
}
