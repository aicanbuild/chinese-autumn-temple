"""Original lotus/flame relief on the existing mandorla; native Z-up metres.

The accepted sculpture and old outline are untouched. The bronze annulus
penetrates the existing backing by 2 mm; each closed petal intersects it.
"""
import bpy,bmesh,math

def build_aureole_relief():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'))
 bronze=next(m for m in used if m.name.startswith('Sanctuary | antique gilt bronze'))
 parts=[]
 def point(a,r,y):return (1.06*r*math.sin(a)*(.85+.15*abs(math.sin(a))),y,2.93+1.18*r*math.cos(a))
 def mesh(name,vs,fs,material):
  g=bpy.data.meshes.new(name);g.from_pydata(vs,[],fs);g.update()
  bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
  o=bpy.data.objects.new('Aureole relief | '+name,g);bpy.context.collection.objects.link(o);g.materials.append(material)
  o['sanctuary_interior']=True;o['aureole_relief']=True
  uv=g.uv_layers.new(name='Physical gilt grain')
  for p in g.polygons:
   p.use_smooth=True
   for li in p.loop_indices:
    v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.7,v.z*.7)
  parts.append(o);return o
 # Four rings form a solid, softly crowned bronze support, with no open edge.
 n=256;vs=[];fs=[]
 for r,y in [(.735,9.242),(.735,9.209),(1.005,9.209),(1.005,9.242)]:
  for j in range(n):vs.append(point(j*math.tau/n,r,y))
 for i in range(4):
  for j in range(n):fs.append((i*n+j,i*n+(j+1)%n,((i+1)%4)*n+(j+1)%n,((i+1)%4)*n+j))
 mesh('continuous bronze ground',vs,fs,bronze)
 def petal(a,r0,r1,width,curl,depth,name):
  nu,nv=32,10;vs=[];fs=[]
  for front in [True,False]:
   for i in range(nu+1):
    t=i/nu;bulge=math.sin(math.pi*t)**.65
    # The tangent curl is strongest at the tapered tip, giving flowing flames.
    angle=a+curl*t*t;r=r0+(r1-r0)*t
    for j in range(nv+1):
     s=j*2/nv-1;w=width*max(.025,bulge)*(1-.25*t)
     rise=.0015+depth*bulge*(1-.83*abs(s)**1.5)
     rise-=.0016*math.exp(-s*s*90)*math.sin(math.pi*t)
     vs.append(point(angle+s*w,r,9.207-rise if front else 9.212))
  count=(nu+1)*(nv+1)
  for i in range(nu):
   for j in range(nv):
    q=i*(nv+1)+j;fs.extend([(q,q+1,q+nv+2,q+nv+1),(q+count,q+nv+1+count,q+nv+2+count,q+1+count)])
  edge=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
  for j,q in enumerate(edge):r=edge[(j+1)%len(edge)];fs.append((q,q+count,r+count,r))
  mesh(name,vs,fs,gold)
 for k in range(40):
  a=(k+.5)*math.tau/40;direction=1 if math.sin(a)>0 else -1
  petal(a,.815,1.0,.047,direction*.150,.020,'curled flame tongue')
  petal(a-math.pi/40,.748,.865,.048,-direction*.030,.009,'inner lotus petal')
 return parts
