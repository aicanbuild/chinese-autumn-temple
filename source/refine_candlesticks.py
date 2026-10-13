"""Replace stands, preserving all existing wax, wicks, bouquets and temple geometry."""
import bpy,sys,json,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from candlesticks import build_candlesticks,is_stand

def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if is_stand(o):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(str(tuple(p.co)).encode());h.update(str(p.radius).encode())
 return count,h.hexdigest()
prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend'
for f in [prototype,temple]:
 backup=f.with_name(f.stem+'-before-candlesticks.blend')
 if not backup.exists():shutil.copy2(f,backup)
bpy.ops.wm.open_mainfile(filepath=str(prototype));before=signature()
for o in list(bpy.data.objects):
 if is_stand(o):bpy.data.objects.remove(o,do_unlink=True)
parts,materials,details=build_candlesticks();bpy.context.view_layer.update();assert signature()==before
component_count=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));bpy.ops.wm.open_mainfile(filepath=str(prototype));assert signature()==before
names=[o.name for o in bpy.data.objects if o.get('crafted_candlestick')]
bpy.ops.wm.open_mainfile(filepath=str(temple));before=signature()
for o in list(bpy.data.objects):
 if is_stand(o):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();assert signature()==before;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert signature()==before
# Verify actual support contact and closed, finite modelling in the native file.
import bmesh,math
for i,stand in enumerate(details['stands']):
 group=[o for o in bpy.data.objects if o.get('crafted_candlestick') and o['candlestick_index']==i];assert len(group)==stand['parts']
 body=next(o for o in group if o.name.startswith('Candle stand | shaped copper body'));points=[body.matrix_world@v.co for v in body.data.vertices];assert abs(min(p.z for p in points)-stand['supportTop'])<.000001
 socket=next(o for o in group if o.name.startswith('Candle stand | candle socket seat'));assert abs(max((socket.matrix_world@v.co).z for v in socket.data.vertices)-stand['candleBase'])<.000001
 for o in group:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert all(f.calc_area()>1e-12 for f in bm.faces),o.name;bm.free();assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
report={'nonStandGeometryPreserved':True,'preservedObjects':before[0],'stands':4,'parts':len(names),'allClosedSurfaces':True,'supportContactVerified':True,'waxWicksAndBouquetsPreserved':True};(R/'evidence/candlesticks-native.json').write_text(json.dumps(report,indent=2));print('CANDLESTICKS NATIVE',report,flush=True)
# Export the sanctuary in material batches, keeping all authored PBR nodes.
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');materials=set(m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['components']=component_count;meta['candlesticks']=details;p.write_text(json.dumps(meta,indent=2));print('CANDLESTICKS EXPORTED',component_count,flush=True)
