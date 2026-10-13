"""Replace only the seven offering cups in both editable native scenes."""
import bpy,bmesh,sys,json,shutil,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from offering_cups import build_offering_cups,is_offering_cup,SUPPORT_TOP

def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if is_offering_cup(o):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
   for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(str(tuple(p.co)).encode())
 return count,h.hexdigest()
prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend';reports=[]
for path in [prototype,temple]:
 backup=path.with_name(path.stem+'-before-offering-cups.blend')
 if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(prototype));before=signature()
for o in list(bpy.data.objects):
 if is_offering_cup(o):bpy.data.objects.remove(o,do_unlink=True)
parts,materials,details=build_offering_cups();bpy.context.view_layer.update();assert signature()==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));bpy.ops.wm.open_mainfile(filepath=str(prototype));assert signature()==before
names=[o.name for o in bpy.data.objects if o.get('crafted_offering_cup')];component_count=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)
reports.append({'file':str(prototype),'preservedOtherObjects':before[0]})
bpy.ops.wm.open_mainfile(filepath=str(temple));before=signature()
for o in list(bpy.data.objects):
 if is_offering_cup(o):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();assert signature()==before;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert signature()==before
reports.append({'file':str(temple),'preservedOtherObjects':before[0]})
for o in bpy.data.objects:
 if not o.get('crafted_offering_cup'):continue
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-12 for f in bm.faces),o.name;bm.free()
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 if 'closed porcelain bowl' in o.name:
  assert abs(min((o.matrix_world@v.co).z for v in o.data.vertices)-SUPPORT_TOP)<1e-6
  # Read the actual native table below the bare foot, not only declared metadata.
  origin=Vector((o.location.x+.065,o.location.y,2.0));hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,Vector((0,0,-1)));assert hit[0] and abs(hit[1].z-SUPPORT_TOP)<1e-5,(o.name,hit)
report={'files':reports,'parts':len(names),'allClosedPositiveVolume':True,'actualTableContact':True,'otherGeometryAndTransformsPreserved':True};(R/'evidence/offering-cups-native.json').write_text(json.dumps(report,indent=2));print('CUPS NATIVE',report,flush=True)
# Export the full sanctuary by material; multi-material foot faces remain attached.
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
materials=set(o.data.materials[0] for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['components']=component_count;meta['offeringCups']=details;p.write_text(json.dumps(meta,indent=2))
print('CUPS EXPORTED',component_count,flush=True)
