"""Profile the remaining box-section caisson frames and slender octagonal fillets.
Runs after cloud carving; preserves every other mesh, UV and object transform.
"""
import bpy,bmesh,math,json,shutil,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
PREFIX=('Caisson | deep','Ceiling | lacquer coffer rim','Caisson | octagonal gilt moulding','Caisson | frame fine inlay')
def chosen(o):return o.type=='MESH' and o.name.startswith(PREFIX)
def ceiling(o):return o.type in {'MESH','CURVE'} and (o.name.startswith(('Caisson |','Dougong |','Ceiling |')) or o.get('ceiling_carving')) and not o.get('caisson_vines')
def signature():
 result={}
 for o in bpy.data.objects:
  if chosen(o):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for coll,prop,width,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(typ,[0])*(len(coll)*width);coll.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

def mesh_for(o,verts,faces):
 m=bpy.data.meshes.new(o.name+' | milled profile');inv=o.matrix_world.inverted();m.from_pydata([inv@Vector(v) for v in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(m);bm.free()
 uv=m.uv_layers.new(name='Fine grain')
 for p in m.polygons:
  for li in p.loop_indices:
   v=Vector(verts[m.loops[li].vertex_index]);uv.data[li].uv=(v.x*.7+v.y*.3,v.z*.7+v.y*.4)
 o.data=m
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 bevel=o.modifiers.new('Small rolled arris','BEVEL');bevel.width=.001;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.18
 normal=o.modifiers.new('Moulded plane normals','WEIGHTED_NORMAL');normal.keep_sharp=True
 o['fine_moulding_revision']=1

reports=[];backupdir=R/'evidence/mouldings-original';backupdir.mkdir(exist_ok=True)
asset=R/'dist/assets/fine-caisson.glb'
if not (backupdir/asset.name).exists():shutil.copy2(asset,backupdir/asset.name)
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-profiled-mouldings.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature()
 frames=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(PREFIX[:2])];assert len(frames)==68,len(frames)
 gold=next(o.data.materials[0] for o in bpy.data.objects if o.name.startswith('Caisson | octagonal gilt moulding'))
 # A spreading crown, recessed neck and rolled lower lip replace the slab side.
 profile=[(0,.70),(.045,.76),(.11,.80),(.17,.80),(.24,.72),(.31,.60),(.48,.58),(.59,.65),(.68,.78),(.74,.88),(.81,.88),(.87,.96),(.95,1),(1,1)]
 for o in frames:
  if o.get('fine_moulding_revision'):continue
  points=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[a] for v in points) for a in range(3)];hi=[max(v[a] for v in points) for a in range(3)];axis=0 if hi[0]-lo[0]>hi[1]-lo[1] else 1;across=1-axis;mid=(lo[across]+hi[across])/2;half=(hi[across]-lo[across])*.5*.82;h=(hi[2]-lo[2])*.8;bottom=hi[2]-h
  section=[(-w*half,bottom+t*h) for t,w in profile]+[(w*half,bottom+t*h) for t,w in reversed(profile)];n=len(section);verts=[]
  for end in [lo[axis],hi[axis]]:
   for width,z in section:
    p=[0,0,z];p[axis]=end;p[across]=mid+width;verts.append(p)
  faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh_for(o,verts,faces)
  # Hairline gilding is seated within the lower lip, not a floating ornament.
  for side in [-1,1]:
   center=Vector((0,0,bottom+h*.16));center[across]=mid+side*half*.79
   verts=[];faces=[];radius=.00135
   for end in [lo[axis]+.003,hi[axis]-.003]:
    for k in range(8):
     p=center.copy();p[axis]=end;p[across]+=radius*math.cos(k*math.tau/8);p.z+=radius*math.sin(k*math.tau/8);verts.append(tuple(p))
   faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
   me=bpy.data.meshes.new('Fine inset gilding');g=bpy.data.objects.new('Caisson | frame fine inlay',me);bpy.context.collection.objects.link(g);me.materials.append(gold);mesh_for(g,verts,faces);g['sanctuary_interior']=True
 bands=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Caisson | octagonal gilt moulding')]
 # Keep original continuous paths; shrink only the round wire cross section.
 levels=[(2.48,4.36),(2.15,4.61),(1.79,4.89),(1.43,5.16),(1.08,5.43)]
 paths=[(r,z) for k in range(4) for r,z in [levels[k],(levels[k][0]-.065,levels[k][1]+.05),levels[k+1]]]
 seen=set();removed=0
 for o in bands:
  if o.get('fine_moulding_revision'):continue
  points=[o.matrix_world@v.co for v in o.data.vertices];zc=sum(p.z for p in points)/len(points)
  def nearest(p,r,z):
   corners=[Vector((r*math.cos(math.pi/8+j*math.tau/8),7.1+r*math.sin(math.pi/8+j*math.tau/8),z)) for j in range(8)];qs=[]
   for j,a in enumerate(corners):
    d=corners[(j+1)%8]-a;qs.append(a+d*max(0,min(1,(p-a).dot(d)/d.length_squared)))
   return min(qs,key=lambda q:(p-q).length_squared)
  r,z=min(paths,key=lambda rz:sum((p-nearest(p,*rz)).length_squared for p in points[::max(1,len(points)//24)]))
  key=(r,z)
  if key in seen:bpy.data.objects.remove(o,do_unlink=True);removed+=1;continue
  seen.add(key);inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;q=nearest(p,r,z);v.co=inv@(q+(p-q)*.55)
  o['fine_moulding_revision']=1
 bpy.context.view_layer.update();assert signature()==before
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 reports.append({'file':filename,'profiledFrames':68,'fineInlays':136,'uniqueOctagonalFillets':sum(o.type=='MESH' and o.name.startswith('Caisson | octagonal gilt moulding') for o in bpy.data.objects),'duplicateRingsRemoved':removed,'frameDepthFactor':.8,'frameWidthFactor':.82,'filletRadiusFactor':.55,'preservedObjects':len(before)})
 if filename=='庄严内殿.blend':
  bpy.ops.object.select_all(action='DESELECT');parts=[o for o in bpy.data.objects if ceiling(o)]
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');groups={}
  for o in bpy.context.selected_objects:groups.setdefault(o.data.materials[0],[]).append(o)
  exports=[]
  for mat,group in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Fine caisson | '+mat.name;o['sourceMaterial']=mat.name;exports.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for o in exports:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18,export_draco_normal_quantization=14)
(R/'evidence/caisson-mouldings-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('PROFILED MOULDINGS',reports,flush=True)
