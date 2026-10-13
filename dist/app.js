import {rapidWaterVertex,rapidWaterFragment,installRapidUniforms,subdivideCreekSurface,createCreekBreakers,bindCreekBreakerWater} from './creek-rapids.js';
import {createHandwash} from './handwash.js';
let handwash;
import {installTempleStream,combineWaterGeometry,streamWaterFragment,installStreamUniforms,streamContains} from './temple-stream.js';
import {currentWaterFragment} from './water-current.js';
import {createPondSplash} from './pond-splash.js';
import {scareKoi} from './koi-reaction.js';
let templeStream,streamOptics;
import {installCamelliaBlossoms} from './camellia-blossoms.js';
import {installCamellias} from './camellia-leaves.js';
import {applyFoliageLighting} from './foliage-lighting.js';
import {installForestEdge} from './forest-edge.js';
import {installFineCaisson} from './fine-caisson.js';
import {playWoodenFish} from './wooden-fish-audio.js';
import {installMuralContact} from './mural-contact.js';
import {installCaissonVines} from './caisson-vines.js';
import {installWaterSunlight} from './water-sunlight.js';
import {createVegetationShadowInstances} from './vegetation-shadow-instances.js';
let vegetationShadows,stoneShadows;
import {installAureoleRelief} from './aureole-relief.js';
import {installDoorBacks} from './door-backs.js';
import {captureHallReflections} from './hall-reflections.js';
let hallReflections;
import {createHallOcclusion} from './hall-occlusion.js';
let hallOcclusion;
import {installAltarBrocade} from './altar-brocade.js';
import {installLotusSurfaces} from './lotus-surfaces.js';
import {installCandleWaxGeometry} from './candlelight.js';
import {createSanctuaryDetail} from './sanctuary-detail.js';
import {applyCanopyWind,createWindShadows} from './foliage-wind.js';
import {lowestLeafPoint,setLeafRotation,leafInstanceColor} from './leaf-settling.js';
import {supportHeight,collectSupportVertices,advanceSweptLeaf} from './sweep-motion.js';
import {installBoundedLocalLighting} from './local-lighting.js';
import {createPondMotion,advanceFloatingLeaf,impactWaterFragment,impactWaterVertex,createPondGeometry} from './pond-motion.js';
import {installPondBasin} from './pond-basin.js';
import {installPondContact} from './pond-contact.js';
import {installHallContact} from './hall-contact.js';
import {createWaterCaptureRegion} from './water-capture-region.js';
import {depthWaterFragment} from './water-optics.js';
import {installPineCrowns} from './pine-crowns.js';
import {installBankGrass} from './bank-grass.js';
import {installSanctuary} from './sanctuary.js';
import {createWaterSurfaceVisibility} from './water-surface.js';
import {createRenderQuality} from './render-quality.js';
import {installIncenseVessel} from './incense-vessel.js';
import {SunlightPass} from './sunlight.js';
import {versionAssetUrl} from './asset-versions.js';
import {createCameraSafety} from './camera-safety.js';
import {panWithArrowKeys} from './keyboard-pan.js';
import {createLeafGeometry,createFallenLeafGeometry,applyLeafSurface} from './leaf-surfaces.js';
import {createGroundSurface} from './ground-surface.js';
import {installGardenGround} from './garden-ground.js';
import {createGpuProfiler,profileGpuMethod} from './gpu-profiler.js';
import {renderSceneFrame} from './scene-frame.js';
import {simulationFrame} from './simulation-time.js';
import {createStaticSunShadows} from './static-sun-shadows.js';
import {installGardenTrees} from './garden-trees.js';
import {installPondOptics} from './pond-optics.js';
import {installLanterns} from './lanterns.js';
import * as THREE from 'three';
import {installPondStones} from './pond-stones.js';
import {replaceBridge} from './bridge.js';
import {installPondShadows} from './pond-shadows.js';
import {installUnderstory} from './understory.js';
import {createSculptureLOD} from './sculpture-lod.js';
import {createWaterVisibility} from './water-visibility.js';
import {createLandscape} from './landscape.js';
import {createKoi,updateKoi} from './koi.js';
import {installRoofTiles} from './roof-tiles.js';
import {installPondLotusMotion} from './pond-lotus-motion.js';
import {createStaticCellCulling} from './static-mesh-cells.js';
import {installGuardians} from './guardians.js';
import {installSanctuaryFloor} from './sanctuary-floor.js';
import {createSanctuaryLighting} from './sanctuary-lighting.js';
import {createRituals} from './rituals.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Water} from 'three/addons/objects/Water2.js';
import {Sky} from 'three/addons/objects/Sky.js';
import {HDRLoader} from 'three/addons/loaders/HDRLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {CachedSSAOPass} from './cached-ao.js';
import {installWaterAOMask} from './water-ao.js';
import {SMAAPass} from 'three/addons/postprocessing/SMAAPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';

installBoundedLocalLighting();

const $=s=>document.querySelector(s), clamp=THREE.MathUtils.clamp;
let pineCrowns,waterRegion,pondMotion,sanctuaryDetail,lotusDetail;
let seed=71127;
function random(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;}
const range=(a,b)=>a+(b-a)*random();
const scene=new THREE.Scene();
scene.background=new THREE.Color('#a7b6a9');
scene.fog=new THREE.FogExp2('#b4bcaa',.0038);
const camera=new THREE.PerspectiveCamera(43,(innerWidth||846)/(innerHeight||747),.09,420);
camera.position.set(14,8.5,26);camera.position.multiplyScalar(Math.min(1.8,Math.max(1,1.35/camera.aspect)));
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
const gpuProfiler=new URLSearchParams(location.search).has('gpuProfile')?createGpuProfiler(renderer.getContext(),{targets:['frame','main','shadows','reflection','refraction','ao','sunlight','smaa','output']}):null;
renderer.setSize(innerWidth,innerHeight);
const renderQuality=createRenderQuality(devicePixelRatio);renderer.setPixelRatio(renderQuality.pixelRatio);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=.83;
renderer.shadowMap.enabled=true;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=true;renderer.info.autoReset=false;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.domElement.tabIndex=0;
renderer.domElement.setAttribute('aria-label','秋日寺庙三维画面。方向键前后左右平移，拖动环顾，滚轮靠近。');
$('#world').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);
controls.target.set(0,2.0,0);
controls.enableDamping=true;controls.dampingFactor=.055;controls.rotateSpeed=.55;controls.zoomSpeed=.7;
controls.minDistance=5;controls.maxDistance=65;controls.maxPolarAngle=1.40;controls.minPolarAngle=.20;controls.enablePan=true;controls.screenSpacePanning=false;controls.panSpeed=.65;
controls.update();
const cameraSafety=createCameraSafety(camera,controls,(x,z)=>surfaceAt(x,z));
scene.add(new THREE.HemisphereLight('#d2e5ee','#3a4329',.30));
const sun=new THREE.DirectionalLight('#ffe6bc',3.7);
sun.position.set(-18,24,7);sun.target.position.set(0,0,-1);
sun.castShadow=true;const shadowSize=innerWidth<700?2048:4096;sun.shadow.mapSize.set(shadowSize,shadowSize);
Object.assign(sun.shadow.camera,{left:-26,right:26,top:26,bottom:-26,near:.5,far:75});
sun.shadow.bias=-.00035;sun.shadow.normalBias=.027;sun.shadow.radius=2;
scene.add(sun,sun.target);
const fill=new THREE.DirectionalLight('#bfdce3',.16);fill.position.set(12,8,-14);scene.add(fill);
const sky=new Sky();sky.userData.waterSide='above';sky.scale.setScalar(500);
Object.assign(sky.material.uniforms.turbidity,{value:5});sky.material.uniforms.rayleigh.value=1.1;sky.material.uniforms.mieCoefficient.value=.004;sky.material.uniforms.mieDirectionalG.value=.82;
sky.material.uniforms.sunPosition.value.copy(sun.position).normalize();
const envScene=new THREE.Scene();envScene.add(sky);
const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(envScene,.03,.1,600).texture;pmrem.dispose();scene.add(sky);

