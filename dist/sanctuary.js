import * as THREE from 'three';
import {extractRegion} from './rituals.js';
import {createCandlelight,finishCandleWax} from './candlelight.js';
import {finishLotusLighting} from './lotus-lighting.js';

export function sanctuaryRegionContains(point,region){
 const [xmin,xmax,ymin,ymax,zmin,zmax]=region;
 return point.x>xmin&&point.x<xmax&&-point.z>ymin&&-point.z<ymax&&point.y>zmin&&point.y<zmax;
}

export function installSanctuary(model,asset,layout,scene,{lotusLighting=true}={}){
 const candlelight=createCandlelight(layout,scene);
 let removedTriangles=0;
 for(const region of layout.removeRegionsNative){
  const inside=p=>sanctuaryRegionContains(p,region);
  const discarded=extractRegion(model,n=>/gilded|cedar/i.test(n),inside,points=>points.every(inside));
  discarded.traverse(o=>{if(o.isMesh){removedTriangles+=o.geometry.attributes.position.count/3;o.geometry.dispose();}});
 }
 asset.name='Blender mineral-painted sanctuary';
 asset.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;o.userData.waterSide='above';
  if(o.material.name.includes('vermilion beeswax'))o.material=finishCandleWax(o.material,layout,candlelight.levels);
  if(lotusLighting&&o.material.name.includes('living lotus'))o.material=finishLotusLighting(o.material,THREE.ShaderChunk.lights_fragment_begin);
  o.material.side=THREE.DoubleSide;o.material.envMapIntensity=o.material.metalness>.6?.68:.32;
  for(const key of ['map','normalMap','roughnessMap'])if(o.material[key])o.material[key].anisotropy=8;
  if(/lacquer|rosewood|porcelain/.test(o.material.name)&&!o.material.isMeshPhysicalMaterial){
   const finish=new THREE.MeshPhysicalMaterial();THREE.MeshStandardMaterial.prototype.copy.call(finish,o.material);finish.clearcoat=.30;finish.clearcoatRoughness=.24;o.material=finish;
  }
  if(o.material.name.includes('clear offering water')){
   o.castShadow=false;o.material.side=THREE.FrontSide;o.material.depthWrite=false;o.material.envMapIntensity=.9;o.material.ior=1.333;
  }
 });scene.add(asset);
 return {removedTriangles,flames:candlelight.flames.length,candles:candlelight,update(t,dt){candlelight.update(t,dt);}};
}
