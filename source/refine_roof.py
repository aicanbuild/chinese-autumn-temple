import bpy,sys,hashlib,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from roof_tiles import refine_roof_mesh
def roofs():return [o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name.startswith('Charcoal glazed ceramic') for m in o.data.materials)]
def signature():
 excluded=set(roofs());h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o in excluded:continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return count,h.hexdigest()
path=R/'source/听秋寺院.blend';backup=path.with_name(path.stem+'-before-roof-shells.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();objects=roofs();assert len(objects)==1
if objects[0].get('roof_shell_revision'):
 with bpy.data.libraries.load(str(backup),link=False) as (src,dst):dst.objects=[objects[0].name]
 original=dst.objects[0];objects[0].data=original.data;bpy.data.objects.remove(original,do_unlink=True);del objects[0]['roof_shell_revision']
report=refine_roof_mesh(objects[0]);assert signature()==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
o=roofs()[0];assert o.data.uv_layers.active and len(o.data.color_attributes)==1
report.update({'preservedObjects':before[0],'nonRoofGeometryPreserved':True})
# Keep an independently editable roof source and export only this one material batch.
for other in list(bpy.data.objects):
 if other!=o:bpy.data.objects.remove(other,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/精修筒瓦.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/roof-tiles.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'dist/assets/roof-tiles.json').write_text(json.dumps(report,indent=2));(R/'evidence/roof-shells-native.json').write_text(json.dumps(report,indent=2));print('ROOF SHELLS',report,flush=True)