const renderTarget=new THREE.WebGLRenderTarget(innerWidth,innerHeight,{type:THREE.HalfFloatType,depthTexture:new THREE.DepthTexture(innerWidth,innerHeight,THREE.UnsignedIntType)});
const composer=new EffectComposer(renderer,renderTarget);composer.setSize(innerWidth,innerHeight);composer.addPass(new RenderPass(scene,camera));
const ao=new CachedSSAOPass(scene,camera,innerWidth,innerHeight,16);ao.kernelRadius=.45;ao.minDistance=.008/(camera.far-camera.near);ao.maxDistance=.9/(camera.far-camera.near);ao.enabled=innerWidth>600;composer.addPass(ao);const sunlight=new SunlightPass(camera,sun);composer.addPass(sunlight);composer.addPass(new SMAAPass());composer.addPass(new OutputPass());
if(gpuProfiler){composer.passes.forEach((pass,i)=>profileGpuMethod(gpuProfiler,pass,'render',['main','ao','sunlight','smaa','output'][i]));profileGpuMethod(gpuProfiler,renderer.shadowMap,'render','shadows');}
const originalOverride=ao._overrideVisibility.bind(ao);const originalRestore=ao._restoreVisibility.bind(ao);let hiddenDuringAO=[];
ao.excludeFromAO=o=>o.isInstancedMesh||o.isWater||o===broom||o.userData.noAO;
ao._overrideVisibility=()=>{originalOverride();hiddenDuringAO=[];scene.traverse(o=>{if(ao.excludeFromAO(o)){hiddenDuringAO.push([o,o.visible]);o.visible=false;}});};
ao._restoreVisibility=()=>{originalRestore();hiddenDuringAO.forEach(([o,v])=>o.visible=v);};
const loadingManager=new THREE.LoadingManager();
loadingManager.setURLModifier(versionAssetUrl);
loadingManager.onProgress=(url,n,total)=>{$('#load-bar').style.width=`${Math.min(90,20+n/total*70)}%`;};
const textureLoader=new THREE.TextureLoader(loadingManager);
function tex(name,srgb=false){const t=textureLoader.load(`./assets/${name}`);if(srgb)t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return t;}
const maps=['maple','ginkgo','green'].map(n=>tex(`${n}-leaf.png`,true));
const leafSurfaces=['maple','ginkgo','green'].map(n=>({normal:tex(`${n}-leaf-normal.png`),surface:tex(`${n}-leaf-surface.png`)}));
const normal0=tex('pond-ripples-0.png'),normal1=tex('pond-ripples-1.png');
const streamFlow=tex('stream-flow.png'),streamNormals=[tex('water-normal-0.jpg'),tex('water-normal-1.jpg')];
const pondLightMaps=[tex('pond-caustics-0.png'),tex('pond-caustics-1.png')];
let creekBreakers;
let model,water,entered=false,sweeping=false,walk=false,held=false,elapsed=0,fallTime=0;
let pondSplash,pondOccluders=[],lastPondHit=null;
let staticSunShadows,waterAOMask,pondOptics,sanctuary,sanctuaryLighting,rituals,landscape,waterVisibility,waterSurface,sculptureLOD,specimenTrees;
let sceneReady=false,keys={},yaw=0,pitch=-.10,viewSaved,panMode=false;
const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2(0,0),dummy=new THREE.Object3D(),worldUp=new THREE.Vector3(0,1,0);
const leafMaterials=maps.map((map,i)=>new THREE.MeshStandardMaterial({map,alphaTest:.42,side:THREE.DoubleSide,roughness:.76,metalness:0,color:i===2?'#9baa79':'#fff1ca'}));
const canopyUniform={value:0};
leafMaterials.forEach((m,i)=>applyLeafSurface(m,{...leafSurfaces[i],wind:canopyUniform}));
const canopyGeom=createLeafGeometry(),fallenLeafGeometries=Array.from({length:6},(_,i)=>createFallenLeafGeometry(i%2,Math.floor(i/2)));

const canopyBatches=[];
const canopyShadows=leafMaterials.map(m=>createWindShadows(m,canopyUniform,applyCanopyWind,'canopy'));
function updateCanopyDetail(){
 for(const mesh of canopyBatches){
  const distance=camera.position.distanceTo(mesh.boundingSphere.center);
  if(distance>31)mesh.userData.distant=true;else if(distance<26)mesh.userData.distant=false;
  mesh.count=Math.round(mesh.userData.fullCount*(mesh.userData.distant?.55:1));
 }
}
function makeCanopies(anchors,plantings){
 const groups=plantings.map(()=>[]);
 for(const [anchorIndex,[x,y,z,kind,r]] of anchors.entries()){
  for(let j=0;j<(innerWidth<600?38:64);j++){
   // Leaves gather around branch tips, with open space between crowns.
   const theta=random()*Math.PI*2,rad=Math.sqrt(random())*r*1.02;
   const xx=x+Math.cos(theta)*rad,zz=-y+Math.sin(theta)*rad,yy=z+(random()+random()-1)*r*.60;
   const size=range(.115,.20)*(kind===2?1.12:1);
   groups[Math.floor(anchorIndex/189)].push([xx,yy,zz,range(-1.2,1.2),random()*6.28,range(-.8,.8),size]);
  }
 }
 groups.forEach((a,treeIndex)=>{
  const k=plantings[treeIndex][3];
  // Shuffle before selecting a distant subset so every branch stays represented.
  for(let j=a.length-1;j>0;j--){const q=Math.floor(random()*(j+1));[a[j],a[q]]=[a[q],a[j]];}
  const mesh=new THREE.InstancedMesh(canopyGeom,leafMaterials[k],a.length);mesh.name=`Individual ${['maple','ginkgo','forest'][k]} leaves`;mesh.userData.waterReflection=false;
  const c=new THREE.Color();
  a.forEach((q,i)=>{dummy.position.set(q[0],q[1],q[2]);dummy.rotation.set(-Math.PI/2+q[3],q[4],q[5]);dummy.scale.set(q[6]*.85,q[6],q[6]);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);const shade=range(.68,1.12);c.setRGB(shade,shade*range(.91,1.04),shade*.89);mesh.setColorAt(i,c);});
  mesh.customDepthMaterial=canopyShadows[k].depth;mesh.customDistanceMaterial=canopyShadows[k].distance;mesh.castShadow=true;mesh.receiveShadow=true;mesh.computeBoundingSphere();mesh.boundingSphere.radius+=.032;mesh.userData.waterMotionPadding=.032;mesh.userData.fullCount=a.length;mesh.userData.distant=false;canopyBatches.push(mesh);scene.add(mesh);
 });updateCanopyDetail();
}

function plantFerns(root){
 root.updateMatrixWorld(true);let species=0;
 root.traverse(o=>{if(!o.isMesh)return;
  const g=o.geometry.clone().applyMatrix4(o.matrixWorld);g.computeBoundingBox();const box=g.boundingBox;const center=box.getCenter(new THREE.Vector3());const width=box.max.x-box.min.x;g.translate(-center.x,-box.min.y,-center.z);
  const mat=o.material.clone();mat.color.set('#b3bd83');mat.envMapIntensity=.2;mat.side=THREE.DoubleSide;mat.alphaTest=.5;mat.transparent=false;mat.roughness=.9;mat.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  applyFoliageLighting(mat,.27);
  const mesh=new THREE.InstancedMesh(g,mat,24);mesh.castShadow=true;mesh.receiveShadow=true;
  for(let i=0;i<24;i++){const a=(i+species*.21)/24*Math.PI*2;const r=range(1.04,1.16);let x=Math.cos(a)*11.5*r,z=5.8+Math.sin(a)*6.9*r;if(Math.abs(x)<2.1)x+=(x<0?-2.3:2.3);dummy.position.set(x,.21,z);dummy.rotation.set(0,random()*Math.PI*2,0);dummy.scale.setScalar(range(.65,1.15)/width);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);}
  mesh.userData.waterMotionPadding=.005;mesh.computeBoundingSphere();scene.add(mesh);species++;
 });
}

const captureCounters={reflection:{count:0,calls:0,triangles:0,cpuMs:0},refraction:{count:0,calls:0,triangles:0,cpuMs:0}};
let captureProfile={},cpuSum=0,averageCpuMs=0,waterPassMode=null;const waterDraws=new Map(),sceneDraws=new Map();
function waterCapture(mode){
 // Overflow shares these capture textures: exclude it while writing them.
 const breakersVisible=creekBreakers?.root.visible;if(creekBreakers)creekBreakers.root.visible=false;
 const endGpu=gpuProfiler?.begin(mode);
 waterPassMode=mode;const restore=waterVisibility?.capture(mode),before={...renderer.info.render},started=performance.now();
 return ()=>{const metrics=captureCounters[mode];metrics.count++;metrics.calls+=renderer.info.render.calls-before.calls;metrics.triangles+=renderer.info.render.triangles-before.triangles;metrics.cpuMs+=performance.now()-started;restore?.();if(creekBreakers)creekBreakers.root.visible=breakersVisible;waterPassMode=null;endGpu?.();};
}
function installWaterMetrics(){
 // Batch callbacks also run for shadows with a null scene. Renderer aggregate
 // counters still include batches; omit them from this named main-pass profiler.
 scene.traverse(o=>{if(!o.isMesh||o.isWater||o.isBatchedMesh)return;const previous=o.onBeforeRender;o.onBeforeRender=function(renderer,scene,camera,geometry,material,group){previous.call(this,renderer,scene,camera,geometry,material,group);const triangles=Math.min(group?.count??Infinity,geometry.drawRange.count,geometry.index?.count??geometry.attributes.position.count)/3*(o.isInstancedMesh?o.count:1);const key=o.name||material.name;const pass=waterPassMode??(scene.overrideMaterial?'ao':'main');const profileKey=pass+': '+key;const profile=sceneDraws.get(profileKey)||{triangles:0,calls:0};profile.triangles+=triangles;profile.calls++;sceneDraws.set(profileKey,profile);if(waterPassMode!=='refraction')return;const entry=waterDraws.get(key)||{triangles:0,bounds:o.userData.waterClipBounds};entry.triangles+=triangles;waterDraws.set(key,entry);};});
}
function recordCaptureProfile(){
 if(sceneDraws.size){canvas.dataset.renderProfile=JSON.stringify([...sceneDraws].sort((a,b)=>b[1].triangles-a[1].triangles).slice(0,25).map(([name,v])=>({name,triangles:Math.round(v.triangles/180),calls:v.calls/180})));sceneDraws.clear();}
 const samples=Math.max(1,captureCounters.refraction.count);captureProfile.underwaterMeshes=[...waterDraws].sort((a,b)=>b[1].triangles-a[1].triangles).slice(0,10).map(([name,entry])=>({name,triangles:Math.round(entry.triangles/samples),bounds:entry.bounds}));waterDraws.clear();
 for(const [name,c]of Object.entries(captureCounters)){const n=Math.max(1,c.count);captureProfile[name]={captures:c.count,drawCalls:Math.round(c.calls/n),triangles:Math.round(c.triangles/n),cpuMs:Math.round(c.cpuMs/n*10)/10};c.count=c.calls=c.triangles=c.cpuMs=0;}
}
function createWater(){
 const pondGeo=createPondGeometry();
 const geo=templeStream?combineWaterGeometry(pondGeo,templeStream.waterGeometry):pondGeo;
 const waterFragment=rapidWaterFragment(currentWaterFragment(impactWaterFragment(streamWaterFragment(depthWaterFragment(Water.WaterShader.fragmentShader,{refraction:false})))));
 water=new Water(geo,{shader:{...Water.WaterShader,vertexShader:rapidWaterVertex(impactWaterVertex(Water.WaterShader.vertexShader)),fragmentShader:waterFragment},color:0xffffff,scale:.45,textureWidth:innerWidth<600?768:1536,textureHeight:innerWidth<600?768:1536,flowDirection:new THREE.Vector2(-.944,-.330),flowSpeed:.055,captureFilter:waterCapture,captureRegion:(mode,cam,target)=>waterRegion?.capture(mode,cam,target),refractionDepth:true,reflectivity:((1.333-1)/(1.333+1))**2,normalMap0:normal0,normalMap1:normal1});
 installStreamUniforms(water.material,streamFlow,streamNormals);installRapidUniforms(water.material,tex('creek-rapids.png'));
 water.rotation.x=-Math.PI/2;water.position.set(0,-.025,5.8);water.name='Reflecting clear koi pond';water.userData.surfaceDisplacement=.55;pondMotion=createPondMotion(water.material,sun);installWaterSunlight(water,sun);if(creekBreakers)bindCreekBreakerWater(creekBreakers,water);scene.add(water);waterSurface=createWaterSurfaceVisibility(water);waterAOMask=installWaterAOMask(ao,water);
 pondSplash=createPondSplash(scene,(x,z)=>poolAt(x,z)&&surfaceAt(x,z)<0);

}

