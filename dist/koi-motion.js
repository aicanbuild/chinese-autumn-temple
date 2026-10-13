// Analytic motion keeps a fish's position, tangent and tail phase coherent at any frame rate.
export function sampleKoiMotion(f,t,out={}){
 const s=Math.sin,c=Math.cos,school=Number.isInteger(f.schoolIndex),lane=school?f.schoolIndex%2:0;
 const cycle=(school?.19:.29)*t+f.drift,effort=.5+.5*(school?c(cycle):s(cycle));
 const cycleIntegral=school?(s(cycle)-s(f.drift))/.19:(c(f.drift)-c(cycle))/.29;
 const travel=.86*t+.14*cycleIntegral,offset=f.tailOffset??f.phase;
 const a=school?f.phase+(lane?.046:.058)*t+.02*(s(cycle)-s(f.drift))+.008*(s(.071*t+offset)-s(offset)):f.speed*travel+f.phase;
 const av=school?(lane?.046:.058)+.0038*c(cycle)+.000568*c(.071*t+offset):f.speed*(.86+.14*s(cycle));
 const aa=school?-.000722*s(cycle)-.000040328*s(.071*t+offset):f.speed*.14*.29*c(cycle);
 const u=.041*t+(school?lane:f.drift),v=.037*t+(school?lane:f.drift);
 // The Blender bridge has 21 cm piers at x=±1.04 and z=1.4+2.6*j.
 // Rounded rectangular routes pass through its gaps. Broad, gradual bends
 // let the complete fish clear the timbers without a sudden evasive turn.
 // The two nested school routes cannot overtake within a lane: individual
 // phase variation is bounded, rather than accumulating into collisions.
 const nearGap=school?(lane?2.2:3.2):2.7,farGap=school?(lane?10.5:7.9):(f.rz>3.5?10.5:7.9);
 const center=(nearGap+farGap)/2+(school?0:.10*s(f.drift+f.phase));
 const driftX=school?.08:.24,driftZ=school?.025:.08;
 const rx=(school?(lane?8.3:5.0):Math.max(4.2,f.rx))+driftX*s(u),rz=(farGap-nearGap)/2+driftZ*c(v);
 const rxv=driftX*.041*c(u),rzv=-driftZ*.037*s(v);
 const rxa=-driftX*.041*.041*s(u),rza=-driftZ*.037*.037*c(v);
 const ca=c(a),sa=s(a),r=Math.sqrt(1+ca*ca+ca**4);
 const g=sa*r,ga=3*ca**5/r,gaa=-15*ca**4*sa/r+3*ca**6*sa*(1+2*ca*ca)/r**3;
 const dx=rxv*ca-rx*sa*av,dz=rzv*g+rz*ga*av;
 const ax=rxa*c(a)-2*rxv*s(a)*av-rx*c(a)*av*av-rx*s(a)*aa;
 const az=rza*g+2*rzv*ga*av+rz*gaa*av*av+rz*ga*aa;
 const speed=Math.hypot(dx,dz),yawRate=(dz*ax-dx*az)/(speed*speed);
 const scale=f.group?.scale?.x??1,cadence=2.2+f.speed*(f.rx+f.rz)*.9/scale;
 const depthWeight=Math.max(0,Math.min(1,(-f.depth-.33)/.25));
 const depth=school?(lane?-.565-.025*depthWeight:-.37-.035*depthWeight):f.depth;
 const heave=school?.014:.035,heaveRate=school?.31:.42;
 out.x=rx*ca;out.y=depth+heave*s(heaveRate*t+f.drift);out.z=center+rz*g;
 out.yaw=Math.atan2(dx,dz);out.pitch=-Math.atan2(heave*heaveRate*c(heaveRate*t+f.drift),speed);
 out.roll=Math.max(-.045,Math.min(.045,-yawRate*.18));
 out.tailPhase=cadence*(.775*t+.225*cycleIntegral)+(f.tailOffset??f.phase);
 out.tailAmplitude=.035+.065*effort;
 out.turnBend=Math.max(-.16,Math.min(.16,.98*scale*yawRate/speed));
 out.finPhase=t*(1.4+f.speed*7)+(f.tailOffset??f.drift);
 out.speed=speed;out.effort=effort;return out;
}
