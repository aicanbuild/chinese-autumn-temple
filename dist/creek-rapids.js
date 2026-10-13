import * as THREE from 'three';

// Real surface relief in scene metres. Broad moving rollers carry shorter
// breaking crests; the relief atlas ties their energy to actual Blender stones.
export const RAPID_MAX_HEIGHT=.55;
export const RAPID_AMPLITUDE=1.35;
export function rapidWaveGLSL(){return `
 uniform sampler2D creekRelief;
 vec4 rapidProfile(vec2 p){
  if(p.x<12.||p.x>18.||p.y< -18.||p.y>20.)return vec4(0.);
  return texture2D(creekRelief,vec2((p.x-12.)/6.,(p.y+18.)/38.));
 }
 // Smooth seeded spatial noise advects downstream. No global sine train,
 // time reset, per-frame random jitter, or painted white crest bands.
 float rapidHash(vec2 p){
  vec3 q=fract(vec3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);
  return fract((q.x+q.y)*q.z);
 }
 vec3 rapidNoise(vec2 p){
  vec2 i=floor(p),f=fract(p);
  vec2 u=f*f*f*(f*(f*6.-15.)+10.);
  vec2 du=30.*f*f*(f*(f-2.)+1.);
  float a=rapidHash(i),b=rapidHash(i+vec2(1.,0.)),c=rapidHash(i+vec2(0.,1.)),d=rapidHash(i+vec2(1.));
  float k=a-b-c+d;
  return vec3(a+(b-a)*u.x+(c-a)*u.y+k*u.x*u.y,du.x*(b-a+k*u.y),du.y*(c-a+k*u.x));
 }
 vec3 rapidDisturbance(vec2 p,float t){
  vec3 broad=rapidNoise(p*vec2(2.8,3.3)-vec2(.14,8.58)*t);
  vec3 fine=rapidNoise(p*vec2(6.7,7.9)-vec2(-.18,20.54)*t+vec2(17.3,8.1));
  return ${RAPID_AMPLITUDE.toFixed(3)}*vec3(.23*(broad.x-.5)+.07*(fine.x-.5),.23*broad.yz*vec2(2.8,3.3)+.07*fine.yz*vec2(6.7,7.9));
 }
 float rapidHeight(vec2 p,float t){
  vec4 field=rapidProfile(p);
  vec3 moving=rapidDisturbance(p,t);
  return field.r*.55+(field.g+field.a*.08)*moving.x;
 }
 vec2 rapidSlope(vec2 p,float t){
  float e=.024;vec4 field=rapidProfile(p);
  vec4 dx=(rapidProfile(p+vec2(e,0.))-rapidProfile(p-vec2(e,0.)))/(2.*e);
  vec4 dz=(rapidProfile(p+vec2(0.,e))-rapidProfile(p-vec2(0.,e)))/(2.*e);
  vec3 wave=rapidDisturbance(p,t);
  return vec2(dx.r,dz.r)*.55+(field.g+field.a*.08)*wave.yz+vec2(dx.g+dx.a*.08,dz.g+dz.a*.08)*wave.x;
 }
 `;}
export function rapidWaterVertex(base){
 return base.replace('#include <common>','#include <common>\n'+rapidWaveGLSL())
 .replace('vToEye = cameraPosition - worldPosition.xyz;',`worldPosition.y+=rapidHeight(worldPosition.xz,pondTime);
 vToEye = cameraPosition - worldPosition.xyz;`);
}
export function rapidWaterFragment(base){
 return base.replace('#include <common>','#include <common>\n'+rapidWaveGLSL())
 .replace('// calculate the fresnel term',`
  vec2 rapidPoint=(cameraPosition-vToEye).xz;
  if(rapidPoint.x>12.){
   vec2 slope=rapidSlope(rapidPoint,pondTime);
   normal=normalize(normal+vec3(-slope.x,0.,-slope.y));
  }
  // calculate the fresnel term`)
 .replace('float foam=creek?(creekFlow.b*.72+.075)*movingCrest:0.;','float foam=0.;')
 .replace('gl_FragColor=vec4(mix(waterRadiance,vec3(.76,.82,.78),foam),1.);','gl_FragColor=vec4(waterRadiance,1.);');
}
export function installRapidUniforms(material,relief){
 relief.flipY=false;relief.colorSpace=THREE.NoColorSpace;relief.wrapS=relief.wrapT=THREE.ClampToEdgeWrapping;
 relief.minFilter=relief.magFilter=THREE.LinearFilter;relief.generateMipmaps=false;
 material.uniforms.creekRelief={value:relief};
}

