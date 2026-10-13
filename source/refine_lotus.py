"""Replace only altar bouquet geometry, preserving sculpture and furnishings."""
import bpy,sys,json,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from lotus_bouquet import build_lotus_bouquets

def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.name.startswith('Lotus |'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return count,h.hexdigest()
prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend'
for f in [prototype,temple]:
 backup=f.with_name(f.stem+'-before-lotus.blend')
 if not backup.exists():shutil.copy2(f,backup)
bpy.ops.wm.open_mainfile(filepath=str(prototype));before=signature()
for o in list(bpy.data.objects):
 if o.name.startswith('Lotus |'):bpy.data.objects.remove(o,do_unlink=True)
for m in list(bpy.data.materials):
 if any(m.name.startswith('Sanctuary | '+label) for label in ['living lotus petals','living lotus leaves','lotus pollen and seed heart']):bpy.data.materials.remove(m)
parts,materials=build_lotus_bouquets();assert signature()==before
component_count=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));bpy.ops.wm.open_mainfile(filepath=str(prototype));assert signature()==before
names=[o.name for o in bpy.data.objects if o.get('lotus_bouquet')]
bpy.ops.wm.open_mainfile(filepath=str(temple));before=signature()
for o in list(bpy.data.objects):
 if o.name.startswith('Lotus |'):bpy.data.objects.remove(o,do_unlink=True)
for m in list(bpy.data.materials):
 if any(m.name.startswith('Sanctuary | '+label) for label in ['living lotus petals','living lotus leaves','lotus pollen and seed heart']):bpy.data.materials.remove(m)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
assert signature()==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert signature()==before
report={'nonBouquetGeometryPreserved':True,'preservedObjects':before[0],'bouquetParts':len(names),'sanctuaryComponents':component_count}
(R/'evidence/lotus-native.json').write_text(json.dumps(report,indent=2))
# Export only the sanctuary, merging meshes by material.
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
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
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['components']=component_count;meta['lotusRevision']=1;meta['lotusBotany']={'openFlowers':6,'buds':4,'peltateLeaves':6,'petals':120,'stamens':288};p.write_text(json.dumps(meta,indent=2));print('LOTUS PRESERVATION',report,flush=True)
