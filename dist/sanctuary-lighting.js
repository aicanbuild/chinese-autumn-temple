import * as THREE from 'three';

export function createSanctuaryLighting(scene,{shadowSize=2048}={}){
 // A broad, warm key from the entry side. Real shadowing keeps reflected fill
 // from erasing the depth of the sculpture, vessels and altar joinery.
 const key=new THREE.SpotLight('#ffe1ad',34,10,.82,.62,2);
 key.name='Sanctuary | shadowed warm key';key.position.set(-1.4,4.2,-4.9);key.target.position.set(0,2.4,-7.8);
 key.castShadow=true;key.shadow.mapSize.set(shadowSize,shadowSize);key.shadow.camera.near=.15;key.shadow.camera.far=10;
 key.shadow.bias=-.00003;key.shadow.normalBias=.004;key.shadow.autoUpdate=false;key.shadow.needsUpdate=true;
 scene.add(key,key.target);
 const fills=[];
 function fill(name,color,intensity,distance,position){const light=new THREE.PointLight(color,intensity,distance,2);light.name='Sanctuary | '+name;light.position.fromArray(position);scene.add(light);fills.push(light);}
 fill('warm room bounce','#ffb75d',1.3,9,[0,3,-7]);
 fill('soft altar bounce','#fff0de',2.2,8,[0,3.73,-7.3]);
 fill('ceiling bounce','#f2dab0',3.2,4.1,[0,4.43,-7.1]);
 fill('entry bounce','#ffe7c4',2.2,5,[-1.3,2.8,-4.6]);
 const fullFill=fills.map(light=>light.intensity);
 function setCandleLevel(value){
  const level=THREE.MathUtils.clamp(value,0,1);
  // A faint trace of doorway daylight remains; candle bounce supplies the room.
  key.intensity=.65+33.35*level;
  fills.forEach((light,i)=>{const dark=i===3?.12:.015;light.intensity=dark+(fullFill[i]-dark)*level;});
 }
 // Geometry is almost static. Refresh at 2 Hz for incense and LOD changes;
 // the sun continues using the existing, independent 12.5 Hz shadow cadence.
 let refreshAt=0;
 return {key,fills,setCandleLevel,update(seconds){if(seconds>=refreshAt){key.shadow.needsUpdate=true;refreshAt=seconds+.5;}},dispose(){key.shadow.map?.dispose();key.removeFromParent();key.target.removeFromParent();for(const light of fills)light.removeFromParent();}};
}