const fish=[];
function makeFish(root){fish.push(...createKoi(root,scene,random));}
function animateFish(t){updateKoi(fish,t);}

// Falling and settled leaves are the same objects. Swept leaves retain their velocity.
const LEAF_COUNT=3900,leaves=[],leafMeshes=[],leafDrawCounts=new Uint16Array(6);
let gardenGround=null;
function poolAt(x,z){return(x/11.5)**2+((z-5.8)/6.9)**2<.97;}
function surfaceAt(x,z){
 if(handwash&&Math.hypot(x+3.7,z-15.6)<.80)return 1.34;
 if(Math.abs(x)<1.48&&z>=12.5&&z<13.5)return .54;
 if(Math.abs(x)<1.20&&z>-.92&&z<12.5){const board=Math.max(0,Math.min(70,Math.round((12.4-z)/.188)));return .52+.61*Math.sin(board*.188/13.3*Math.PI)+.072;}
 if(x>=-6.127501&&x<=6.117501&&z<=-3.474999&&z>=-10.725001)return 1.07;
 if(z<-3.2&&z>-10.7&&Math.abs(x)<6.2)return gardenGround?.heightAt(x,z)??1.095;
 if(z<-0.6&&z>-4.7&&Math.abs(x)<6.8)return gardenGround?.heightAt(x,z)??.505;
 if(poolAt(x,z)||streamContains(x,z))return -.025;
 return gardenGround?.heightAt(x,z)??.385;
}
function spawnLeaf(l,fall=true){
 if(random()<.72){l.x=range(-6.1,6.1);l.z=range(-3.5,.15);}else if(random()<.63){l.x=range(-1.15,1.15);l.z=range(1,12);}else{l.x=range(-12,12);l.z=range(-3,11);}
 l.floor=surfaceAt(l.x,l.z);l.y=l.floor+(fall?range(5,10):.005);l.settledHeight=undefined;l.initialSupportChecked=false;
 l.size=range(.115,.205);l.rot=random()*Math.PI*2;l.tilt=random()*6;l.vx=0;l.vz=0;l.vy=0;l.life=0;l.landedAt=-Infinity;l.contactTilt=0;l.active=true;l.state=fall?'falling':'rest';l.water=poolAt(l.x,l.z)&&l.floor<0;
}
function createLeaves(){
 const materials=[0,1].map(k=>{const m=leafMaterials[k].clone();m.color.set('#ffffff');applyLeafSurface(m,leafSurfaces[k]);return m;});
 for(let b=0;b<6;b++){
  const mesh=new THREE.InstancedMesh(fallenLeafGeometries[b],materials[b%2],Math.ceil(LEAF_COUNT/6));mesh.name='Curled fallen leaves '+b;mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);mesh.userData.waterSide='above';leafMeshes.push(mesh);
 }
 const tint=new THREE.Color();
 for(let i=0;i<LEAF_COUNT;i++){const l={id:i,index:Math.floor(i/6),kind:i%2,batch:i%6,active:false};spawnLeaf(l,false);l.active=i<560;if(!l.active)l.size=0;leaves.push(l);leafMeshes[l.batch].setColorAt(l.index,leafInstanceColor(i,tint));}
 updateLeaves(0,0);
}
const SWEEP_RADIUS=2.4, SWEEP_CLEAR_TIME=1.05;
let spawnBudget=0,sweptTotal=0,sweepSoundAt=0;
function updateLeaves(dt,t,publish=true){
 if(publish)leafDrawCounts.fill(0);
 if(entered){fallTime+=dt;if(fallTime>7){spawnBudget+=dt*(fallTime>40?9:5);while(spawnBudget>=1){spawnBudget--;const l=leaves.find(a=>!a.active);if(l)spawnLeaf(l,true);}}}
 for(const l of leaves){
  if(!l.active){if(publish){dummy.scale.setScalar(0);dummy.updateMatrix();leafMeshes[l.batch].setMatrixAt(l.index,dummy.matrix);}continue;}
  if(publish)leafDrawCounts[l.batch]=Math.max(leafDrawCounts[l.batch],l.index+1);
  if(l.state==='falling'){
   l.y-=dt*range(.40,.48);l.x+=Math.sin(t*.8+l.id)*dt*.22;l.z+=Math.cos(t*.6+l.id)*dt*.10;l.rot+=dt*.47;l.tilt+=dt*.95;
   l.floor=surfaceAt(l.x,l.z);setLeafRotation(l,t,dummy.rotation);
   // Nearby boards or steps may be higher than the surface under the center.
   if(l.y<=Math.max(l.floor,1.5)+l.size+.05){const contact=supportHeight(fallenLeafGeometries[l.batch].attributes.position,dummy.rotation,l.size,l.x,l.z,surfaceAt);if(l.y<=contact){l.y=contact;l.state='rest';l.landedAt=t;l.contactTilt=l.tilt;l.water=poolAt(l.x,l.z)&&l.floor<0&&contact+lowestLeafPoint(fallenLeafGeometries[l.batch],dummy.rotation,l.size)<-.018;if(l.water)pondMotion?.impact(l.x,l.z,t,l.size);}}
  }else if(l.state==='swept'){
   advanceSweptLeaf(l,dt);
   if(l.life>SWEEP_CLEAR_TIME){l.active=false;sweptTotal++;}
  }
  if(l.state==='rest'&&l.water)advanceFloatingLeaf(l,dt,t,surfaceAt);
  setLeafRotation(l,t,dummy.rotation);
  if(l.state==='rest'){
   if(!Number.isFinite(l.landedAt)&&!l.initialSupportChecked){const contact=supportHeight(fallenLeafGeometries[l.batch].attributes.position,dummy.rotation,l.size,l.x,l.z,surfaceAt);if(l.water&&contact+lowestLeafPoint(fallenLeafGeometries[l.batch],dummy.rotation,l.size)>=-.018)l.water=false;l.settledHeight=contact;l.initialSupportChecked=true;}
   if(l.water){const offset=t-l.landedAt<.8?lowestLeafPoint(fallenLeafGeometries[l.batch],dummy.rotation,l.size):0;l.y=-.025+.002-offset+(pondMotion?.heightAt(l.x,l.z,t)??0);}
   else if(t-l.landedAt<.8)l.y=supportHeight(fallenLeafGeometries[l.batch].attributes.position,dummy.rotation,l.size,l.x,l.z,surfaceAt);
   else{l.settledHeight??=supportHeight(fallenLeafGeometries[l.batch].attributes.position,dummy.rotation,l.size,l.x,l.z,surfaceAt);l.y=l.settledHeight;}
  }
  const shrink=l.state==='swept'?clamp((SWEEP_CLEAR_TIME-l.life)/.38,0,1):1;
  if(l.state==='swept'){
   const contact=supportHeight(fallenLeafGeometries[l.batch].attributes.position,dummy.rotation,l.size*shrink,l.x,l.z,surfaceAt);
   if(l.y<contact){l.y=contact;l.vy=Math.max(0,l.vy);}
  }
  if(publish){dummy.position.set(l.x,l.y+(l.water&&l.state==='rest'?Math.sin(t+l.id)*.002:0),l.z);
  dummy.scale.setScalar(l.size*shrink);dummy.updateMatrix();leafMeshes[l.batch].setMatrixAt(l.index,dummy.matrix);}
 }
 if(publish)leafMeshes.forEach((m,i)=>{m.count=leafDrawCounts[i];m.instanceMatrix.needsUpdate=true;});
}

