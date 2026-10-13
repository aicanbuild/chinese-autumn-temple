"""Original solid lotus carvings for the existing ceiling and caisson fields.

Context, not copied geometry or textures:
https://caea.lib.uchicago.edu/dcadp/zh/zhihuasi/ceilings/
https://www.dpm.org.cn/collection/ceramic/226778.html
These are contemporary original ornaments, not a reconstruction of either object.
"""
import bpy,bmesh,math

PREFIXES=('Ceiling | lotus rosette','Ceiling | rear return lotus','Caisson | corner gilt lotus',
 'Caisson | central gilded lotus','Caisson | layered lotus inner whorl',
 'Caisson | lotus heart whorl','Caisson | small lotus crown')
def is_ceiling_carving(o):
 return bool(o.get('ceiling_carving')) or o.name.startswith(PREFIXES)

def support_height(kind,x,y):
 if kind=='coffer':return 4.305
 if kind=='rear':return 4.31
 if kind=='corner':return 4.36
 r=math.hypot(x,y-7.1)
 profile=[(0,5.74),(.78,5.70),(.99,5.59),(1.08,5.43)]
 for (r0,z0),(r1,z1) in zip(profile,profile[1:]):
  if r<=r1:return z0+(z1-z0)*(r-r0)/(r1-r0)
 return 5.43

def build_ceiling_carving():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'))
 ivory=next((m for m in used if m.name.startswith('Sanctuary | ivory lotus petals')),None)
 if ivory is None:ivory=bpy.data.materials['Sanctuary | ivory lotus petals']
 parts=[];motifs=[]
 def mesh(name,vs,faces,mat,kind,back_count=0):
  g=bpy.data.meshes.new(name);g.from_pydata(vs,[],faces);g.update()
  bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
  o=bpy.data.objects.new('Ceiling carving | '+name,g);bpy.context.collection.objects.link(o);g.materials.append(mat)
  o['sanctuary_interior']=True;o['ceiling_carving']=True;o['ceiling_field']=kind;o['back_grid_count']=back_count;parts.append(o)
  uv=g.uv_layers.new()
  for p in g.polygons:
   p.use_smooth=True
   for li in p.loop_indices:
    v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.5,v.y*.7)
  return o
 def flower(x,y,z,r,n,kind,mat=gold,phase=0):
  first=len(parts);nu,nv=24,8
  for k in range(n):
   a=k*math.tau/n+phase;vs=[];faces=[]
   for front in [True,False]:
    for i in range(nu+1):
     t=i/nu;wave=math.sin(math.pi*t);d=r*(.075+.925*t)
     width=r*.235*max(.020,wave**.68)
     for j in range(nv+1):
      s=2*j/nv-1;u=x+d*math.cos(a)-s*width*math.sin(a);v=y+d*math.sin(a)+s*width*math.cos(a)
      back=support_height(kind,u,v)+.002
      # Cambered petal, gently turned tip, rounded raised edge and three incised veins.
      relief=r*(.125*wave**.65*(1-.74*s*s)+.026*t**6)
      rim=r*.012*math.exp(-((abs(s)-.82)/.17)**2)*wave
      veins=r*.006*wave*(math.exp(-(s/.12)**2)+.55*math.exp(-((abs(s)-.5)/.12)**2))
      zz=min(z,back-.012)-.004-relief-rim+veins if front else back
      vs.append((u,v,zz))
   count=(nu+1)*(nv+1)
   for i in range(nu):
    for j in range(nv):
     q=i*(nv+1)+j;faces.extend([(q,q+1,q+nv+2,q+nv+1),(q+count,q+nv+1+count,q+nv+2+count,q+1+count)])
   edge=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
   for j,q in enumerate(edge):q2=edge[(j+1)%len(edge)];faces.append((q,q+count,q2+count,q2))
   mesh('cambered lotus petal',vs,faces,mat,kind,count)
  # Closed round boss, with one vertex at each pole and its back seated in the field.
  top=support_height(kind,x,y)+.002;bottom=z-max(.020,r*.07);rz=(top-bottom)/2;mid=(top+bottom)/2
  vs=[(x,y,bottom)];faces=[];sides,rows=24,12
  for i in range(1,rows):
   ph=-math.pi/2+math.pi*i/rows
   for j in range(sides):
    a=j*math.tau/sides;vs.append((x+r*.13*math.cos(ph)*math.cos(a),y+r*.13*math.cos(ph)*math.sin(a),mid+rz*math.sin(ph)))
  vs.append((x,y,top));pole=len(vs)-1
  for j in range(sides):faces.extend([(0,1+(j+1)%sides,1+j),(pole,1+(rows-2)*sides+j,1+(rows-2)*sides+(j+1)%sides)])
  for i in range(rows-2):
   for j in range(sides):q=1+i*sides+j;q2=1+i*sides+(j+1)%sides;faces.append((q,q2,q2+sides,q+sides))
  mesh('lotus central boss',vs,faces,mat,kind)
  motifs.append({'field':kind,'center':[x,y,z],'radius':r,'petals':n,'parts':len(parts)-first})
 for x in [-4.45,-3.05,3.05,4.45]:
  for y in [5.95,7.22,8.49,9.76]:flower(x,y,4.294,.37,8,'coffer')
 for x in [-1.8,-.6,.6,1.8]:flower(x,10,4.295,.22,8,'rear')
 for sx in [-1,1]:
  for sy in [-1,1]:flower(sx*1.92,7.1+sy*1.92,4.345,.21,8,'corner')
 flower(0,7.1,5.68,.79,16,'well')
 flower(0,7.1,5.53,.46,12,'well',phase=math.pi/12)
 flower(0,7.1,5.44,.23,8,'well',ivory,math.pi/8)
 for i in range(16):
  a=i*math.tau/16;flower(math.cos(a)*.92,7.1+math.sin(a)*.92,5.46,.10,6,'well',ivory,a)
 return parts,{'revision':1,'motifs':len(motifs),'petals':sum(m['petals'] for m in motifs),'parts':len(parts),'closedReliefs':True,'supportOverlapMeters':.002,'fields':motifs}
