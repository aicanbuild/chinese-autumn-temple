// Pre-refinement geometry retained only for the visual comparison fixture.
import * as THREE from 'three';
export function createFallenLeafGeometry(kind=0,variant=0){
 // Boundaries follow the botanical albedo silhouette; empty card corners cannot
 // become invisible support points when a leaf rocks against the ground.
 let outline;
 if(kind===0)outline=[[507,957],[476,737],[78,635],[281,582],[103,333],[337,465],[282,89],[430,354],[514,33],[603,370],[768,129],[713,478],[958,367],[794,595],[935,689],[550,743],[524,957]];
 else{
  outline=[[505,951],[497,758]];
  for(let i=0;i<=24;i++){const t=i/24,a=(204+132*t)*Math.PI/180,r=660-94*Math.exp(-(((t-.50)/.046)**2));outline.push([512+r*Math.cos(a)*.74,777+r*Math.sin(a)]);}
  outline.push([530,754],[523,952]);
 }
 const points=outline.map(([x,y])=>new THREE.Vector2(x/1024-.5,.5-y/1024));
 const faces=THREE.ShapeUtils.triangulateShape(points,[]),midpoints=new Map();
 function midpoint(a,b){const key=[Math.min(a,b),Math.max(a,b)].join(':');if(!midpoints.has(key)){midpoints.set(key,points.length);points.push(points[a].clone().add(points[b]).multiplyScalar(.5));}return midpoints.get(key);}
 const indices=[];for(const [a,b,c] of faces){const ab=midpoint(a,b),bc=midpoint(b,c),ca=midpoint(c,a);indices.push(a,ab,ca,ab,b,bc,ca,bc,c,ab,bc,ca);}
 const positions=[],uv=[];let minimum=Infinity;
 for(const p of points){const x=p.x,y=p.y;
  const rib=.016*Math.exp(-x*x*65)*(y+.6);
  const z=variant===0?.055*Math.abs(x*2)**1.6+.016*(y+.5)**2+rib:variant===1?.16*(x+.10)**2+.085*(y+.5)**3+.045*x*Math.sin(y*6)+rib:.11*(x*2)**2+.10*Math.max(0,y-.03)**2+.045*Math.sin(y*5+x*5)+rib;
  minimum=Math.min(minimum,z);positions.push(x,y,z);uv.push(x+.5,y+.5);
 }
 for(let i=2;i<positions.length;i+=3)positions[i]-=minimum;
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();g.userData.species=kind;g.userData.curlVariant=variant;return g;
}