// A real twig broom, not a screen-space cursor image.
const broom=new THREE.Group();broom.visible=false;scene.add(broom);
const broomWood=new THREE.MeshStandardMaterial({color:'#8c6232',roughness:.87}),straw=new THREE.MeshStandardMaterial({color:'#8b7445',roughness:1});
function cylinderBetween(parent,a,b,r1,r2,mat,n=8){const d=new THREE.Vector3().subVectors(b,a);const m=new THREE.Mesh(new THREE.CylinderGeometry(r2,r1,d.length(),n),mat);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(worldUp,d.normalize());m.castShadow=true;parent.add(m);return m;}
cylinderBetween(broom,new THREE.Vector3(0,.15,0),new THREE.Vector3(.25,1.8,.14),.028,.023,broomWood,14);
for(let i=0;i<90;i++){let x=range(-.44,.44),z=range(-.14,.14);cylinderBetween(broom,new THREE.Vector3(x,.015,z),new THREE.Vector3(x*.14,.47,z*.15),.003,.009,straw,5);}
for(let i=0;i<5;i++){const ring=new THREE.Mesh(new THREE.TorusGeometry(.062+i*.01,.01,5,12),new THREE.MeshStandardMaterial({color:'#493b23'}));ring.rotation.x=Math.PI/2;ring.position.y=.34-i*.024;broom.add(ring);}
const broomHit=new THREE.Vector3(),previousHit=new THREE.Vector3();let validBroomHit=false,stroke=0,lastPointer=null,sweepConnected=false;
let broomSupport;
const plane=new THREE.Plane(worldUp,0),probe=new THREE.Vector3();
function findSweepPoint(){
 raycaster.setFromCamera(mouse,camera);
 // Intersect the analytic ground surfaces, then refine height twice.
 plane.constant=-.4;let p=raycaster.ray.intersectPlane(plane,probe);
 if(!p)return false;
 for(let i=0;i<3;i++){plane.constant=-surfaceAt(probe.x,probe.z);if(!raycaster.ray.intersectPlane(plane,probe))return false;}
 if(probe.distanceTo(camera.position)>(walk?4.5:60)||Math.abs(probe.x)>16||Math.abs(probe.z)>15||(poolAt(probe.x,probe.z)&&surfaceAt(probe.x,probe.z)<0))return false;
 broomHit.copy(probe);return true;
}
function sweepAt(point,dt){
 // Sweep the whole drag segment so a quick stroke cannot skip leaves between frames.
 const start=sweepConnected?previousHit:point;
 const sx=point.x-start.x,sz=point.z-start.z,lengthSq=sx*sx+sz*sz;
 const dir=new THREE.Vector3(sx,0,sz);
 if(lengthSq<.0005)dir.set(Math.cos(elapsed*8),0,-.65);dir.normalize();
 let count=0;
 for(const l of leaves){
  if(!l.active||l.state!=='rest'||l.water)continue;
  const t=lengthSq?clamp(((l.x-start.x)*sx+(l.z-start.z)*sz)/lengthSq,0,1):0;
  const cx=start.x+sx*t,cz=start.z+sz*t,dx=l.x-cx,dz=l.z-cz;
  if(dx*dx+dz*dz<SWEEP_RADIUS*SWEEP_RADIUS&&Math.abs(l.y-surfaceAt(cx,cz))<.85){
   setLeafRotation(l,elapsed,dummy.rotation);l.sweepPose=[dummy.rotation.x,dummy.rotation.y,dummy.rotation.z];l.sweepSpin=range(-2.8,2.8);
   l.state='swept';l.vx=dir.x*range(2.0,3.4)+dx*.85;l.vz=dir.z*range(2.0,3.4)+dz*.85;l.vy=range(.18,.42);l.life=0;count++;
  }
 }
 if(count&&elapsed-sweepSoundAt>.15){audio.rustle(Math.min(count/24,1));sweepSoundAt=elapsed;}
 previousHit.copy(point);sweepConnected=true;
}

const audio={ctx:null,master:null,enabled:false,nextBell:2,bellCount:0,
 async start(){
  if(this.ctx){await this.ctx.resume();this.enable(true);return;}
  const AC=window.AudioContext||window.webkitAudioContext;this.ctx=new AC();this.master=this.ctx.createGain();this.master.gain.value=.65;this.master.connect(this.ctx.destination);this.enable(true);
  const reverb=this.ctx.createConvolver(),len=this.ctx.sampleRate*4,imp=this.ctx.createBuffer(2,len,this.ctx.sampleRate);
  for(let c=0;c<2;c++){const d=imp.getChannelData(c);for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/len,3)*.28;}reverb.buffer=imp;const wet=this.ctx.createGain();wet.gain.value=.34;reverb.connect(wet).connect(this.master);this.reverb=reverb;
  for(const [name,volume]of[['wind',.10],['water',.065]]){
   try{const buffer=await this.ctx.decodeAudioData(await(await fetch(versionAssetUrl(`./ambience/${name}.m4a`))).arrayBuffer());const source=this.ctx.createBufferSource();source.buffer=buffer;source.loop=true;const g=this.ctx.createGain();g.gain.value=volume;source.connect(g).connect(this.master);source.start();}catch(e){console.warn('Ambient audio unavailable',name,e);}
  }
  this.enable(this.enabled);
 },
 enable(value){this.enabled=value;if(this.master)this.master.gain.setTargetAtTime(value?.65:0,this.ctx.currentTime,.3);$('#sound').setAttribute('aria-pressed',String(value));$('#sound').setAttribute('aria-label',value?'关闭环境声音':'开启环境声音');$('#sound').title=value?'关闭环境声音':'开启环境声音';},
 splash(){if(!this.ctx||!this.enabled)return;const c=this.ctx,n=c.sampleRate*.22,b=c.createBuffer(1,n,c.sampleRate),a=b.getChannelData(0);for(let i=0;i<n;i++)a[i]=(Math.random()*2-1)*Math.sin(i/n*Math.PI)*Math.exp(-i/n*4);const source=c.createBufferSource(),filter=c.createBiquadFilter(),gain=c.createGain();source.buffer=b;filter.type='lowpass';filter.frequency.value=1400;gain.gain.value=.075;source.connect(filter).connect(gain).connect(this.master);source.start();source.onended=()=>{source.disconnect();filter.disconnect();gain.disconnect();};},
 bell(){if(!this.ctx||!this.enabled)return;const t=this.ctx.currentTime;this.bellCount++;
  const pan=this.ctx.createStereoPanner();pan.pan.value=-.34;pan.connect(this.master);pan.connect(this.reverb);
  [[139,1,11],[281,.47,8],[376,.25,6],[568,.10,4],[731,.045,2.7]].forEach(([f,a,decay])=>{const o=this.ctx.createOscillator(),g=this.ctx.createGain();o.frequency.setValueAtTime(f,t);o.frequency.exponentialRampToValueAtTime(f*.997,t+2);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(a*.12,t+.012);g.gain.exponentialRampToValueAtTime(.0001,t+decay);o.connect(g).connect(pan);o.start(t);o.stop(t+decay+.2);});
  setTimeout(()=>pan.disconnect(),12500);
 },
 rustle(amount=.5){if(!this.ctx||!this.enabled)return;const sr=this.ctx.sampleRate,buf=this.ctx.createBuffer(1,sr*.3,sr),d=buf.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*Math.sin(Math.PI*i/d.length);const src=this.ctx.createBufferSource();src.buffer=buf;const filter=this.ctx.createBiquadFilter();filter.type='bandpass';filter.frequency.value=1600;filter.Q.value=.5;const g=this.ctx.createGain();g.gain.value=.02+amount*.04;src.connect(filter).connect(g).connect(this.master);src.start();}
};

