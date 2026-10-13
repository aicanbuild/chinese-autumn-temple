"""Original closed-surface lotus-scroll relief for the three altar apron panels.

Native Z-up. Leaves are modelled as lobed, cambered solids, not flat decals.
The reverse of each carving penetrates the existing rosewood field by 2 mm.
"""
import bpy,bmesh,math
from mathutils import Vector

def is_altar_carving(o):
 return bool(o.get('altar_relief')) or o.name.startswith(('Altar | carved eight petal lotus','Altar | flowing vine relief'))

def build_altar_carving():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'))
 bronze=next(m for m in used if m.name.startswith('Sanctuary | antique gilt bronze'))
 parts=[];panels=[]
 def mesh(name,vs,faces,material=gold):
  g=bpy.data.meshes.new(name);g.from_pydata(vs,[],faces);g.update()
  bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
  o=bpy.data.objects.new('Altar relief | '+name,g);bpy.context.collection.objects.link(o);g.materials.append(material);o['sanctuary_interior']=True;o['altar_relief']=True;parts.append(o)
  for p in g.polygons:p.use_smooth=True
  uv=g.uv_layers.new()
  for p in g.polygons:
   for li in p.loop_indices:
    v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.7,v.z*.7)
  return o
 def bezier(points,t):
  p=[Vector(v) for v in points]
  while len(p)>1:p=[a.lerp(b,t) for a,b in zip(p,p[1:])]
  return p[0]
 def ribbon(name,path,width,depth,lobes=0,material=gold,base=0):
  # Front/back grids are joined along their complete perimeter; tips never collapse.
  nu,nv=24,8;vs=[];faces=[];back=7.848
  def sample(t,s,front=True):
   c=bezier(path,t);d=bezier(path,min(1,t+.0001))-bezier(path,max(0,t-.0001));d.normalize();n=Vector((-d.y,d.x))
   taper=max(.018,math.sin(math.pi*t)**.65);w=width*taper*(1+lobes*math.sin(t*math.pi*7)**2)
   pos=c+n*s*w
   raised=.0015+base+depth*math.sin(math.pi*t)**.55*(1-.80*abs(s)**1.4)
   # A narrow cut down the midrib helps leaf halves catch separate highlights.
   if lobes:raised-=.0014*math.exp(-s*s*75)*math.sin(math.pi*t)
   return (pos.x,back-raised if front else back,pos.y)
  for front in [True,False]:
   for i in range(nu+1):
    for j in range(nv+1):vs.append(sample(i/nu,2*j/nv-1,front))
  count=(nu+1)*(nv+1)
  for i in range(nu):
   for j in range(nv):
    q=i*(nv+1)+j;faces.extend([(q,q+1,q+nv+2,q+nv+1),(q+count,q+nv+1+count,q+nv+2+count,q+1+count)])
  boundary=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
  for i,q in enumerate(boundary):r=boundary[(i+1)%len(boundary)];faces.append((q,q+count,r+count,r))
  return mesh(name,vs,faces,material)
 def roundel(name,x,z,rx,rz,depth,material=gold,base=0):
  # One vertex per pole avoids coincident sphere rings and zero-area triangles.
  n,m=32,12;vs=[(x,7.848,z-rz)];faces=[]
  for i in range(1,m):
   ph=-math.pi/2+math.pi*i/m
   for j in range(n):
    a=j*math.tau/n;vs.append((x+rx*math.cos(ph)*math.cos(a),7.848-base-depth*(1+math.sin(a))*math.cos(ph),z+rz*math.sin(ph)))
  vs.append((x,7.848,z+rz));top=len(vs)-1
  for j in range(n):faces.append((0,1+(j+1)%n,1+j));faces.append((top,1+(m-2)*n+j,1+(m-2)*n+(j+1)%n))
  for i in range(m-2):
   for j in range(n):a=1+i*n+j;b=1+i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
  return mesh(name,vs,faces,material)
 for index,x in enumerate([-1.16,0,1.16]):
  first=len(parts);z=1.42
  # Nested whorls fit inside the existing double moulding instead of crossing it.
  for layer,(count,r0,r1,w,d,base) in enumerate([(12,.024,.125,.027,.025,0),(8,.012,.086,.023,.028,.006)]):
   for k in range(count):
    a=k*math.tau/count+(math.pi/8 if layer else 0);direction=Vector((math.cos(a),math.sin(a)));side=Vector((-direction.y,direction.x));center=Vector((x,z))
    path=[center+direction*r0,center+direction*(r1*.54)+side*.008,center+direction*(r1*.88)+side*.011,center+direction*r1]
    ribbon('overlapping lotus petal',path,w,d,base=base)
  roundel('lotus seed cup',x,z,.026,.026,.021,bronze)
  for k in range(7):
   a=k*math.tau/7;roundel('gilt lotus seed',x+.015*math.cos(a),z+.015*math.sin(a),.0035,.0035,.005,base=.032)
  for sign in [-1,1]:
   def p(u,v):return (x+sign*u,z+v)
   ribbon('sweeping stem',[p(.105,0),p(.19,-.065),p(.32,.070),p(.405,.005)],.007,.012)
   # Opposed, lobed leaves grow from the stem; asymmetry gives hand-carved rhythm.
   for j,(u,v) in enumerate([(.155,-.013),(.232,.002),(.310,.020)]):
    for side in [-1,1]:
     path=[p(u,v),p(u+.040,v+side*.012),p(u+.068,v+side*.086),p(u+.027,v+side*(.095 if j<2 else .080))]
     ribbon('lobed scroll leaf',path,.018,.020,lobes=.23)
   ribbon('upper curling tendril',[p(.105,.030),p(.170,.116),p(.212,.110),p(.193,.065)],.0045,.009)
   ribbon('lower curling tendril',[p(.285,.004),p(.362,-.102),p(.404,-.100),p(.386,-.052)],.0045,.009)
  for o in parts[first:]:o['altar_panel_index']=index
  panels.append({'centerNative':[x,7.846,z],'parts':len(parts)-first})
 return parts,{'revision':1,'panels':panels,'parts':len(parts),'closedReliefs':True,'backPlaneNative':7.848,'maxDepth':.050}
