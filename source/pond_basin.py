"""Native Z-up sediment basin and support placement shared by asset builders."""
import math
RADIUS_X=11.5;RADIUS_Y=6.9;CENTER_Y=-5.8;EDGE=.985
def basin_height(x,y):
 r=min(1,math.hypot(x/RADIUS_X,(y-CENTER_Y)/RADIUS_Y)/EDGE)
 t=max(0,min(1,(r-.28)/.72));s=t*t*(3-2*t)
 return -.98-.58*(1-s)+.022*math.sin(.75*x+.4*y)*math.sin(.5*y-.23*x)*(1-r*r)

def basin_mesh():
 import bpy,bmesh
 rings,sectors=48,192;vs=[(0,CENTER_Y,basin_height(0,CENTER_Y))];fs=[]
 for i in range(1,rings+1):
  r=EDGE*i/rings
  for j in range(sectors):
   a=j*math.tau/sectors;x=RADIUS_X*r*math.cos(a);y=CENTER_Y+RADIUS_Y*r*math.sin(a);vs.append((x,y,basin_height(x,y)))
 for j in range(sectors):fs.append((0,1+j,1+(j+1)%sectors))
 for i in range(rings-1):
  for j in range(sectors):q=1+i*sectors+j;q2=1+i*sectors+(j+1)%sectors;fs.append((q,q+sectors,q2+sectors,q2))
 bottom=len(vs)
 for j in range(sectors):x,y,z=vs[1+(rings-1)*sectors+j];vs.append((x,y,-1.84))
 center=len(vs);vs.append((0,CENTER_Y,-1.84))
 for j in range(sectors):
  a=1+(rings-1)*sectors+j;b=1+(rings-1)*sectors+(j+1)%sectors
  fs.extend([(a,b,bottom+(j+1)%sectors,bottom+j),(center,bottom+(j+1)%sectors,bottom+j)])
 m=bpy.data.meshes.new('Pond | gently contoured sediment');m.from_pydata(vs,[],fs);m.update()
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
 uv=m.uv_layers.new()
 for p in m.polygons:
  p.use_smooth=p.center.z> -1.75 and p.normal.z>.1
  for li in p.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=((v.x+15)*7/30,(v.y+15)*7/18)
 return m

def seat_stone(o,embed=.010):
 from mathutils import Vector
 rotation=o.rotation_euler.to_matrix()
 points=[rotation@Vector((v.co.x*o.scale.x,v.co.y*o.scale.y,v.co.z*o.scale.z)) for v in o.data.vertices]
 o.location.z=max(basin_height(o.location.x+v.x,o.location.y+v.y)-v.z for v in points)-embed
 return o.location.z

def extend_pier(o):
 from mathutils import Vector
 points=[o.matrix_world@v.co for v in o.data.vertices];old=min(p.z for p in points)
 x=sum(p.x for p in points)/len(points);y=sum(p.y for p in points)/len(points)
 target=basin_height(x,y)-.12;delta=target-old;inverse=o.matrix_world.inverted()
 for v,p in zip(o.data.vertices,points):
  if p.z<old+.020:v.co=inverse@(p+Vector((0,0,delta)))
 # Preserve the physical grain pitch along the extended vertical faces.
 for uv in o.data.uv_layers:
  for poly in o.data.polygons:
   if abs(poly.normal.z)>.7:continue
   for li in poly.loop_indices:
    i=o.data.loops[li].vertex_index
    if points[i].z<old+.020:uv.data[li].uv.x+=delta*.38
 o.data.update();o['basin_pier_bottom']=target
 return {'x':x,'y':y,'oldBottom':old,'bottom':target,'top':max(p.z for p in points)}