function toast(s){$('#toast').textContent=s;$('#toast').classList.add('show');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').classList.remove('show'),3300);}
function setBroom(value){if(value)handwash?.putBack();renderer.domElement.focus({preventScroll:true});sweeping=value;held=false;sweepConnected=false;$('#broom-mode').setAttribute('aria-pressed',String(value));$('#broom-mode span').textContent=value?'放回扫帚':'桥边扫帚';controls.enableRotate=!value;controls.enablePan=!value;$('#pan-mode').disabled=value;}
function setPan(value){panMode=value;controls.mouseButtons.LEFT=value?THREE.MOUSE.PAN:THREE.MOUSE.ROTATE;controls.touches.ONE=value?THREE.TOUCH.PAN:THREE.TOUCH.ROTATE;$('#pan-mode').setAttribute('aria-pressed',String(value));renderer.domElement.focus({preventScroll:true});}
$('#pan-mode').addEventListener('click',()=>setPan(!panMode));
function setWalk(value){
 if(handwash?.held)handwash.putBack();
 renderer.domElement.focus({preventScroll:true});walk=value;held=false;sweepConnected=false;keys={};
 if(value){viewSaved={position:camera.position.clone(),target:controls.target.clone()};camera.position.set(0,2.18,13.3);yaw=0;pitch=-.075;controls.enabled=false;camera.rotation.order='YXZ';camera.rotation.set(pitch,yaw,0);}
 else{controls.enabled=true;camera.position.copy(viewSaved?.position||new THREE.Vector3(20,13.5,25));controls.target.copy(viewSaved?.target||new THREE.Vector3(0,2,0));controls.update();}
 $('#view-mode').setAttribute('aria-pressed',String(value));$('#view-mode span').textContent=value?'返回俯览':'走入寺院';$('#crosshair').classList.toggle('hidden',!value);$('#mobile-walk').classList.toggle('hidden',!value||!(innerWidth<700||matchMedia('(pointer:coarse)').matches));
}
function walkGround(x,z){
 if(Math.hypot(x+3.7,z-15.6)<1.02)return null;
 if(streamContains(x,z,.20))return null;
 for(const [sx,sz] of [[-11.4,-8.5],[11.6,-10]])if(Math.abs(x-sx)<1.22&&Math.abs(z-sz)<1.22)return null;
 if(Math.abs(Math.abs(x)-6.12)<.16&&z<-3.8&&z>-10.8)return null;
 for(const sx of [-3.6,3.6])if(Math.abs(x-sx)<.72&&Math.abs(z+2.25)<.83)return null;
 for(const sx of [-2.65,2.65])if(Math.hypot(x-sx,z+2.35)<.28)return null;
 if(Math.abs(x)>15||z>17.5||z<-12.6)return null;
 if(poolAt(x,z)&&surfaceAt(x,z)<0)return null;
 if(z<-5.15&&z>-10.3&&Math.abs(x)>5.15&&Math.abs(x)<5.75)return null;
 if(z<-10.1&&z>-10.7&&Math.abs(x)<5.6)return null;
 if(z<-4.94&&z>-5.30&&Math.abs(x)>2.08&&Math.abs(x)<5.5)return null;
 const cols=[-5.6,-2.8,2.8,5.6];for(const cx of cols)for(const cz of[-3.85,-10.35])if(Math.hypot(x-cx,z-cz)<.34)return null;
 if(Math.abs(x)<1.9&&z<-7.6&&z>-9.5)return null;
 return surfaceAt(x,z);
}
function moveWalk(dt){
 let f=(keys.KeyW||keys.ArrowUp?1:0)-(keys.KeyS||keys.ArrowDown?1:0),r=(keys.KeyD||keys.ArrowRight?1:0)-(keys.KeyA||keys.ArrowLeft?1:0);
 const len=Math.hypot(f,r);if(len){f/=len;r/=len;const speed=1.55*dt;const dx=(-Math.sin(yaw)*f+Math.cos(yaw)*r)*speed,dz=(-Math.cos(yaw)*f-Math.sin(yaw)*r)*speed;
  if(walkGround(camera.position.x+dx,camera.position.z)!==null)camera.position.x+=dx;
  if(walkGround(camera.position.x,camera.position.z+dz)!==null)camera.position.z+=dz;
 }
 const floor=walkGround(camera.position.x,camera.position.z)??.4;camera.position.y=THREE.MathUtils.damp(camera.position.y,floor+1.62,8,dt);camera.rotation.set(pitch,yaw,0,'YXZ');
}
$('#enter').addEventListener('click',()=>{entered=true;$('#welcome').classList.add('hidden');$('#tools').classList.remove('hidden');audio.start().catch(()=>toast('可点击右上角重新开启声音。'));renderer.domElement.focus();});
$('#sound').addEventListener('click',async()=>{if(!audio.ctx)await audio.start();else{await audio.ctx.resume();audio.enable(!audio.enabled);}});
$('#broom-mode').addEventListener('click',()=>{if(sweeping)setBroom(false);else{if(walk)setWalk(false);camera.position.set(4.6,3.5,16.4);controls.target.set(1,1.3,11.9);controls.update();}});
$('#leave-hall').addEventListener('click',()=>{rituals?.leave();});$('#view-mode').addEventListener('click',()=>setWalk(!walk));
$('#help').onclick=()=>{held=false;keys={};$('#help-dialog').showModal();};$('#close-help').onclick=()=>$('#help-dialog').close();
const canvas=renderer.domElement;
function pointer(e){mouse.set(e.clientX/innerWidth*2-1,-e.clientY/innerHeight*2+1);}
let gesture=null;
const pondRay=new THREE.Raycaster(),pondPlane=new THREE.Plane(new THREE.Vector3(0,1,0),.025),pondPoint=new THREE.Vector3();
function pickPond(checkOcclusion=false){
 if(!water||sweeping||rituals?.inside||rituals?.bellHeld||handwash?.held)return false;
 pondRay.setFromCamera(mouse,camera);if(!pondRay.ray.intersectPlane(pondPlane,pondPoint)||!poolAt(pondPoint.x,pondPoint.z)||surfaceAt(pondPoint.x,pondPoint.z)>=0)return false;
 if(checkOcclusion){const far=pondRay.far;pondRay.far=pondRay.ray.origin.distanceTo(pondPoint)-.02;const covered=pondRay.intersectObjects(pondOccluders,true).some(h=>h.object.visible&&h.object.material?.visible!==false);pondRay.far=far;if(covered)return false;}
 lastPondHit=pondPoint.clone();return true;
}
function pickAction(){return handwash?.held?'handwash-use':(!sweeping&&!rituals?.inside&&!rituals?.bellHeld?handwash?.pick(mouse):null)||rituals?.pick(mouse,sweeping)||(pickPond()?'pond':null);}
function returnObject(){if(handwash?.held)handwash.putBack();else if(rituals?.woodenFish.held)rituals.woodenFish.putBack();else if(rituals?.bellHeld)rituals.leaveBell();else if(sweeping)setBroom(false);else if(rituals?.inside)rituals.leave();}
$('#return-object').addEventListener('click',returnObject);
function updateReturnControl(){
 const holding=handwash?.held||rituals?.woodenFish.held||sweeping;
 const active=holding||rituals?.bellHeld||rituals?.inside,button=$('#return-object');
 const label=holding?'放回':'返回';
 if(button.textContent!==label){button.textContent=label;button.setAttribute('aria-label',holding?'放回当前道具':'返回庭院');}
 $('#tools').classList.toggle('hidden',!active);
}
function updateHallCandleLighting(){const level=sanctuary?.candles.strength??0;sanctuaryLighting?.setCandleLevel(level);hallReflections?.setIntensity(.065+.935*level);}
function activateRitual(id){
 if(!entered||!rituals)return;
 if(id==='handwash'){if(sweeping)setBroom(false);if(walk)setWalk(false);keys={};handwash.take();}
 if(id==='handwash-use')handwash.click();
 if(id==='broom')setBroom(true);
 if(id==='bell'){audio.ctx?.resume();if(!rituals.bellHeld)rituals.focusBell();rituals.ring();}
 if(id==='pond'&&pickPond(true)){pondMotion.disturb(lastPondHit.x,lastPondHit.z,elapsed);pondSplash.splash(lastPondHit.x,lastPondHit.z);scareKoi(fish,lastPondHit.x,lastPondHit.z,elapsed);audio.splash();}
 if(id==='temple'){handwash?.putBack();if(sweeping)setBroom(false);if(walk)setWalk(false);rituals.enter();}
 if(id==='incense')rituals.light();
 if(id?.startsWith('candle-'))sanctuary?.candles.light(Number(id.slice(7)));
 if(id==='wooden-fish')rituals.woodenFish.take();
 if(id==='wooden-fish-strike'){audio.ctx?.resume();rituals.woodenFish.strike();}
}
canvas.addEventListener('pointerdown',e=>{
 pointer(e);if(!entered||rituals?.moving)return;
 if(!audio.ctx)audio.start().catch(e=>console.warn('Ambient audio unavailable',e));
 controls.mouseButtons.LEFT=panMode&&!e.shiftKey&&!e.ctrlKey&&!e.metaKey?THREE.MOUSE.PAN:THREE.MOUSE.ROTATE;
 const panning=panMode||e.button===2||e.shiftKey||e.ctrlKey||e.metaKey;
 if(sweeping&&panning)return;
 const action=e.button===2||e.shiftKey||e.ctrlKey||e.metaKey?null:pickAction();
 gesture={x:e.clientX,y:e.clientY,moved:0,action,bellY:e.clientY,panning};
 if(action==='bell'||action==='handwash'||action==='handwash-use'){e.stopImmediatePropagation();controls.enabled=false;}
 held=true;lastPointer={x:e.clientX,y:e.clientY};sweepConnected=false;canvas.setPointerCapture(e.pointerId);
},true);
canvas.addEventListener('pointermove',e=>{
 pointer(e);if(handwash?.held){if(gesture)gesture.moved=Math.max(gesture.moved,Math.hypot(e.clientX-gesture.x,e.clientY-gesture.y));handwash.move(mouse);return;}if(gesture){gesture.moved=Math.max(gesture.moved,Math.hypot(e.clientX-gesture.x,e.clientY-gesture.y));
  if(gesture.action==='bell'){if(Math.abs(e.clientY-gesture.bellY)>22){activateRitual('bell');gesture.bellY=e.clientY;}return;}}
 if(walk&&held&&!sweeping&&lastPointer){
  const dx=e.clientX-lastPointer.x,dy=e.clientY-lastPointer.y;
  if(gesture?.panning){const sx=-dx*.006,forward=dy*.006,x=camera.position.x+Math.cos(yaw)*sx-Math.sin(yaw)*forward,z=camera.position.z-Math.sin(yaw)*sx-Math.cos(yaw)*forward;if(walkGround(x,z)!==null){camera.position.x=x;camera.position.z=z;}}
  else{yaw-=dx*.003;pitch=clamp(pitch-dy*.003,-.90,.65);}
 }
 lastPointer={x:e.clientX,y:e.clientY};
 if(!held&&!sweeping)canvas.style.cursor=pickAction()?'pointer':'grab';
});
function release(){if(gesture?.action==='bell'||gesture?.action==='handwash')controls.enabled=!walk&&!rituals?.moving;held=false;lastPointer=null;sweepConnected=false;gesture=null;}
canvas.addEventListener('pointerup',e=>{
 const g=gesture;release();if(g&&g.moved<9){pointer(e);if(pickAction()===g.action)activateRitual(g.action);}
});
canvas.addEventListener('pointercancel',release);canvas.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('keydown',e=>{if(document.activeElement?.matches('input,textarea,select,[contenteditable]:not([contenteditable="false"])'))return;if(e.code==='Escape'&&!$('#help-dialog').open){returnObject();return;}if($('#help-dialog').open)return;if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();keys[e.code]=true;});
window.addEventListener('keyup',e=>keys[e.code]=false);window.addEventListener('blur',()=>{keys={};release();});
document.querySelectorAll('[data-key]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();keys[b.dataset.key]=true;b.setPointerCapture(e.pointerId);};b.onpointerup=b.onpointercancel=()=>keys[b.dataset.key]=false;});
document.addEventListener('visibilitychange',()=>{prev=performance.now();if(document.hidden){keys={};held=false;audio.ctx?.suspend();}else if(audio.enabled)audio.ctx?.resume();});
window.addEventListener('resize',()=>{camera.aspect=(innerWidth||846)/(innerHeight||747);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);sculptureLOD?.resize(innerHeight);ao.enabled=innerWidth>600;$('#mobile-walk').classList.toggle('hidden',!walk||!(innerWidth<700||matchMedia('(pointer:coarse)').matches));});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();toast('画面连接暂时中断，请刷新页面恢复庭院。');});

