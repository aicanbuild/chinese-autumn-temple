// Keep the scene at real speed down to 4 fps. Only long stalls are bounded;
// physics/collision steps retain the previous maximum of 45 milliseconds.
export function simulationFrame(seconds){
 const delta=Number.isFinite(seconds)?Math.max(0,Math.min(seconds,.25)):0;
 const steps=Math.max(1,Math.ceil(delta/.045));
 return {delta,steps,step:delta/steps};
}
