import * as THREE from 'three';

// Screen-space AO has no knowledge of the pond's bent refraction ray. Mark the
// mean water surface in the AO normal/depth pass so submerged contact stays in
// the refracted color (baked basin contact and actual sunlight shadows).
export function installWaterAOMask(ao,water){
 const control={enabled:true},enabled={value:false},normalTexture={value:ao.normalRenderTarget.texture};
 const material=new THREE.ShaderMaterial({side:THREE.DoubleSide,depthTest:true,depthWrite:true,blending:THREE.NoBlending,
  vertexShader:'void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:'void main(){gl_FragColor=vec4(.5,.5,1.,0.);}' });
 const proxy=new THREE.Mesh(water.geometry,material),maskScene=new THREE.Scene();proxy.matrixAutoUpdate=false;proxy.name='Water AO exclusion surface';maskScene.add(proxy);
 const ssao=ao.ssaoMaterial,copy=ao.copyMaterial;
 const originalSSAO=ssao.fragmentShader,originalCopy=copy.fragmentShader;
 if(!ssao.fragmentShader.includes('float realDepth = getLinearDepth( samplePointUv );')||!copy.fragmentShader.includes('vec4 texel = texture2D( tDiffuse, vUv );'))throw new Error('Unsupported AO shader for water exclusion');
 ssao.uniforms.waterMaskEnabled=enabled;
 ssao.fragmentShader='uniform bool waterMaskEnabled;\n'+ssao.fragmentShader.replace('void main() {',`void main() {
  if(waterMaskEnabled&&texture2D(tNormal,vUv).a<.5){gl_FragColor=vec4(1.);return;}`);
 ssao.fragmentShader=ssao.fragmentShader.replace('float realDepth = getLinearDepth( samplePointUv );',`if(waterMaskEnabled&&texture2D(tNormal,samplePointUv).a<.5)continue;
  float realDepth = getLinearDepth( samplePointUv );`);
 copy.uniforms.waterMaskEnabled=enabled;copy.uniforms.waterMaskNormals=normalTexture;
 copy.fragmentShader='uniform bool waterMaskEnabled;uniform sampler2D waterMaskNormals;\n'+copy.fragmentShader.replace('vec4 texel = texture2D( tDiffuse, vUv );',`vec4 texel = texture2D( tDiffuse, vUv );
  if(waterMaskEnabled&&texture2D(waterMaskNormals,vUv).a<.5)texel=vec4(1.);`);
 ssao.needsUpdate=copy.needsUpdate=true;
 const originalRender=ao.render,originalOverride=ao._renderOverride;
 const lastMatrix=new THREE.Matrix4();let lastVisible=null,lastGeometry=null,maskVisible=false;
 const stats={draws:0};
 ao.render=function(renderer,...args){
  water.updateWorldMatrix(true,false);maskVisible=control.enabled&&water.visible;
  if(lastVisible!==maskVisible||lastGeometry!==water.geometry||!lastMatrix.equals(water.matrixWorld))this.invalidated=true;
  lastVisible=maskVisible;lastGeometry=water.geometry;lastMatrix.copy(water.matrixWorld);proxy.geometry=water.geometry;proxy.matrix.copy(water.matrixWorld);
  enabled.value=maskVisible&&this.output===0;normalTexture.value=this.normalRenderTarget.texture;
  return originalRender.call(this,renderer,...args);
 };
 ao._renderOverride=function(renderer,override,target,...args){
  const result=originalOverride.call(this,renderer,override,target,...args);
  if(!maskVisible||override!==this.normalMaterial)return result;
  const previousTarget=renderer.getRenderTarget(),autoClear=renderer.autoClear,shadows=renderer.shadowMap.enabled;
  try{renderer.setRenderTarget(target);renderer.autoClear=false;renderer.shadowMap.enabled=false;renderer.render(maskScene,this.camera);stats.draws++;}
  finally{renderer.setRenderTarget(previousTarget);renderer.autoClear=autoClear;renderer.shadowMap.enabled=shadows;}
  return result;
 };
 Object.assign(control,{stats,dispose(){ao.render=originalRender;ao._renderOverride=originalOverride;ssao.fragmentShader=originalSSAO;copy.fragmentShader=originalCopy;delete ssao.uniforms.waterMaskEnabled;delete copy.uniforms.waterMaskEnabled;delete copy.uniforms.waterMaskNormals;ssao.needsUpdate=copy.needsUpdate=true;ao.invalidated=true;material.dispose();}});
 return control;
}
