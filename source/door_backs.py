"""Original interior linings for the four existing opaque lattice door leaves.

Native Z-up. The existing exterior face and solid backing are retained.
Members project inward from the measured back plane y=5.165 m.
"""
import bpy,bmesh,math
from mathutils import Vector
from altar_carving import build_altar_carving
CENTERS=[-4.35,-2.88,2.88,4.35]

def build_door_backs():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 def material(name):return next(m for m in used if m.name.startswith('Sanctuary | '+name))
 wood,dark,gold=[material(n) for n in ['oxblood lacquer','carved rosewood','hand burnished gold']]
 parts=[]
 def register(o,name):
  o.name='Door back | '+name;o['door_back']=True;o['door_index']=index;o['sanctuary_interior']=True;parts.append(o);return o
 def box(name,center,size,mat,angle=0,grain=2,bevel=.002):
  a,b,c=[v/2 for v in size];g=bpy.data.meshes.new(name)
  g.from_pydata([(i*a,j*b,k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);g.update()
  o=bpy.data.objects.new(name,g);bpy.context.collection.objects.link(o);o.location=center;o.rotation_euler.y=angle;o.data.materials.append(mat)
  uv=o.data.uv_layers.new(name='Member grain')
  for p in o.data.polygons:
   axes=[i for i in range(3) if abs(p.normal[i])<.9];a=grain if grain in axes else axes[0];b=next(i for i in axes if i!=a)
   for li in p.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[a]*.5+index*.217,v[b]*.7+.31)
  bm=bmesh.new();bm.from_mesh(g);bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bevel,min(size)*.22),segments=3,affect='EDGES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free();g.update()
  for p in o.data.polygons:p.use_smooth=max(abs(c) for c in p.normal)<.999
  return register(o,name)
 def frame(name,x,z,w,h,mat,width=.022,depth=.022,y=5.21):
  for side in [-1,1]:
   box(name+' stile',(x+side*(w-width)/2,y,z),(width,depth,h),mat)
   box(name+' rail',(x,y,z+side*(h-width)/2),(w-width*2,depth,width),mat,grain=0)
 for index,x in enumerate(CENTERS):
  # The 2 mm inset penetrates the old backing and cannot float off the door.
  box('continuous lacquer lining',(x,5.172,2.53),(1.316,.018,2.866),wood,bevel=.001)
  frame('outer rosewood frame',x,2.53,1.316,2.866,dark,width=.064,depth=.052,y=5.192)
  frame('gilt inset bead',x,2.53,1.182,2.728,gold,width=.003,depth=.004,y=5.207)
  # Solid recessed upper field: this is carved/assembled wood, not fake glass.
  box('recessed upper field',(x,5.186,3.035),(1.166,.016,1.57),dark,bevel=.001)
  frame('upper moulding',x,3.035,1.172,1.58,wood,width=.025,depth=.025,y=5.199)
  # Closed diamond cells. Each joint terminates at the same node; alternating
  # corners receive small gilt pins, leaving the wood dominant at close range.
  for row in range(5):
   for col in range(4):
    cx=x+(col-1.5)*.278;cz=3.035+(row-2)*.292
    pts=[(cx,cz+.146),(cx+.139,cz),(cx,cz-.146),(cx-.139,cz)]
    for i,(ax,az) in enumerate(pts):
     bx,bz=pts[(i+1)%4];dx=bx-ax;dz=bz-az
     box('diamond lattice member',((ax+bx)/2,5.211,(az+bz)/2),(.017,.028,math.hypot(dx,dz)),wood,angle=math.atan2(dx,dz),bevel=.001)
    if (row+col)%2==0:box('gilt square pin',(cx,5.226,cz+.146),(.012,.006,.012),gold,angle=math.pi/4,bevel=.001)
  for z in [2.18,3.91]:box('cross rail',(x,5.208,z),(1.192,.055,.073),dark,grain=0,bevel=.003)
  box('lower carved field',(x,5.184,1.685),(1.168,.014,.86),wood,bevel=.001)
  frame('lower moulding',x,1.685,1.174,.866,dark,width=.032,depth=.036,y=5.204)
  frame('lower gilt inlay',x,1.685,1.09,.782,gold,width=.003,depth=.004,y=5.223)
  # Reuse the temple's original closed lotus relief, scaled to the door field.
  relief,_=build_altar_carving()
  for o in relief:
   if o['altar_panel_index']!=1:bpy.data.objects.remove(o,do_unlink=True);continue
   for v in o.data.vertices:
    q=v.co.copy();v.co=(x+q.x*1.1,5.189+(7.848-q.y)*.65,1.685+(q.z-1.42)*1.55)
   # Reflection reverses winding; restore outward normals for closed solids.
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   for key in ['altar_relief','altar_panel_index']:
    if key in o:del o[key]
   register(o,'lotus skirt carving')
 return parts
