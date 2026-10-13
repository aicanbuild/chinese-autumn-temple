import bpy,bmesh,sys,hashlib,array,json,shutil,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from caisson_vines import build_caisson_vines

def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('caisson_vines'):continue
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
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-caisson-vines.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 for o in list(bpy.data.objects):
  if o.get('caisson_vines'):bpy.data.objects.remove(o,do_unlink=True)
 parts=build_caisson_vines();bpy.context.view_layer.update();assert signatures()==before
 triangles=0;vertex_count=0;max_offset=0
 soffits=sorted([o for o in bpy.data.objects if o.name.startswith('Caisson | inward stepped painted soffit')],key=lambda o:min(v.co.z for v in o.data.vertices))
 assert len(soffits)==4
 for o in parts:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0;bm.free()
  o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
  support=soffits[o['tier']];face=support.data.polygons[o['edge']];corners=[support.matrix_world@support.data.vertices[i].co for i in face.vertices]
  a,b,d=corners[0],corners[1],corners[-1];normal=(b-a).cross(d-a).normalized()
  if normal.z>0:normal=-normal
  for v in o.data.vertices:
   p=o.matrix_world@v.co;offset=(p-a).dot(normal);max_offset=max(max_offset,offset)
   assert -.0021<offset<.0066,(o.name,offset)
   projected=p-normal*offset
   # Every relief point projects inside its actual four-sided supporting board.
   signs=[(corners[(j+1)%4]-q).cross(projected-q).dot(normal) for j,q in enumerate(corners)]
   assert min(signs)>-1e-6 or max(signs)<1e-6,(o.name,signs)
   vertex_count+=1
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
 assert sum(bool(o.get('caisson_vines')) for o in bpy.data.objects)==32
 report={'file':filename,'preservedObjects':len(before),'panels':32,'triangles':triangles,'checkedSupportVertices':vertex_count,'maximumReliefMetres':max_offset,'closedSolids':True};reports.append(report);print('VERIFIED',report,flush=True)
 if filename=='庄严内殿.blend':
  meta_path=R/'dist/assets/sanctuary.json';meta=json.loads(meta_path.read_text());meta['components']=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects);meta['caissonVines']={'panels':32,'triangles':triangles,'asset':'caisson-vines.glb'};meta_path.write_text(json.dumps(meta,indent=2))
  bpy.ops.object.select_all(action='DESELECT');selected=[o for o in bpy.data.objects if o.get('caisson_vines')]
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();o=bpy.context.object;o.name='Caisson gilt foliage';o['sourceMaterial']=o.data.materials[0].name
  bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/caisson-vines.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/caisson-vines-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False))
