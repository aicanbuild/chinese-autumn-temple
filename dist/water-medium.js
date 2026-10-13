// Authored RGB extinction per metre, shared by sun-to-receiver and
// receiver-to-interface travel through the same homogeneous pond water.
export const POND_EXTINCTION=Object.freeze([.55,.18,.095]);
export function pondTransmittanceGLSL(){return `
 vec3 pondBeamTransmittance(float distanceMeters){
  return exp(-vec3(${POND_EXTINCTION.join(',')})*max(distanceMeters,0.));
 }`;}
