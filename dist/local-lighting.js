import * as THREE from 'three';

// Install before any material is compiled. Three already computes exact zero
// attenuation; avoid the subsequent PBR lobes only in that existing zero case.
export function boundedLocalLighting(chunk){
 if(chunk.includes('// temple: skip zero local light'))return chunk;
 const boundary=chunk.indexOf('#if ( NUM_DIR_LIGHTS');
 if(boundary<0)throw new Error('Unsupported Three lighting chunk');
 let local=chunk.slice(0,boundary);
 const direct='RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );';
 for(const kind of ['Point','Spot']){
  const start=local.indexOf(`get${kind}LightInfo(`),end=local.indexOf(direct,start);
  if(start<0||end<0)throw new Error(`Missing ${kind} light evaluation`);
  const infoEnd=local.indexOf(';',start)+1;
  local=local.slice(0,infoEnd)+'\n\t\tif ( directLight.visible ) {\n'+local.slice(infoEnd,end+direct.length)+'\n\t\t}'+local.slice(end+direct.length);
 }
 return '// temple: skip zero local light\n'+local+chunk.slice(boundary);
}

export function installBoundedLocalLighting(){
 THREE.ShaderChunk.lights_fragment_begin=boundedLocalLighting(THREE.ShaderChunk.lights_fragment_begin);
}
