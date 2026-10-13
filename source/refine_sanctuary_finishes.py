"""Preserve every object and mesh while refining only two sanctuary finishes."""
import bpy,sys,shutil,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from sanctuary_finishes import apply_sanctuary_finishes
def signature():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
   for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return len(bpy.data.objects),h.hexdigest()
reports=[]
for name in ['庄严内殿','听秋寺院']:
 path=R/'source'/f'{name}.blend';backup=path.with_name(path.stem+'-before-gold-leaf.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();apply_sanctuary_finishes();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'));images=[n.image for n in gold.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==3 and all(i.packed_file and tuple(i.size)==(1024,1024) for i in images)
 p=next(m for m in used if m.name.startswith('Sanctuary | oxblood lacquer')).node_tree.nodes.get('Principled BSDF');assert abs(p.inputs['Coat Weight'].default_value-.45)<1e-5
 reports.append({'file':str(path),'allGeometryAndTransformsPreserved':True,'objects':before[0],'goldMapsPacked':3})
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
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
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['finishRevision']=1;p.write_text(json.dumps(meta,indent=2))
(R/'evidence/sanctuary-finishes-native.json').write_text(json.dumps(reports,indent=2));print('FINISH VERIFICATION',reports,flush=True)
