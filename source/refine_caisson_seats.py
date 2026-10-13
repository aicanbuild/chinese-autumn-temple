"""Replace square caisson bearing blocks with closed, rounded, waisted woodwork.
Only 288 tagged bearing blocks are changed; all other native geometry is preserved.
"""
import bpy,bmesh,math,json,shutil,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def chosen(o):return o.type=='MESH' and o.name.startswith(('Dougong | seated dou block','Dougong | lower bearing block'))
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
reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-waisted-dou.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();parts=[o for o in bpy.data.objects if chosen(o)];assert len(parts)==288,len(parts)
 revised=0
 for o in parts:
  if o.get('waisted_dou_revision')==1:continue
  world=[o.matrix_world@v.co for v in o.data.vertices];edges=[world[e.vertices[1]]-world[e.vertices[0]] for e in o.data.edges];horizontal=[e for e in edges if abs(e.z)<1e-6];axis=max(horizontal,key=lambda e:e.length).normalized();cross=Vector((-axis.y,axis.x,0))
  us=[v.dot(axis) for v in world];vs=[v.dot(cross) for v in world];lo=min(v.z for v in world);hi=max(v.z for v in world);h=hi-lo
  center=axis*((min(us)+max(us))/2)+cross*((min(vs)+max(vs))/2);w=(max(us)-min(us))/2;d=(max(vs)-min(vs))/2
  # Lower heel, concave waist, spreading shoulder and subtly rolled top lip.
  profile=[(0,.63),(.025,.66),(.17,.68),(.26,.69),(.34,.72),(.52,.83),(.70,.96),(.77,1),(.89,1),(.965,.985),(1,.96)]
  verts=[];faces=[];radius=min(w,d)*.17;n=32
  for height,scale in profile:
   for corner in range(4):
    a0=corner*math.pi/2;sx=1 if corner in [0,3] else -1;sy=1 if corner<2 else -1
    for j in range(8):
     a=a0+j*math.pi/14;x=(sx*(w-radius)+radius*math.cos(a))*scale;y=(sy*(d-radius)+radius*math.sin(a))*scale
     p=center+axis*x+cross*y+Vector((0,0,lo+height*h));verts.append(tuple(o.matrix_world.inverted()@p))
  for row in range(len(profile)-1):
   for i in range(n):a=row*n+i;b=row*n+(i+1)%n;faces.append((a,b,b+n,a+n))
  faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
  mesh=bpy.data.meshes.new(o.name+' | rounded waisted profile');mesh.from_pydata(verts,[],faces);mesh.update()
  for m in o.data.materials:mesh.materials.append(m)
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free()
  uv=mesh.uv_layers.new(name='UVMap')
  for poly in mesh.polygons:
   poly.use_smooth=len(poly.vertices)==4
   for li in poly.loop_indices:
    p=o.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((p.dot(axis)-min(us))/(2*w),(p.z-lo)/h)
  o.data=mesh;o['waisted_dou_revision']=1;revised+=1
 bpy.context.view_layer.update();assert signature()==before
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 for o in bpy.data.objects:
  if chosen(o):
   bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.free()
 reports.append({'file':filename,'blocks':len(parts),'revised':revised,'preservedObjects':len(before),'closedPositiveVolumes':True})
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
  bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/fine-caisson.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18,export_draco_normal_quantization=14)
(R/'evidence/caisson-waisted-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('WAISTED DOU',reports,flush=True)
