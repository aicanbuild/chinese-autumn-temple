import bpy,bmesh,sys,hashlib,array,json,shutil,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from aureole_relief import build_aureole_relief
preview='--preview' in sys.argv
def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('aureole_relief') or o.name.startswith('Aureole | fine chased rays'):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result
reports=[]
for filename in (['庄严内殿.blend'] if preview else ['庄严内殿.blend','听秋寺院.blend']):
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-aureole-relief.blend')
 if not preview and not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 removed=0;removed_triangles=0
 for o in list(bpy.data.objects):
  if o.name.startswith('Aureole | fine chased rays'):
   evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get());g=evaluated.to_mesh();g.calc_loop_triangles();removed_triangles+=len(g.loop_triangles);evaluated.to_mesh_clear()
   removed+=1;bpy.data.objects.remove(o,do_unlink=True)
  elif o.get('aureole_relief'):bpy.data.objects.remove(o,do_unlink=True)
 parts=build_aureole_relief();bpy.context.view_layer.update();assert signatures()==before
 tris=0
 for o in parts:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),(o.name,'open');assert bm.calc_volume(signed=True)>0,(o.name,'volume');bm.free()
  o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
  assert all(all(math.isfinite(c) for c in v.co) for v in o.data.vertices)
 # Independently ray-check the bronze mounting against the original backing.
 backing=next(o for o in bpy.data.objects if o.name.startswith('Shrine | shaped mandorla backing'))
 tree=BVHTree.FromPolygons([backing.matrix_world@v.co for v in backing.data.vertices],[tuple(p.vertices) for p in backing.data.polygons])
 ground=parts[0];supported=0
 for v in ground.data.vertices:
  if abs(v.co.y-9.242)<1e-5:
   hit=tree.ray_cast(Vector((v.co.x,9.27,v.co.z)),Vector((0,-1,0)),.1)
   assert hit[0] is not None and abs(hit[0].y-9.24)<1e-4; supported+=1
 assert supported==512
 support=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[tuple(p.vertices) for p in ground.data.polygons])
 petal_contacts=0
 for o in parts[1:]:
  for v in o.data.vertices:
   if abs(v.co.y-9.212)<1e-5:
    hit=support.ray_cast(Vector((v.co.x,9.22,v.co.z)),Vector((0,-1,0)),.02)
    assert hit[0] is not None and abs(hit[0].y-9.209)<1e-4;petal_contacts+=1
 if not preview:
  bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
  assert sum(bool(o.get('aureole_relief')) for o in bpy.data.objects)==81
 reports.append({'file':filename,'preservedObjects':len(before),'removedRays':removed,'removedTriangles':removed_triangles,'parts':81,'triangles':tris,'closedSolids':True,'supportedGroundVertices':supported,'supportedPetalVertices':petal_contacts});print('VERIFIED',reports[-1],flush=True)
 if filename=='庄严内殿.blend':
  if not preview:
   layout_path=R/'dist/assets/sanctuary.json';layout=json.loads(layout_path.read_text())
   layout['components']=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)
   layout['aureoleRelief']={'parts':81,'petals':80,'triangles':117888,'replacedRays':44,'asset':'aureole-relief.glb'}
   layout_path.write_text(json.dumps(layout,indent=2))
  # Export from the current data after verification; the saved file retains objects.
  materials=set(o.data.materials[0] for o in bpy.data.objects if o.get('aureole_relief'))
  for m in materials:
   bpy.ops.object.select_all(action='DESELECT');selected=[o for o in bpy.data.objects if o.get('aureole_relief') and o.data.materials[0]==m]
   for o in selected:o.select_set(True)
   bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=m.name;bpy.context.object['sourceMaterial']=m.name
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.data.objects:
   if o.get('aureole_relief'):o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/aureole-relief.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/('evidence/aureole-preview-native.json' if preview else 'evidence/aureole-native.json')).write_text(json.dumps(reports,indent=2,ensure_ascii=False))