function makePlaque(){const c=document.createElement('canvas');c.width=512;c.height=128;let ctx=c.getContext('2d');ctx.fillStyle='#d5b570';ctx.textAlign='center';ctx.font='76px serif';ctx.fillText('听  秋  寺',256,92);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;const m=new THREE.Mesh(new THREE.PlaneGeometry(1.68,.42),new THREE.MeshBasicMaterial({map:t,transparent:true}));m.position.set(0,4.04,-3.578);scene.add(m);}

async function init(){try{
 const [gltf,layout,fern,koi,hdr,sculpture,terrain,woodland,forestLayout,distantSculpture,bridgeAsset,stoneAsset,stoneLayout,lanternAsset,lanternLayout,treeAsset,treeLayout,treeDistant,incenseVessel,sanctuaryAsset,sanctuaryLayout,bankGrassAsset,pineNear,pineFar,understoryAsset,understoryLayout,daylight,roofAsset,guardianAsset,sanctuaryFloorAsset,bellAsset,basinAsset,sanctuaryDistant,waxAsset,hallNavigation,lotusSurfaces,lotusDistant,brocadeAsset,hallOccluders,doorBackAsset,aureoleAsset,caissonVinesAsset,pondContactMap,hallContactMap,muralContactMap,muralContactLayout,woodenFishAsset,fineCaissonAsset,pondLotusAsset,bankMossAsset,forestEdgeLayout,camelliaAsset,camelliaLayout,camelliaBuffer,camelliaBlossomAsset,camelliaBlossomLayout]=await Promise.all([new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/temple.glb'),fetch(versionAssetUrl('./assets/garden.json')).then(r=>r.json()),new GLTFLoader(loadingManager).loadAsync('./assets/fern/fern-cutout.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/koi/koi.glb'),new HDRLoader(loadingManager).loadAsync('./assets/autumn-forest.hdr'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/sculpture.glb'),...['terrain','woodland'].map(name=>new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync(`./assets/${name}.glb`)),fetch(versionAssetUrl('./assets/woodland.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/sculpture-distant.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/bridge.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/pond-stones.glb'),fetch(versionAssetUrl('./assets/pond-stones.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/stone-lantern.glb'),fetch(versionAssetUrl('./assets/stone-lantern.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/garden-trees.glb'),fetch(versionAssetUrl('./assets/garden-trees.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/garden-trees-distant.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/incense-vessel.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/sanctuary.glb'),fetch(versionAssetUrl('./assets/sanctuary.json')).then(r=>r.json()),new GLTFLoader(loadingManager).loadAsync('./assets/bank-grass.glb'),...['pine-crowns','pine-crowns-distant'].map(name=>new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync(`./assets/${name}.glb`)),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/understory.glb'),fetch(versionAssetUrl('./assets/understory.json')).then(r=>r.json()),fetch(versionAssetUrl('./assets/daylight.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/roof-tiles.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/guardian-lions.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/sanctuary-floor.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/temple-bell.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/pond-basin.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/sanctuary-distant.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/candle-wax.glb'),fetch(versionAssetUrl('./assets/hall-navigation.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/lotus-surfaces.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/lotus-distant.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/altar-brocade.glb'),fetch(versionAssetUrl('./assets/hall-occluders.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/door-backs.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/aureole-relief.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/caisson-vines.glb'),textureLoader.loadAsync('./assets/pond-contact-ao.png'),textureLoader.loadAsync('./assets/hall-contact-ao.png'),textureLoader.loadAsync('./assets/mural-contact-ao.png'),fetch(versionAssetUrl('./assets/mural-contact-ao.json')).then(r=>r.json()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/wooden-fish.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/fine-caisson.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/pond-lotus.glb'),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/bank-moss.glb'),fetch(versionAssetUrl('./assets/forest-edge.json')).then(r=>r.json()),new GLTFLoader(loadingManager).loadAsync('./assets/camellia-leaf.glb'),fetch(versionAssetUrl('./assets/camellia-leaves.json')).then(r=>r.json()),fetch(versionAssetUrl('./assets/camellia-instances.bin')).then(r=>r.arrayBuffer()),new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/camellia-blossoms.glb'),fetch(versionAssetUrl('./assets/camellia-blossoms.json')).then(r=>r.json())]);
 cameraSafety.setHall(hallNavigation);
 sun.position.fromArray(daylight.sunPosition);sun.target.position.fromArray(daylight.sunTarget);sun.color.set(daylight.sunColor);sun.intensity=daylight.sunIntensity;scene.environmentIntensity=daylight.environmentIntensity;sunlight.integrate.uniforms.extinction.value=daylight.volumeExtinction;sky.material.uniforms.sunPosition.value.copy(sun.position).sub(sun.target.position).normalize();
 const capture=new THREE.PMREMGenerator(renderer);const environment=capture.fromEquirectangular(hdr);scene.environment.dispose();scene.environment=environment.texture;scene.environmentRotation.y=.7;capture.dispose();hdr.dispose();
 model=gltf.scene;model.name='Blender temple architecture';model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.userData.waterClipStatic=true;if(o.material){if(o.material.name.includes('moss garden'))o.visible=false;if(o.material.name.includes('cedar'))o.material.color.set('#9e8065');if(o.material.name.includes('granite'))o.material.color.set('#969587');if(o.material.name.includes('bark'))o.material.color.set('#b2afa1');if(['Ridged maple bark','Deep green pine needles','Clipped garden foliage','Living bamboo jade'].includes(o.material.name))o.userData.waterReflection=false;o.material.envMapIntensity=o.material.metalness>.6?1.15:.55;
 if(o.material.name.includes('cedar')||o.material.name.includes('lacquer')){const finish=new THREE.MeshPhysicalMaterial();THREE.MeshStandardMaterial.prototype.copy.call(finish,o.material);finish.clearcoat=o.material.name.includes('cedar')?.22:.40;finish.clearcoatRoughness=.32;o.material=finish;}
 if(o.material.name.toLowerCase().includes('ceramic')){const finish=new THREE.MeshPhysicalMaterial();THREE.MeshStandardMaterial.prototype.copy.call(finish,o.material);finish.clearcoat=.48;finish.clearcoatRoughness=.20;finish.roughness=.38;finish.envMapIntensity=.72;o.material=finish;}
 if(o.material.name.includes('paper')){o.material.emissive=new THREE.Color('#e29c35');o.material.emissiveIntensity=.36;}for(const k of ['map','normalMap','roughnessMap'])if(o.material[k])o.material[k].anisotropy=8;}}});scene.add(model);
 installPondBasin(model,basinAsset.scene);
 pondLotusAsset.scene.traverse(o=>{if(o.isMesh){o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.material.envMapIntensity=.65;for(const k of ['map','normalMap','roughnessMap'])if(o.material[k])o.material[k].anisotropy=8;}});scene.add(pondLotusAsset.scene);
 renderer.domElement.dataset.pondLotusMotion=JSON.stringify(installPondLotusMotion(pondLotusAsset.scene,canopyUniform,ao.normalMaterial));
 renderer.domElement.dataset.pondContact=JSON.stringify(installPondContact(model,pondContactMap).stats);
 installRoofTiles(model,roofAsset.scene,scene);
 installGuardians(model,guardianAsset.scene,scene);
 installSanctuaryFloor(model,sanctuaryFloorAsset.scene,scene);renderer.domElement.dataset.hallContact=JSON.stringify(installHallContact(sanctuaryFloorAsset.scene,hallContactMap).stats);
 sculptureLOD=createSculptureLOD(sculpture.scene,distantSculpture.scene,camera,innerHeight);scene.add(sculptureLOD);
 bankMossAsset.scene.traverse(o=>{if(o.isMesh){o.castShadow=o.receiveShadow=true;o.userData.waterClipStatic=true;o.material.side=THREE.DoubleSide;o.material.envMapIntensity=.4;}});scene.add(bankMossAsset.scene);
 const bankGrass=installBankGrass(model,bankGrassAsset.scene,scene);renderer.domElement.dataset.bankGrass=JSON.stringify(bankGrass);
 replaceBridge(model,bridgeAsset.scene,scene);pondOccluders=[model,bridgeAsset.scene,pondLotusAsset.scene];const pondStones=installPondStones(model,stoneAsset.scene,stoneLayout,scene);pondOccluders.push(...pondStones.meshes);const lanterns=installLanterns(model,lanternAsset.scene,lanternLayout,scene,{perLampCulling:renderer.extensions.has('WEBGL_multi_draw')});renderer.domElement.dataset.lanternCulling=JSON.stringify({lamps:lanterns.count,perLampCulling:lanterns.perLampCulling});
 installIncenseVessel(model,incenseVessel.scene,scene);
 installCandleWaxGeometry(sanctuaryAsset.scene,waxAsset.scene);
 installLotusSurfaces(sanctuaryAsset.scene,lotusSurfaces.scene);
 sanctuary=installSanctuary(model,sanctuaryAsset.scene,sanctuaryLayout,scene);
 renderer.domElement.dataset.muralContact=JSON.stringify(installMuralContact(sanctuaryAsset.scene,muralContactMap,muralContactLayout).stats);
 installAltarBrocade(brocadeAsset.scene,scene);
 renderer.domElement.dataset.doorBacks=JSON.stringify(installDoorBacks(doorBackAsset.scene,sanctuaryAsset.scene,scene));
 renderer.domElement.dataset.aureoleRelief=JSON.stringify(installAureoleRelief(aureoleAsset.scene,sanctuaryAsset.scene,scene));
 renderer.domElement.dataset.caissonVines=JSON.stringify(installCaissonVines(caissonVinesAsset.scene,sanctuaryAsset.scene,scene));
 renderer.domElement.dataset.fineCaisson=JSON.stringify(installFineCaisson(fineCaissonAsset.scene,sanctuaryAsset.scene,sanctuaryDistant.scene,scene));
 const staticCells=[createStaticCellCulling(roofAsset.scene,camera,{cellSize:4}),createStaticCellCulling(fineCaissonAsset.scene,camera,{cellSize:2.5}),createStaticCellCulling(bankMossAsset.scene,camera,{cellSize:1.5})];
 setInterval(()=>{renderer.domElement.dataset.staticCells=JSON.stringify(staticCells.map(c=>c.sample()));},3000);
 sanctuaryDetail=createSanctuaryDetail(sanctuaryAsset.scene,sanctuaryDistant.scene);
 lotusDetail=createSanctuaryDetail(sanctuaryAsset.scene,lotusDistant.scene,{errorBudget:.0015,pixelLimit:.5,expectedMeshes:2});
 rituals=createRituals({scene,model,camera,controls,broom,candlePositions:sanctuaryLayout.flames,onEnter:()=>{sanctuary.candles.enter();updateHallCandleLighting();},onLeave:()=>{sanctuary.candles.leave();updateHallCandleLighting();},bellAsset:bellAsset.scene,woodenFishAsset:woodenFishAsset.scene,knockSound:()=>{if(audio.ctx&&audio.enabled)playWoodenFish(audio.ctx,audio.master,audio.reverb);},ringSound:()=>{audio.bell();audio.nextBell=fallTime+range(29,43);}});
 broomSupport=collectSupportVertices(broom);
 const washAsset=await new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/handwash.glb');
 handwash=createHandwash(washAsset.scene,scene,camera,controls,{stoneNormal:tex('handwash-granite-normal.png'),woodMap:tex('handwash-hinoki.jpg',true),splash:()=>audio.splash()});
 const streamAsset=await new GLTFLoader(loadingManager).setDRACOLoader(new DRACOLoader().setDecoderPath('./vendor/three/addons/libs/draco/gltf/')).loadAsync('./assets/temple-stream.glb');
 templeStream=installTempleStream(streamAsset.scene,scene,{normal:tex('pbr-stone-normal.jpg'),roughness:tex('pbr-stone-rough.jpg'),stoneColor:tex('pbr-stone.jpg',true),moss:tex('garden-moss-runtime.jpg',true),sandNormal:tex('sand-normal.jpg'),waterNormal:streamNormals[0]});
 const originalStreamSurface=templeStream.waterGeometry;templeStream.waterGeometry=subdivideCreekSurface(originalStreamSurface);originalStreamSurface.dispose();
 const rapidsResponse=await fetch(versionAssetUrl('./assets/creek-rapids.json'));if(!rapidsResponse.ok)throw new Error('Cannot load creek rapid layout');
 creekBreakers=createCreekBreakers(scene,await rapidsResponse.json(),streamNormals[0]);renderer.domElement.dataset.creekRapids=JSON.stringify(creekBreakers.stats);
 streamOptics=installPondOptics(templeStream.root,pondLightMaps,canopyUniform,sun,{creek:true,causticContrast:.62});
 landscape=createLandscape(terrain.scene,woodland.scene,forestLayout,scene,{perTreeCulling:renderer.extensions.has('WEBGL_multi_draw')});renderer.domElement.dataset.forestCulling=JSON.stringify({trees:landscape.trees,batches:landscape.batches.length,perTreeCulling:landscape.perTreeCulling});renderer.domElement.dataset.gardenMoss=JSON.stringify(await installGardenGround(terrain.scene,loadingManager));cameraSafety.setTerrain(terrain.scene);gardenGround=createGroundSurface([{root:terrain.scene},{root:templeStream.root,maxHeight:1.2},{root:model,include:o=>['Honed silver granite','Polished ebony cedar'].includes(o.material?.name),maxHeight:1.5}]);renderer.domElement.dataset.groundSurface=JSON.stringify(gardenGround.stats);const forestEdge=installForestEdge(understoryAsset.scene,fern.scene,forestEdgeLayout,scene,{perPlantCulling:renderer.extensions.has('WEBGL_multi_draw')});renderer.domElement.dataset.forestEdge=JSON.stringify({plants:forestEdge.plants,batches:forestEdge.batches.length,perPlantCulling:forestEdge.perPlantCulling});const understory=installUnderstory(understoryAsset.scene,understoryLayout,scene);renderer.domElement.dataset.understory=JSON.stringify({shrubs:understory.shrubs,batches:understory.batches.length});const camellias=installCamellias(model,camelliaAsset.scene,camelliaLayout,camelliaBuffer,understoryAsset.scene,scene);renderer.domElement.dataset.camellias=JSON.stringify(camellias.stats);const camelliaBlossoms=installCamelliaBlossoms(model,camelliaBlossomAsset.scene,camelliaBlossomLayout,scene);renderer.domElement.dataset.camelliaBlossoms=JSON.stringify(camelliaBlossoms.stats);specimenTrees=installGardenTrees(model,treeAsset.scene,treeDistant.scene,scene);pineCrowns=installPineCrowns(model,pineNear.scene,pineFar.scene,scene);pineCrowns.update(camera);renderer.domElement.dataset.pineCrowns=JSON.stringify({oldTriangles:pineCrowns.oldTriangles,meshes:pineCrowns.levels.length});specimenTrees.update(camera);makeCanopies(treeLayout.anchors,treeLayout.trees);plantFerns(fern.scene);createWater();makeFish(koi.scene);pondOptics=installPondOptics(scene,pondLightMaps,canopyUniform,sun);createLeaves();makePlaque();waterVisibility=createWaterVisibility(scene,water.position.y);waterRegion=createWaterCaptureRegion(water,scene);// Water captures retain ordinary perspective geometry; ripple UVs refract the clear bed.
 const pondShadows=installPondShadows(scene,sun);renderer.domElement.dataset.pondShadows=JSON.stringify({casters:pondShadows.casters.length,materials:pondShadows.materials,index:1.333});renderer.domElement.dataset.waterRefraction=JSON.stringify({method:"surface-distortion",index:1.333});
 sanctuaryLighting=createSanctuaryLighting(scene,{shadowSize:innerWidth<700?1024:2048});
 hallReflections=captureHallReflections(renderer,scene,[sanctuaryAsset.scene,sculptureLOD,incenseVessel.scene,brocadeAsset.scene,sanctuaryFloorAsset.scene,fineCaissonAsset.scene],{
  exclude:[sculptureLOD,incenseVessel.scene],
  specularRoots:[sanctuaryFloorAsset.scene],
  // The paving extends into the side aisles; include its bevel and recessed joints.
  projections:new Map([
   [sanctuaryFloorAsset.scene,{min:new THREE.Vector3(-6.14,.939,-10.74),max:new THREE.Vector3(6.14,4.3,-3.46)}],
   [fineCaissonAsset.scene,{min:new THREE.Vector3(-5.18,1.07,-10.43),max:new THREE.Vector3(5.18,5.85,-3.6)}]
  ])
 });
 updateHallCandleLighting();
 $('#load-label').textContent='风已入庭';$('#load-bar').style.width='100%';
 hallOcclusion=createHallOcclusion(scene,camera,hallOccluders.rectangles,{isInside:()=>rituals?.inside});
 vegetationShadows=createVegetationShadowInstances([...landscape.batches,...understory.batches,...camellias.batches],[sanctuaryLighting.key,sun]);
 stoneShadows=createVegetationShadowInstances(pondStones.meshes,[sanctuaryLighting.key,sun],{reorder:false});
 staticSunShadows=createStaticSunShadows(renderer,scene,sun,[handwash.staticRoot,templeStream.root,model,roofAsset.scene,guardianAsset.scene,sanctuaryFloorAsset.scene,sanctuaryAsset.scene,sculptureLOD,incenseVessel.scene,bridgeAsset.scene,brocadeAsset.scene,doorBackAsset.scene,aureoleAsset.scene,caissonVinesAsset.scene,fineCaissonAsset.scene,pondLotusAsset.scene,...specimenTrees.levels,...pineCrowns.levels]);
 if(new URLSearchParams(location.search).has('profile'))installWaterMetrics();sceneReady=true;renderer.compile(scene,camera);renderer.render(scene,camera);
 entered=true;setTimeout(()=>{$('#loading').style.opacity=0;$('#loading').style.pointerEvents='none';setTimeout(()=>$('#loading').classList.add('hidden'),1100);},450);
 }catch(e){console.error(e);$('#load-label').textContent='庭院未能打开，请刷新重试';$('#load-bar').style.background='#b88160';}}

