"""Apply the native wax finish and export only the existing sanctuary asset."""
import bpy,sys,json,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from candle_finish import finish_candles

def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.name.startswith('Candle | red wax') or o.name.startswith('Candle | accumulated wax drip'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return count,h.hexdigest()

prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend'
for f,label in [(prototype,'sanctuary'),(temple,'temple')]:
 backup=f.with_name(f.stem+'-before-wax.blend')
 if not backup.exists():shutil.copy2(f,backup)
 bpy.ops.wm.open_mainfile(filepath=str(f));before=signature();report=finish_candles(list(bpy.data.objects));assert report['bodies']==4 and report['drips'] in [0,28];assert signature()==before
 bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.wm.open_mainfile(filepath=str(f));assert signature()==before
 if label=='temple':
  report.update(nonCandleGeometryPreserved=True,preservedObjects=before[0]);(R/'evidence/candle-native.json').write_text(json.dumps(report,indent=2))
# Export the prototype using its existing fifteen material batches.
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')];assert len(parts)==json.loads((R/'dist/assets/sanctuary.json').read_text())['components']
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
materials=set(m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
print('CANDLE FINISH VERIFIED',report,flush=True)
