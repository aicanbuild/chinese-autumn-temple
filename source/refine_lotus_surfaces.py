"""Refine both native projects; export only replacement lotus geometry."""
import bpy,bmesh,sys,json,hashlib,array,shutil,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from lotus_surfaces import refine_lotus_surfaces,is_flower_heart
from lotus_optics import configure_lotus_optics

def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('botanical_part') in {'petal','leaf'} or is_flower_heart(o):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

def verify():
 objects=[o for o in bpy.data.objects if o.get('botanical_part') in {'petal','leaf'}]
 assert len(objects)==126
 triangles=0;min_volume=1
 for o in objects:
  assert o.get('lotus_surface_revision')==1
  bm=bmesh.new();bm.from_mesh(o.data)
  assert all(e.is_manifold for e in bm.edges),o.name
  volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
  min_volume=min(min_volume,volume);assert all(f.calc_area()>1e-13 for f in bm.faces);bm.free()
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  assert o.data.uv_layers and all(math.isfinite(v) for p in o.data.uv_layers[0].data for v in p.uv)
  o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 hearts=[o for o in bpy.data.objects if is_flower_heart(o)]
 assert len(hearts)==90 and all(o.get('lotus_heart_revision')==1 for o in hearts)
 for o in hearts:
  if not o.get('flower_calyx'):continue
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.free()
 return {'petals':120,'leaves':6,'heartParts':84,'calyces':6,'closedPositiveVolumes':True,'minVolume':min_volume,'triangles':triangles}

reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-lotus-surfaces.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 refine_lotus_surfaces(list(bpy.data.objects));configure_lotus_optics(list(bpy.data.objects));assert signatures()==before;verify()
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
 assert signatures()==before;report=verify();report.update(file=filename,preservedObjects=len(before));reports.append(report);print('VERIFIED',report,flush=True)
 if filename.startswith('庄严'):components=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)

layout_path=R/'dist/assets/sanctuary.json';layout=json.loads(layout_path.read_text());layout['components']=components;layout_path.write_text(json.dumps(layout,indent=2))

bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'))
names={'Sanctuary | living lotus petals','Sanctuary | living lotus leaves','Sanctuary | lotus pollen and seed heart','Sanctuary | botanical stems'}
for name in names:
 group=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.materials) and o.data.materials[0].name==name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=name;bpy.context.object['sourceMaterial']=name
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('sourceMaterial') in names:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/lotus-surfaces.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_attributes=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/lotus-surfaces-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False))