let nextShadow=0,prev=performance.now(),frames=0,frameSum=0,realFrameSum=0,averageFrameMs=0;
function animate(now){requestAnimationFrame(animate);const rawDt=(now-prev)/1000;prev=now;if(document.hidden||!sceneReady)return;const cpuStart=performance.now(),frame=simulationFrame(rawDt),dt=frame.delta;elapsed+=dt;canopyUniform.value=elapsed;landscape?.update(elapsed);
 if(walk){for(let i=0;i<frame.steps;i++)moveWalk(frame.step);}else if(!rituals?.moving&&!handwash?.held){if(controls.enabled)panWithArrowKeys(camera,controls,keys,dt,rituals?.inside);controls.update();cameraSafety.constrain(rituals?.inside);}
 rituals?.update(dt,elapsed,{entered,sweeping});handwash?.update(dt,elapsed);
 pondSplash?.update(dt);updateReturnControl();
 // BEGIN hall contact scale
 // SSAO depth gaps are normalized by the camera range; use metres for both hall and garden.
 const indoorAO=rituals?.inside,depthRange=camera.far-camera.near;
 ao.kernelRadius=indoorAO ? .14 : .45;
 ao.minDistance=(indoorAO ? .004 : .008)/depthRange;
 ao.maxDistance=(indoorAO ? .28 : .9)/depthRange;
 // END hall contact scale

 sanctuaryDetail?.update(camera,composer.readBuffer.height,rituals?.inside);lotusDetail?.update(camera,composer.readBuffer.height,rituals?.inside);sanctuary?.update(elapsed,dt);updateHallCandleLighting();sanctuaryLighting?.update(elapsed);animateFish(elapsed);
 for(let i=0;i<frame.steps;i++)updateLeaves(frame.step,elapsed-dt+frame.step*(i+1),i===frame.steps-1);
 pondMotion?.update(elapsed);pondOptics?.update();streamOptics?.update();templeStream?.update(elapsed);creekBreakers?.update(elapsed);updateCanopyDetail();specimenTrees?.update(camera);pineCrowns?.update(camera);
 if(sweeping){
  if(!held&&!keys.Space)sweepConnected=false;
  if(walk&&keys.Space)mouse.set(0,-.63);
  const wasBroomVisible=broom.visible;validBroomHit=findSweepPoint();broom.visible=validBroomHit;if(!validBroomHit)sweepConnected=false;
  if(validBroomHit){
   if(wasBroomVisible)broom.position.lerp(broomHit,1-Math.exp(-dt*18));else broom.position.copy(broomHit);
   broom.rotation.y=Math.atan2(camera.position.x-broomHit.x,camera.position.z-broomHit.z);
   const working=held||keys.Space;stroke=THREE.MathUtils.damp(stroke,working?1:0,8,dt);
   broom.rotation.z=Math.sin(elapsed*9)*.2*stroke;broom.rotation.x=.3;
   broom.position.y=supportHeight(broomSupport,broom.rotation,1,broom.position.x,broom.position.z,surfaceAt);
   if(working)sweepAt(broom.position,dt);
  }
 }else broom.visible=false;
 if(entered&&audio.enabled&&fallTime>audio.nextBell){audio.bell();audio.nextBell=fallTime+range(29,43);}
 // Slow foliage and ritual motion need fewer shadow captures than color frames.
 if(now>=nextShadow){renderer.shadowMap.needsUpdate=true;nextShadow=now+80;}
 sunlight.integrate.uniforms.strength.value=rituals?.inside?.35:1;
 waterSurface?.update(camera);
 hallOcclusion?.beginFrame();vegetationShadows?.update();vegetationShadows?.beginFrame();stoneShadows?.update();stoneShadows?.beginFrame();renderer.info.reset();gpuProfiler?.beginFrame();const endGpuFrame=gpuProfiler?.begin('frame');try{renderSceneFrame(scene,()=>composer.render());rituals?.woodenFish.render(renderer);}finally{endGpuFrame?.();gpuProfiler?.endFrame();}cpuSum+=performance.now()-cpuStart;
 frames++;frameSum+=dt;realFrameSum+=Math.min(rawDt,.25);if(frames===180){recordCaptureProfile();averageCpuMs=Math.round(cpuSum/180*10)/10;cpuSum=0;averageFrameMs=Math.round(realFrameSum/180*10000)/10;const nextRatio=renderQuality.sample(averageFrameMs,now/1000);if(nextRatio!==null){renderer.setPixelRatio(nextRatio);composer.setPixelRatio(nextRatio);}canvas.dataset.stats=JSON.stringify(window.__temple.stats);frames=0;frameSum=0;realFrameSum=0;}
}
requestAnimationFrame(animate);init();
window.__temple={get ready(){return sceneReady;},get stats(){return {simulation:{seconds:elapsed,fallSeconds:fallTime,sampledAt:performance.now()/1000},leaves:leaves.filter(l=>l.active).length,resting:leaves.filter(l=>l.active&&l.state==='rest').length,settling:leaves.filter(l=>l.active&&l.state==='rest'&&elapsed-l.landedAt<.8).length,leafBatches:leafMeshes.map(m=>m.count),falling:leaves.filter(l=>l.active&&l.state==='falling').length,swept:sweptTotal,fish:fish.length,koiAudit:new URLSearchParams(location.search).has('profile')?fish.map(f=>({phase:f.phase,speed:f.speed,rx:f.rx,rz:f.rz,depth:f.depth,drift:f.drift,scale:f.group.scale.x})):undefined,handwash:handwash?.stats,candles:sanctuary?.candles.stats,forestTrees:landscape?.trees??0,hallReflections:hallReflections?.stats,staticSunShadows:staticSunShadows?.stats,hallOcclusion:hallOcclusion?.stats,stoneShadows:stoneShadows?.stats,vegetationShadows:vegetationShadows?.stats,waterOnScreen:water?.visible??false,renderWidth:composer.readBuffer.width,renderHeight:composer.readBuffer.height,waterCullAbove:waterVisibility?.above??0,waterCullBelow:waterVisibility?.below??0,waterSplitMeshes:waterVisibility?.splitMeshes??0,bells:audio.bellCount,walk,sweeping,position:camera.position.toArray(),target:controls.target.toArray(),polar:controls.getPolarAngle(),panMode,frameMs:averageFrameMs,cpuMs:averageCpuMs,gpu:gpuProfiler?.stats,waterPasses:captureProfile,waterRegion:waterRegion?.stats,pondMotion:pondMotion?.stats,floatingLeaves:leaves.filter(l=>l.active&&l.water&&l.state==='rest').length,floatingLeafSamples:leaves.filter(l=>l.active&&l.water&&l.state==='rest').slice(0,3).map(l=>[l.id,l.x,l.y,l.z]),sculptureDetail:sculptureLOD?.getCurrentLevel()===0?'full':'distant',hallCamera:cameraSafety.hallStats,sanctuaryDetail:sanctuaryDetail?.stats,lotusDetail:lotusDetail?.stats,waterAO:waterAOMask?.stats,aoCaptures:ao.captures,aoReuses:ao.reuses,pixelRatio:renderer.getPixelRatio(),drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles};},camera,controls,scene,leaves,walkGround,surfaceAt};
