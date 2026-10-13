import * as THREE from 'three';

// Keep existing materials and draw batches while replacing the four wax bodies
// and the corresponding wicks with the continuous Blender geometry.
export function installCandleWaxGeometry(root,asset){
 root.updateMatrixWorld(true);asset.updateMatrixWorld(true);const sources=new Map();
 asset.traverse(o=>{if(o.isMesh)sources.set(o.userData.sourceMaterial,o);});let replaced=0;
 root.traverse(o=>{
  if(!o.isMesh)return;const source=sources.get(o.material.name);if(!source)return;
  const transform=new THREE.Matrix4().copy(o.matrixWorld).invert().multiply(source.matrixWorld);
  const geometry=source.geometry.clone().applyMatrix4(transform);geometry.computeBoundingBox();geometry.computeBoundingSphere();
  o.geometry.dispose();o.geometry=geometry;replaced++;
 });
 if(replaced!==2)throw new Error('Missing candle wax or wick replacement');
 return replaced;
}

// Each candle has its own quiet air movement; the flame and its light use the same state.
export function candleMotion(t,phase){
 return new THREE.Vector4(
  .65*Math.sin(t*2.7+phase)+.20*Math.sin(t*7.1+phase*1.7),
  .45*Math.sin(t*3.3+phase*.7)+.15*Math.sin(t*8.9+phase),
  1.+.045*Math.sin(t*6.2+phase)+.022*Math.sin(t*10.7+phase*2),
  1.+.07*Math.sin(t*6.2+phase)+.03*Math.sin(t*10.7+phase*2));
}