// Horizontal water is subdivided across the channel, not just at its banks.
// Reuse the authored bank coordinates so the wet outline cannot creep uphill.
export function subdivideCreekSurface(authored,across=36){
 const source=authored.attributes.position,rows=[];
 for(let i=0;i<source.count;i++)rows.push([source.getX(i),source.getY(i),source.getZ(i)]);
 rows.sort((a,b)=>a[2]-b[2]||a[0]-b[0]);const sections=[];
 for(const p of rows){const last=sections.at(-1);if(!last||Math.abs(last[0][2]-p[2])>.0001)sections.push([p,p]);else {if(p[0]<last[0][0])last[0]=p;if(p[0]>last[1][0])last[1]=p;}}
 const positions=[],uv=[],indices=[];let count=0;
 for(let k=0;k<sections.length;k++){
  // Two rows per authored 10 cm interval resolve the sharp front of each roller.
  for(let half=0;half<(k===sections.length-1?1:2);half++){
   const mix=half*.5,next=sections[Math.min(k+1,sections.length-1)];
   const left=sections[k][0].map((v,i)=>v*(1-mix)+next[0][i]*mix),right=sections[k][1].map((v,i)=>v*(1-mix)+next[1][i]*mix);
   for(let j=0;j<=across;j++){const u=j/across,x=left[0]+u*(right[0]-left[0]),y=left[1]+u*(right[1]-left[1]),z=left[2];positions.push(x,y,z);uv.push(x,z);}
   count++;
  }
 }
 for(let k=0;k<count-1;k++)for(let j=0;j<across;j++){const a=k*(across+1)+j,b=a+across+1;indices.push(a,b,a+1,a+1,b,b+1);}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();return g;
}

