"""Replace only ceiling flower carvings; preserve and reopen both native projects."""
import bpy,bmesh,sys,json,shutil,hashlib,math,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from ceiling_carving import build_ceiling_carving,is_ceiling_carving,support_height
prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend'
def signature():
 out={}
 for o in bpy.data.objects:
  if is_ceiling_carving(o):continue
  h=hashlib.sha256();h.update(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for collection,prop,width,code in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    values=array.array(code,[0])*(len(collection)*width);collection.foreach_get(prop,values);h.update(values.tobytes())
   for uv in o.data.uv_layers:
    values=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',values);h.update(values.tobytes())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(array.array('f',p.co).tobytes())
  out[o.name]=h.hexdigest()
 return out
def verify():
 parts=[o for o in bpy.data.objects if o.get('ceiling_carving')];triangles=0;contacts=0
 assert len(parts)==367,len(parts)
 for o in parts:
  bm=bmesh.new();bm.from_mesh(o.data)
  assert all(e.is_manifold for e in bm.edges),o.name
  assert bm.calc_volume(signed=True)>0,o.name
  assert all(f.calc_area()>1e-12 for f in bm.faces),o.name
  bm.free();assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  back=o['back_grid_count']
  if back:
   for v in list(o.data.vertices)[back:]:
    assert abs(v.co.z-support_height(o['ceiling_field'],v.co.x,v.co.y)-.002)<2e-6,(o.name,tuple(v.co));contacts+=1
  triangles+=sum(len(p.vertices)-2 for p in o.data.polygons)
 return {'parts':len(parts),'triangles':triangles,'backContactVertices':contacts,'closedPositiveVolumes':True}
for f in [prototype,temple]:
 backup=f.with_name(f.stem+'-before-ceiling-carving.blend')
 if not backup.exists():shutil.copy2(f,backup)
bpy.ops.wm.open_mainfile(filepath=str(prototype));before=signature();old=sum(is_ceiling_carving(o) for o in bpy.data.objects)
for o in list(bpy.data.objects):
 if is_ceiling_carving(o):bpy.data.objects.remove(o,do_unlink=True)
parts,details=build_ceiling_carving();bpy.context.view_layer.update();assert signature()==before;verify()
component_count=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));bpy.ops.wm.open_mainfile(filepath=str(prototype));assert signature()==before;verify()
names=[o.name for o in bpy.data.objects if o.get('ceiling_carving')]
bpy.ops.wm.open_mainfile(filepath=str(temple));before=signature()
for o in list(bpy.data.objects):
 if is_ceiling_carving(o):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();assert signature()==before;verify()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert signature()==before
report=verify();report.update({'removedParts':old,'preservedOtherObjects':len(before),'geometryTransformsUVsPreserved':True})
(R/'evidence/ceiling-carving-native.json').write_text(json.dumps(report,indent=2));print('CEILING NATIVE',report,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
materials=set(o.data.materials[0] for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m];bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['components']=component_count;meta['ceilingCarving']=details;p.write_text(json.dumps(meta,indent=2));print('CEILING EXPORTED',component_count,flush=True)