export function createCandlelight(layout,scene){
 const flames=[],lights=[],states=[],geometry=new THREE.BoxGeometry(.04,.105,.04).translate(0,.0525,0);
 const lit=layout.flames.map(()=>false),levels={value:new Float32Array(layout.flames.length)};
 let visiting=false;
 layout.flames.forEach(([x,y,z],i)=>{
  const motion={value:candleMotion(0,i*2.31)},material=new THREE.ShaderMaterial({
   transparent:true,depthWrite:false,side:THREE.BackSide,uniforms:{motion},
   vertexShader:`varying vec3 localPoint;varying vec3 localEye;
    void main(){localPoint=position;localEye=(inverse(modelMatrix)*vec4(cameraPosition,1.)).xyz;
     gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
   fragmentShader:`uniform vec4 motion;varying vec3 localPoint;varying vec3 localEye;
    void main(){
     vec3 ray=normalize(localPoint-localEye);
     vec3 safeRay=mix(vec3(-1.),vec3(1.),step(vec3(0.),ray))*max(abs(ray),vec3(.00001));
     vec3 a=(vec3(-.02,0.,-.02)-localEye)/safeRay,b=(vec3(.02,.105,.02)-localEye)/safeRay;
     vec3 lo=min(a,b),hi=max(a,b);float start=max(0.,max(lo.x,max(lo.y,lo.z))),end=min(hi.x,min(hi.y,hi.z));
     if(end<=start)discard;
     float ds=(end-start)/24.,alpha=0.;vec3 radiance=vec3(0.);
     for(int k=0;k<24;k++){
      vec3 p=localEye+ray*(start+(float(k)+.5)*ds);float h=p.y/(.082*motion.z);
      if(h<=0.||h>=1.)continue;
      vec2 center=.003*motion.xy*h*h;
      float radius=.010*pow(sin(h*3.14159265),.65)*(1.-.58*h);
      float radial=length(p.xz-center)/max(radius,.0001);
      float density=exp(-2.*pow(radial,4.))*smoothstep(0.,.035,h)*(1.-smoothstep(.91,1.,h));
      // A darker vapour core and a small blue root sit below the luminous envelope.
      density*=1.-.70*(1.-smoothstep(.25,.70,radial))*(1.-smoothstep(.12,.40,h));
      vec3 fire=mix(vec3(3.8,.80,.075),vec3(5.0,3.2,1.1),1.-smoothstep(.15,1.1,radial));
      fire=mix(vec3(.16,.38,1.1),fire,smoothstep(.015,.14,h));
      float opacity=1.-exp(-density*135.*ds);
      radiance+=(1.-alpha)*opacity*fire*motion.w;alpha+=(1.-alpha)*opacity;
     }
     if(alpha<.002)discard;
     gl_FragColor=vec4(radiance/max(alpha,.0001),alpha);
     #include <tonemapping_fragment>
     #include <colorspace_fragment>
    }`
  });
  const flame=new THREE.Mesh(geometry,material);
  // Original layout is 8 mm above the actual wick tip. Enclose that tip in the blue root.
  flame.position.set(x+.004,y-.010,z);flame.name='Red candle flame';flame.visible=false;flame.userData.noAO=true;flame.userData.waterSide='above';flame.renderOrder=3;scene.add(flame);flames.push(flame);states.push(motion);
  const light=new THREE.PointLight('#ffbc73',0,3.1,2);light.name='Local candle illumination';light.position.copy(flame.position).add(new THREE.Vector3(0,.028,0));scene.add(light);lights.push(light);
 });
 function reset(active){visiting=active;lit.fill(false);levels.value.fill(0);flames.forEach(f=>f.visible=false);lights.forEach(l=>l.intensity=0);}
 return {flames,lights,levels,enter(){reset(true);},leave(){reset(false);},
  light(i){if(!visiting||!Number.isInteger(i)||i<0||i>=lit.length||lit[i])return false;lit[i]=true;return true;},
  get strength(){return levels.value.reduce((sum,v)=>sum+v,0)/lit.length;},
  get stats(){return {lit:lit.slice(),count:lit.filter(Boolean).length,strength:this.strength,visiting};},
  update(t,dt=0){states.forEach((state,i)=>{
   levels.value[i]=lit[i]?Math.min(1,levels.value[i]+Math.max(0,dt)/.65):0;
   state.value.copy(candleMotion(t,i*2.31));flames[i].visible=levels.value[i]>0;
   flames[i].scale.setScalar(.65+.35*levels.value[i]);
   lights[i].intensity=.65*state.value.w*levels.value[i];lights[i].position.y=flames[i].position.y+.028*state.value.z;
  });}
 };
}

export function finishCandleWax(source,layout,levels={value:new Float32Array(4)}){
 const material=source.clone();material.roughness=.43;
 const tips=layout.flames.map(([x,y,z])=>new THREE.Vector3(x,y-.015,z));
 const radii=layout.flames.map((_,i)=>(layout.continuousWax?.find(w=>w.index===i)?.radius??(.04/.68))*.68);
 material.onBeforeCompile=shader=>{
  shader.uniforms.waxTips={value:tips};shader.uniforms.waxPoolRadii={value:radii};shader.uniforms.candleLevels=levels;
  shader.vertexShader='varying vec3 waxWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\nwaxWorld=(modelMatrix*vec4(transformed,1.)).xyz;');
  shader.fragmentShader='varying vec3 waxWorld;uniform vec3 waxTips[4];uniform float waxPoolRadii[4];uniform float candleLevels[4];\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
   float waxGlow=0.,waxPool=0.;
   for(int i=0;i<4;i++){
    vec3 d=waxWorld-waxTips[i];float radial=length(d.xz);
    waxGlow=max(waxGlow,candleLevels[i]*exp(-radial*24.-abs(d.y)*55.));
    waxPool=max(waxPool,(1.-smoothstep(waxPoolRadii[i]*.80,waxPoolRadii[i],radial))*(1.-smoothstep(.002,.008,abs(d.y))));
   }
   float waxGrain=sin(waxWorld.x*1100.)*sin(waxWorld.y*975.)*sin(waxWorld.z*1050.);
   roughnessFactor=mix(clamp(roughnessFactor+waxGrain*.035,.30,.60),.19,waxPool);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\ntotalEmissiveRadiance+=vec3(.28,.026,.003)*waxGlow;');
 };
 material.customProgramCacheKey=()=> 'warm-pigmented-candle-wax-v3';return material;
}
