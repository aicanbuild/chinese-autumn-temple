"""Original gilt scroll foliage fitted to the four existing octagonal soffits.

Native Z-up metres. Relief is seated into the painted board by 0.8 mm;
it follows the actual trapezoid, rather than floating in a horizontal ring.
"""
import bpy,bmesh,math
from mathutils import Vector

def build_caisson_vines():
 gold=next(m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m and m.name.startswith('Sanctuary | hand burnished gold'))
 levels=[(2.48,4.36),(2.15,4.61),(1.79,4.89),(1.43,5.16),(1.08,5.43)]
 parts=[]
 for tier in range(4):
  r,z=levels[tier];r2,z2=levels[tier+1]
  for edge in range(8):
   a=math.pi/8+edge*math.tau/8;b=a+math.tau/8
   corners=[Vector((rr*math.cos(t),7.10+rr*math.sin(t),zz)) for rr,zz,t in [(r,z,a),(r,z,b),(r2,z2,a),(r2,z2,b)]]
   normal=(corners[1]-corners[0]).cross(corners[2]-corners[0]).normalized()
   if normal.z>0:normal=-normal
   tangent=(corners[1]-corners[0]).normalized();across=normal.cross(tangent).normalized()
   vs=[];fs=[]
   def point(u,v,h=0):return corners[0].lerp(corners[1],u).lerp(corners[2].lerp(corners[3],u),v)+normal*h
   def tube(coords,radius=.0028):
    centers=[point(u,v,.001) for u,v in coords];start=len(vs);sides=6
    for j,c in enumerate(centers):
     direction=(centers[min(j+1,len(centers)-1)]-centers[max(j-1,0)]).normalized();side=direction.cross(normal).normalized()
     for k in range(sides):
      angle=k*math.tau/sides;vs.append(c+radius*(normal*math.cos(angle)+side*math.sin(angle)))
    fs.append(tuple(start+k for k in range(sides-1,-1,-1)))
    for j in range(len(centers)-1):
     for k in range(sides):
      q=start+j*sides+k;n=start+j*sides+(k+1)%sides;fs.append((q,n,n+sides,q+sides))
    fs.append(tuple(start+(len(centers)-1)*sides+k for k in range(sides)))
   # Two restrained waves carry paired curled leaves between the brackets.
   tube([(.055+.89*j/96,.50+.105*math.sin(j/96*math.tau*2)) for j in range(97)])
   for u,sign in [(.13,1),(.25,-1),(.37,1),(.58,-1),(.70,1),(.82,-1)]:
    v=.50+.105*math.sin((u-.055)/.89*math.tau*2);start=len(vs);nu,nv=16,6
    for front in [True,False]:
     for i in range(nu+1):
      t=i/nu;shape=math.sin(math.pi*t)**.7
      for j in range(nv+1):
       s=j*2/nv-1
       x=u+.085*t+.011*math.sin(math.pi*t)+s*.025*max(.025,shape)
       y=v+sign*(.22*t-.06*t*t)+s*.065*shape
       h=.0005+.006*shape*(1-.85*abs(s)**1.5) if front else -.0008
       vs.append(point(x,y,h))
    count=(nu+1)*(nv+1)
    for i in range(nu):
     for j in range(nv):
      q=start+i*(nv+1)+j;fs.extend([(q,q+1,q+nv+2,q+nv+1),(q+count,q+nv+1+count,q+nv+2+count,q+1+count)])
    rim=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
    for j,q in enumerate(rim):
     n=rim[(j+1)%len(rim)];fs.append((start+q,start+q+count,start+n+count,start+n))
   g=bpy.data.meshes.new('Seated scroll foliage');g.from_pydata(vs,[],fs);g.update()
   bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
   o=bpy.data.objects.new('Caisson vines | tier %d face %d'%(tier+1,edge+1),g);bpy.context.collection.objects.link(o);g.materials.append(gold)
   o['sanctuary_interior']=True;o['caisson_vines']=True;o['tier']=tier;o['edge']=edge
   uv=g.uv_layers.new(name='Physical gilt grain')
   for p in g.polygons:
    p.use_smooth=True
    for li in p.loop_indices:
     v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(tangent)*.7,v.dot(across)*.7)
   parts.append(o)
 return parts