// Short overflowing sheets leave the downstream lip with forward momentum.
// They are open, thin water surfaces, never opaque tubes or decorative arcs.
function coherentVariation(t,seed){
 const i=Math.floor(t),f=t-i,u=f*f*f*(f*(f*6-15)+10);
 const hash=n=>{const v=Math.sin(n*127.1+seed*311.7)*43758.5453;return v-Math.floor(v);};
 return hash(i)*(1-u)+hash(i+1)*u;
}
export function jetPoint(j,u,v,t,out=new THREE.Vector3()){
 const pulse=.86+.14*coherentVariation(t*2.1,j.seed),length=j.length*pulse;
 const y=j.lipY+.15*v-((j.lipY+.025)+.15)*v*v;
 const ripple=.027*(coherentVariation(v*5.7-t*7.4+u*.6,j.seed)-.5)*Math.sin(Math.PI*v);
 return out.set(j.x+u*j.width*(.5-.28*v+.10*(coherentVariation(v*5.1-t*3.7,j.seed+u)-.5))+.040*(coherentVariation(v*3.2-t*2.1,j.seed+2)-.5)*v,y+ripple,j.lipZ+length*v);
}
export function createCreekBreakers(scene,layout,normalMap){
 const root=new THREE.Group();root.name='Stone lips — overflowing water and spray';root.userData.rapids=true;
 const nx=8,nz=24,positions=[],uv=[],indices=[],point=new THREE.Vector3();
 layout.jets.forEach((j,k)=>{const start=positions.length/3;for(let z=0;z<=nz;z++)for(let x=0;x<=nx;x++){jetPoint(j,x/nx*2-1,z/nz,0,point);positions.push(...point);uv.push(x/nx,z/nz);}for(let z=0;z<nz;z++)for(let x=0;x<nx;x++){const a=start+z*(nx+1)+x,b=a+nx+1;indices.push(a,b,a+1,a+1,b,b+1);}});
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();g.computeBoundingBox();g.boundingBox.expandByScalar(.15);g.computeBoundingSphere();g.boundingSphere.radius+=.15;
 const material=new THREE.MeshPhysicalMaterial({color:'#102321',metalness:0,roughness:.08,ior:1.333,transparent:true,opacity:.2,side:THREE.DoubleSide,depthWrite:false,normalMap});
 const sheets=new THREE.Mesh(g,material);sheets.name='Thin forward falling water sheets';sheets.userData.waterSide='above';sheets.receiveShadow=true;root.add(sheets);
 const perJet=12,drops=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1,1),new THREE.MeshPhysicalMaterial({color:'#597e79',roughness:.09,metalness:0,clearcoat:1,transparent:true,opacity:.20,depthWrite:false}),layout.jets.length*perJet);drops.name='Short ballistic creek droplets';drops.userData.waterSide='above';drops.frustumCulled=false;drops.instanceMatrix.setUsage(THREE.DynamicDrawUsage);root.add(drops);scene.add(root);const dummy=new THREE.Object3D();
 function update(t){let index=0;for(const j of layout.jets){for(let z=0;z<=nz;z++)for(let x=0;x<=nx;x++){jetPoint(j,x/nx*2-1,z/nz,t,point);g.attributes.position.setXYZ(index++,point.x,point.y,point.z);}}
  g.attributes.position.needsUpdate=true;g.computeVertexNormals();
  layout.jets.forEach((j,k)=>{for(let i=0;i<perJet;i++){const id=k*perJet+i,life=.28+(i%4)*.025,age=((t+i*.071+j.seed)%life),v=age/life;dummy.position.set(j.x+Math.sin(i*7.1)*j.width*.43+Math.sin(i*3.4)*age*.35,j.lipY+.10+(.50+(i%4)*.10)*age-4.9*age*age,j.lipZ+.22+(1.2+(i%3)*.28)*age);const size=(.008+(i%3)*.003)*Math.sin(Math.PI*v);dummy.scale.set(size,size*1.6,size);dummy.rotation.set(0,0,-.4);dummy.updateMatrix();drops.setMatrixAt(id,dummy.matrix);}});drops.instanceMatrix.needsUpdate=true;
 }
 update(0);return {root,update,sheets,drops,stats:{spillLips:layout.jets.length,sheetVertices:g.attributes.position.count,droplets:drops.count}};
}

// Share the pond's existing capture textures, lighting and Fresnel/refraction.
// The water over a stone is the same optical surface, not a pale diffuse prop.
export function bindCreekBreakerWater(breakers,water){
 const m=water.material.clone();m.uniforms=water.material.uniforms;
 m.vertexShader=m.vertexShader
  .replace('worldPosition.y+=rapidHeight(worldPosition.xz,pondTime);','')
  .replace('vCoord = textureMatrix * vec4( position, 1.0 );','vCoord = textureMatrix * vec4(position.x,5.8-position.z,position.y+.025,1.);');
 m.fragmentShader=m.fragmentShader.replace('vec2 slope=rapidSlope(rapidPoint,pondTime);',`vec3 sheetPoint=cameraPosition-vToEye;
   vec3 sheetNormal=normalize(cross(dFdx(sheetPoint),dFdy(sheetPoint)));
   if(sheetNormal.y<0.)sheetNormal=-sheetNormal;
   vec2 slope=-sheetNormal.xz/max(sheetNormal.y,.12);`)
 .replace('#include <tonemapping_fragment>',`gl_FragColor.a*=smoothstep(0.,.16,vUv.x)*smoothstep(0.,.16,1.-vUv.x)*smoothstep(0.,.08,vUv.y)*(1.-smoothstep(.78,1.,vUv.y));
 #include <tonemapping_fragment>`);
 m.depthWrite=false;m.side=THREE.DoubleSide;m.transparent=true;m.name='Overflow — shared pond reflection and refraction';
 breakers.sheets.material.dispose();breakers.sheets.material=m;breakers.sheets.renderOrder=water.renderOrder+1;breakers.drops.renderOrder=water.renderOrder+2;
 return m;
}
