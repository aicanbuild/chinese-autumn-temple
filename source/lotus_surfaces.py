"""Editable, curved thin shells for the original altar lotus petals and leaves."""
import bpy,bmesh,math
from mathutils import Vector,Matrix

def is_flower_heart(o):
 return o.get('botanical_part')=='stamens' or o.get('flower_calyx') or o.name.startswith(('Lotus | flat seed receptacle','Lotus | receptacle stigma'))

def refine_flower_hearts(parts):
 flowers=[]
 for side in [-1,1]:
  for j,(dx,dy,z,opening) in enumerate([(-.13,-.11,3.04,1.),(.16,.05,3.21,.85),(-.12,.16,3.34,.53)]):
   phase=j*1.4+side*.3
   center=Vector((side*2.18+side*dx,8.48+dy,z+(.015 if side>0 else 0)))
   tilt=Matrix.Rotation(.32+.12*math.sin(phase),4,'X')@Matrix.Rotation(.14*math.cos(phase),4,'Y')
   flowers.append((center,tilt,[.026,.040,.085][j]))
 for o in parts:
  if not is_flower_heart(o) or o.get('lotus_heart_revision'):continue
  centroid=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  center,tilt,shift=min(flowers,key=lambda f:(centroid-f[0]).length)
  delta=o.matrix_world.inverted().to_3x3()@(tilt@Vector((0,0,shift)))
  for v in o.data.vertices:v.co+=delta
  o['lotus_heart_revision']=1;o['core_lift_m']=shift
 # A small closed green receptacle joins each stalk to the petal bases.
 existing=[o for o in parts if o.get('flower_calyx')]
 for center,tilt,shift in flowers:
  if any((Vector(o['flower_center'])-center).length<.001 for o in existing):continue
  profile=[(.003,0),(.004,.003),(.013,.008),(.024,.013),(.027,.018),(.023,.021)]
  vertices=[];faces=[];segments=48
  for radius,z in profile:
   for k in range(segments):
    a=k*math.tau/segments;vertices.append(tuple(center+tilt@Vector((radius*math.cos(a),radius*math.sin(a),z))))
  for j in range(len(profile)-1):
   for k in range(segments):a=j*segments+k;b=j*segments+(k+1)%segments;faces.append((a,b,b+segments,a+segments))
  faces.append(tuple(reversed(range(segments))));faces.append(tuple((len(profile)-1)*segments+k for k in range(segments)))
  mesh=bpy.data.meshes.new('Lotus calyx shell');mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(bpy.data.materials['Sanctuary | botanical stems'])
  o=bpy.data.objects.new('Lotus | small green calyx',mesh);bpy.context.collection.objects.link(o)
  for p in mesh.polygons:p.use_smooth=True
  o['flower_calyx']=True;o['flower_center']=tuple(center);o['lotus_bouquet']=True;o['sanctuary_interior']=True;o['lotus_heart_revision']=1;parts.append(o)

def refine_lotus_surfaces(parts):
 refine_flower_hearts(parts)
 changed=[]
 for o in parts:
  kind=o.get('botanical_part')
  if kind not in {'petal','leaf'} or o.get('lotus_surface_revision'):continue
  mesh=o.data
  if kind=='petal':
   assert len(mesh.vertices)==19*9
   for row in range(19):
    t=row/18;center=mesh.vertices[row*9+4].co.copy()
    for column in range(9):
     v=mesh.vertices[row*9+column]
     v.co=center+(v.co-center)*.88+Vector((0,0,.04*t**1.4))
  # Weld collapsed parametric poles before subdivision/solidification.
  bm=bmesh.new();bm.from_mesh(mesh)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('Continuous botanical curvature','SUBSURF');mod.levels=1;mod.render_levels=1
  bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Natural thin edge','SOLIDIFY');mod.thickness=.00045 if kind=='petal' else .00065;mod.offset=0;mod.use_even_offset=True
  bpy.ops.object.modifier_apply(modifier=mod.name)
  for p in mesh.polygons:p.use_smooth=True
  o['lotus_surface_revision']=1;o['surface_thickness_m']=.00045 if kind=='petal' else .00065
  changed.append(o)
 return changed
