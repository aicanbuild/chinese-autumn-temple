import bpy,bmesh,sys,hashlib,array,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from altar_brocade import build_altar_brocade

def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('altar_brocade'):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result
reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-altar-brocade.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 for o in list(bpy.data.objects):
  if o.get('altar_brocade'):bpy.data.objects.remove(o,do_unlink=True)
 parts=build_altar_brocade();bpy.context.view_layer.update();assert signatures()==before
 for o in parts:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert abs(bm.calc_volume(signed=True))>1e-5;bm.free()
  # Horizontal fabric is above the unchanged table; apron drape is in front.
  assert min(v.co.z for v in o.data.vertices)>1.47
  assert all(v.co.z>=1.9468 or v.co.y<7.711 for v in o.data.vertices)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
 reports.append({'file':filename,'preservedObjects':len(before),'addedRunners':2,'closedCloth':True});print('VERIFIED',reports[-1],flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('altar_brocade'):o.select_set(True)
layout_path=R/'dist/assets/sanctuary.json';layout=json.loads(layout_path.read_text());layout['components']=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects);layout['altarBrocade']={'runners':2,'width':.6,'fabricThickness':.0008,'asset':'altar-brocade.glb'};layout_path.write_text(json.dumps(layout,indent=2))
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/altar-brocade.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/altar-brocade-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False))
