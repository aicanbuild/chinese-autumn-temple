"""Branch-aligned bark UVs for the existing fused garden-tree surface."""
import math, random
import numpy as np
from mathutils import Vector

def curve(a,b,bend,steps=12):
 a,b,bend=Vector(a),Vector(b),Vector(bend)
 return [a.lerp(b,t/steps)+bend*math.sin(t/steps*math.pi) for t in range(steps+1)]

def authored_paths(trees):
 """Replay build_garden_trees' seed, including twig RNG; verify against anchors."""
 rng=random.Random(4811);result=[];anchors=[]
 for x,y,h,kind in trees:
  angle=rng.random()*math.tau;lean=Vector((math.cos(angle)*.32,math.sin(angle)*.32,0))
  trunk=curve((0,0,.08),(lean.x,lean.y,h*.88),(lean.y*.8,-lean.x*.8,.08),28)
  radius=(.27 if kind<2 else .34)*(h/7)**.55;paths=[(trunk,radius,.026)]
  for k in range(7):
   a=k/7*math.tau+rng.uniform(-.18,.18);start=Vector((math.cos(a)*rng.uniform(.67,.97),math.sin(a)*rng.uniform(.67,.97),.10))
   paths.append((curve(start,(0,0,.92),(math.cos(a)*.10,math.sin(a)*.10,-.13),10),.055,radius*.63))
  limbs=[]
  for level in range(7):
   t=.34+level*.068;start=trunk[round(t*28)];a=angle+level*2.399+rng.uniform(-.25,.25)
   reach=h*(.37-level*.016)*(1.12 if kind==0 else .94);end=start+Vector((math.cos(a)*reach,math.sin(a)*reach,h*(.16+.017*level)))
   points=curve(start,end,(math.cos(a)*.12,math.sin(a)*.12,-h*.07),16);r=radius*(.49-level*.032)
   paths.append((points,r,.033));limbs.append((points,a,r))
  for points,a,r in limbs:
   for j in range(3):
    start=points[7+j*3];az=a+(j-1)*.82+rng.uniform(-.2,.2);reach=h*.14*rng.uniform(.85,1.2)
    end=start+Vector((math.cos(az)*reach,math.sin(az)*reach,h*rng.uniform(.09,.16)))
    second=curve(start,end,(math.cos(az)*.13,math.sin(az)*.13,-.14),10)
    for k in range(3):
     start=second[4+k*2];az2=az+(k-1)*.85;reach=rng.uniform(.42,.74);end=start+Vector((math.cos(az2)*reach,math.sin(az2)*reach,rng.uniform(.21,.43)))
     twig=curve(start,end,(0,0,-.09),8)
     for n in [3,6,8]:
      q=twig[n]+Vector((x,y,.08));d=(twig[-1]-twig[0]).normalized();anchors.append([round(q.x,4),round(q.y,4),round(q.z,4),kind,rng.uniform(.40,.66),*d])
  result.append(paths)
 return result,anchors

class BranchProjection:
 def __init__(self,points,r0,r1):
  p=np.asarray(points,dtype=float);self.a=p[:-1];self.delta=np.diff(p,axis=0);self.length=np.linalg.norm(self.delta,axis=1);self.direction=self.delta/self.length[:,None]
  self.arc=np.r_[0,np.cumsum(self.length)];self.r0=r0;self.r1=r1
  # A transported frame puts branch seams on the underside; vertical stems
  # use a stable lateral fallback. No world-axis cylindrical branch stretching.
  d=self.direction[0];u=np.array([0.,0.,-1.]);u-=d*np.dot(u,d)
  if np.linalg.norm(u)<.15:u=np.array([0.,1.,0.])-d*d[1]
  frames=[]
  for d in self.direction:
   u-=d*np.dot(u,d);u/=np.linalg.norm(u);frames.append(u.copy())
  self.u=np.asarray(frames);self.v=np.cross(self.direction,self.u)

 def project(self,positions):
  rel=positions[:,None,:]-self.a[None,:,:]
  raw=np.einsum('nsd,sd->ns',rel,self.delta)/self.length[None,:]**2
  t=np.clip(raw,0,1);radial=rel-t[:,:,None]*self.delta[None,:,:]
  distance=np.linalg.norm(radial,axis=2);segment=np.argmin(distance,axis=1);row=np.arange(len(positions));t=t[row,segment];radial=radial[row,segment]
  radius=self.r0+(self.r1-self.r0)*((segment+t)/len(self.length))**.85
  along=self.arc[segment]+t*self.length[segment]
  theta=np.mod(np.arctan2(np.einsum('nd,nd->n',radial,self.v[segment]),np.einsum('nd,nd->n',radial,self.u[segment])),math.tau)
  unit=radial/np.maximum(np.linalg.norm(radial,axis=1)[:,None],1e-9)
  return np.abs(distance[row,segment]-radius),theta,along,unit

def align_bark(mesh,paths):
 projections=[BranchProjection(*p) for p in paths]
 centers=np.asarray([p.center[:] for p in mesh.polygons]);normals=np.asarray([p.normal[:] for p in mesh.polygons])
 scores=[]
 for p in projections:
  error,theta,along,unit=p.project(centers)
  scores.append(error+.025*(1-np.einsum('nd,nd->n',unit,normals)))
 chosen=np.argmin(scores,axis=0);layer=mesh.uv_layers.active or mesh.uv_layers.new()
 positions=np.asarray([v.co[:] for v in mesh.vertices]);lookups=[p.project(positions) for p in projections]
 # The trunk retains approximately the old grain scale. Branch circumference
 # uses its own radius instead of the angle around the whole tree.
 for face,path_index in zip(mesh.polygons,chosen):
  error,theta,along,unit=lookups[path_index];indices=[mesh.loops[i].vertex_index for i in face.loop_indices]
  angles=theta[indices].copy()
  if np.ptp(angles)>math.pi:angles[angles<math.pi]+=math.tau
  circumference=math.tau*max(paths[path_index][1:])*1.3
  for li,vi,a in zip(face.loop_indices,indices,angles):layer.data[li].uv=(a/math.tau*circumference,along[vi]*.65)
 mesh.update()
 from bark_junctions import add_bark_blend
 add_bark_blend(mesh,paths)
 return {"faces":len(mesh.polygons),"branchesUsed":len(set(chosen.tolist())),"maxAssignmentScore":float(np.max(np.min(np.asarray(scores),axis=0)))}
